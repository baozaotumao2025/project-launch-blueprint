# CLI Architecture

> 这份文档重新定义 `project-launch-blueprint` 的命令层。  
> 目标是让整套蓝图可以通过 `uv` 管理、通过命令推进、通过状态机记录，并且把 LLM 校验隔离到 fresh subagent 中执行。

## 1. Design Goals

- `uv` 是唯一推荐的运行和发布入口
- `project-launch-blueprint/` 是模板和技能包的根路径
- CLI 负责推进状态，不负责重新定义业务语义
- 每个阶段都必须先验证再进入下一阶段
- 每个阶段的 LLM 校验都必须用隔离上下文执行
- `analysis/` 只承载原始素材，不承载 CLI 生成的派生结果
- 派生结果和工作副本放入 `.project-launch-blueprint/projections/`
- 状态库是权威层，派生投影只是可重建视图

## 2. Runtime Model

### 2.1 Canonical State

每个目标项目都必须有一个本地运行态目录，建议命名为：

```text
.project-launch-blueprint/
  state.db
  logs/
  audits/
  exports/
  backups/
```

其中：

- `state.db` 记录项目、阶段、revision、review、transition 和 audit
- `logs/` 记录命令执行日志
- `audits/` 记录 LLM 审查 packet 和审查结果
- `exports/` 存放导出的 manifest、report 和模板包
- `backups/` 用于回退和恢复

### 2.2 Source vs Projection

`analysis/` 目录只放原始素材，不放 CLI 生成的派生结果。

- 人可以改原始 Markdown
- 命令如果要生成派生稿，必须写到 `.project-launch-blueprint/projections/`
- 状态库始终是 gate 判断的真相
- 如果原始素材和状态库不一致，必须先收敛差异，再继续后续阶段

### 2.3 Revision Rules

- 所有阶段产物都按 revision 管理
- 新 revision 先进入 `draft`
- 结构检查通过后进入 `structurally_valid`
- LLM 审查通过后进入 `semantic_review`
- `record` 会把 worker verdict 归一为 `passed` / `needs_revision` / `failed`
- `approve` / `reject` 只能基于 worker verdict 终态落库，不能覆盖审查结果
- verdict 为 `passed` 时才可进入 `approved`
- 上游 revision 变化后，下游已批准 revision 自动变 `stale`
- 回退不是改写旧 revision，而是创建新 revision

## 3. Command Tree

`command-reference.md` 是本节命令树的可实现清单。  
这里保留的是命令层级、状态模型和约束原则。

### 3.1 Project Commands

```txt
uv run plb init
uv run plb status
uv run plb publish
```

- `init`：初始化状态库、目录和模板骨架
- `status`：展示当前阶段、revision 状态、阻塞原因和下一步
- `publish`：把当前模板包或阶段成果打包发布

### 3.2 Stage Commands

```txt
uv run plb stage discovery plan
uv run plb stage discovery next
uv run plb stage discovery verify
uv run plb stage discovery status
uv run plb stage discovery set
```

所有阶段都遵守同一命令模式：

- `plan`：冻结本阶段输入范围，生成目标和回归边界
- `next`：执行本阶段生成与验证，并在通过后推进状态
- `verify`：只做验证，不推进状态
- `status`：只读查看当前 revision、门禁和回退点
- `set`：手动写入状态，用于推进、阻塞或回退

阶段顺序固定为：

1. `discovery`
2. `domain`
3. `state`
4. `api`
5. `design`
6. `slice`
7. `gates`
8. `implementation`

### 3.3 Review Commands

```txt
uv run plb review packet
uv run plb review run
uv run plb review record
uv run plb review approve
uv run plb review reject
```

- `packet`：生成只读审查包
- `run`：把 packet 交给 fresh subagent 做隔离审查
- `record`：把 worker verdict 写回状态库并归一化为最终 review state
- `approve` / `reject`：最终审批入口，但只按 worker verdict 终态落库，不允许手工覆盖

## 4. Initialization Flow

`init` 必须完成以下动作：

1. 验证当前目录就是模板根路径或目标项目根路径
2. 创建本地运行态目录
3. 初始化状态库
4. 记录项目 metadata
5. 创建或确认 `.project-launch-blueprint/projections/` 投影目录
6. 建立空的 stage registry
7. 建立 revision history 和 audit trail
8. 生成首个 `project state`

`init` 之后，项目不能直接进入实现阶段，必须先完成前面所有设计阶段的门禁。

## 5. Stage Progression

每个阶段都遵守同一条推进链：

1. `plan`
2. `generate`
3. `structural validate`
4. `LLM review packet`
5. `fresh subagent review`
6. `record result`
7. `approve` or `reject` based on worker verdict
8. `mark downstream stale` if upstream changed

阶段之间的约束关系：

- `domain` 只能消费已批准的 `discovery`
- `state` 只能消费已批准的 `discovery + domain`
- `api` 只能消费已批准的 `discovery + domain + state`
- `design` 只能消费已批准的 `api`
- `slice` 只能消费已批准的 `api + design + state`
- `gates` 只能消费前面全部已批准输出
- `implementation` 只能消费 `quality-gates` 已批准输出

## 6. LLM Isolation Policy

所有校验都默认使用 packet 驱动的 fresh reviewer。

### 6.1 Isolation Requirements

- review packet 只包含当前阶段和已批准上游材料
- 审查上下文不得继承生成上下文
- 审查必须在只读模式运行
- 审查 worker 必须对 packet 结构、上游输入、回退点和反例提示做规则校验
- 审查结果必须记录 evidence、counterexample 和 rollback point
- 审查失败不能静默忽略，必须标记为 `needs_revision` 或 `rejected`

### 6.2 Subagent Rule

在支持 sub-agent 的 Codex 环境中，校验命令必须等价于：

- 新建一个 fresh reviewer sub-agent
- `fork_context: false`
- 只读 packet
- 不访问生成阶段的私有上下文

如果输出缺少反例、证据或回退点，不得通过。

## 7. Natural Language Routing

自然语言输入只映射到少量意图：

- `init`
- `status`
- `plan`
- `next`
- `verify`
- `review`
- `publish`

例子：

- “帮我初始化这个蓝图” -> `init`
- “现在到哪一步了” -> `status`
- “开始 discovery” -> `stage discovery plan`
- “继续下一步并先做回归” -> `stage <current> next`
- “先检查能不能进入下一阶段” -> `stage <current> verify`
- “把审查包发给隔离 reviewer” -> `review run`
- “把模板包发布出去” -> `publish`

## 8. Publish Model

`publish` 的职责是把当前模板、命令规范和阶段规范打包成可分发 skill bundle。

发布产物至少包括：

- `README.md`
- `index.md`
- `command-reference.md`
- `template-spec.md`
- `cli-architecture.md`
- `workflow-state.md`
- `discovery/`
- `domain-model/`
- `state-machine/`
- `api-contract/`
- `design-system/`
- `vertical-slice/`
- `quality-gates/`
- `implementation/`

## 9. Design Note

这套 CLI 的目标不是把命令做多，而是把状态推进做稳。

- 命令少
- 状态真
- 校验隔离
- 回退明确
- 上游变化会自动让下游失效
