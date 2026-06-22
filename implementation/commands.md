# Commands

> 这份文件把 implementation bridge 封装成少量、好记、可自动化的命令。  
> 这里定义的是 `uv run plb stage implementation ...` 的局部命令，不是全局入口。  
> 全局 CLI、状态库和发布规则见 `../cli-architecture.md` 与 `../workflow-state.md`。

## 1. Design Goals

- 少命令
- 命令语义稳定
- 自然语言和 CLI 同构
- 每个命令都有明确输入、输出和回退点
- 每个 goal 完成后自动回归前序能力
- goal registry 会根据 goal 文本的并列语义和层级语义自动扩展，不固定死在演示步骤

## 1.1 Command Contract

所有命令都应遵守同一输出形状：

```json
{
  "command": "",
  "status": "",
  "summary": "",
  "stage": "implementation",
  "goal_progress": {
    "total_goals": 0,
    "completed_goals": 0,
    "current_goal": "",
    "next_goal": ""
  },
  "rollback_point": "",
  "next_action": "",
  "evidence": [],
  "artifacts": [],
  "warnings": []
}
```

状态值建议统一为：

- `ok`
- `blocked`
- `needs_revision`
- `no_go`
- `dry_run`

所有命令都必须写回或只读同一个 `run-state`，不得各自维护私有状态。

## 2. Command Set

### 2.1 `uv run plb stage implementation plan`

用途：

- 冻结 `goal`
- 拆分 `goal registry`
- 生成 implementation plan
- 初始化回归范围

自然语言别名：

- “帮我开始 implementation”
- “把这个 goal 拆成执行计划”
- “生成 implementation 计划”

输入：

- `Codex goal`
- `quality-gates validation report`
- 上游蓝图产物

参数：

- `--project <project_key>`: 目标项目
- `--goal <goal_text>`: 本次要拆解的自然语言 goal
- `--dry-run`: 只生成计划，不写入状态
- `--output <path>`: 可选，导出 plan JSON
- `--fresh-reviewer <true|false>`: 强制后续审查使用隔离 reviewer

输出：

- `implementation plan`
- `goal registry`
- `code scaffold map`
- `directory tree`
- `bootstrap manifest`
- `task batch list`
- `verification plan`
- `implementation handoff report`

状态变化：

- 若通过并非 `--dry-run`，创建或更新 `stage_run`
- 记录 `goal_registry`
- 初始化 `goal_progress.total_goals`
- 将当前执行指针设为第一个 goal
- 初始化回归集合

失败时回退：

- `analysis` 或最近的上游已验证层

### 2.2 `uv run plb stage implementation status`

用途：

- 查看当前实现进度
- 查看总共拆了多少个 goal
- 查看当前 goal、已完成 goal、下一 goal
- 查看每个 goal 的回归状态

自然语言别名：

- “现在做到哪了”
- “我们还有几个 goal”
- “当前进度”

输入：

- 当前 `run-state`

参数：

- `--project <project_key>`
- `--json`: 以 JSON 输出
- `--verbose`: 显示每个 goal 的详细状态

输出：

- `goal_progress`
- `goal_registry`
- `latest_verification`
- `rollback_point`

状态变化：

- 无

失败时回退：

- 无需修改状态，只读返回

### 2.3 `uv run plb stage implementation next`

用途：

- 执行下一个 goal
- 自动应用当前 goal 的任务批次
- 自动跑前序能力回归
- 通过后推进进度

自然语言别名：

- “继续下一个 goal”
- “帮我推进 implementation”
- “执行下一步并回归”

输入：

- 当前 `run-state`
- 已冻结的 `goal registry`
- 当前任务批次

参数：

- `--project <project_key>`
- `--goal-id <goal_id>`: 指定要执行的 goal，默认当前 goal
- `--regress`: 强制在推进前先跑回归
- `--dry-run`: 只模拟推进，不写状态
- `--output <path>`: 导出执行结果

输出：

- `goal execution result`
- `regression result`
- 更新后的 `goal_progress`
- 更新后的 `run-state`

状态变化：

- 当前 goal 标记为完成或失败
- 若完成则推进到下一 goal
- 每个完成的 goal 都触发前序回归集合
- 回归失败时，将当前 goal 标记为 `blocked`，并停止推进

失败时回退：

- 当前 goal 的 `rollback_point`

### 2.4 `uv run plb stage implementation verify`

用途：

- 只做验证，不推进执行
- 检查是否可以进入真实编码
- 检查 goal registry、回归、验证和回退点是否齐全

自然语言别名：

- “检查能不能进入真实编码”
- “验证一下现在是否可交付”
- “做一次 implementation 审核”

输入：

- 当前 `run-state`
- `implementation plan`
- `verification plan`

参数：

- `--project <project_key>`
- `--strict`: 任何缺失都直接判 `no_go`
- `--json`: 以 JSON 输出
- `--output <path>`: 导出验证结果

输出：

- `go / no-go`
- `verification summary`
- `gaps`
- `rollback_point`

状态变化：

- 默认无
- 若 `--strict` 且发现阻塞项，只返回 `no_go`

失败时回退：

- 不修改状态，只报告最近可回退点

## 3. Shared Runtime State

所有命令都读写同一个运行态文件，建议名称：

- `.project-launch-blueprint/state.db`

如果需要导出可读快照，可额外生成：

- `./project-launch-blueprint-run-state.json`

建议数据库实体：

- project
- stage_run
- goal_registry
- goal_progress
- regression_check
- command_log
- audit_event

建议快照字段：

```json
{
  "goal": "",
  "scope": "",
  "goal_registry": [],
  "goal_progress": {
    "total_goals": 0,
    "completed_goals": 0,
    "current_goal": "",
    "next_goal": ""
  },
  "latest_verification": {},
  "regression_checks": [],
  "rollback_point": "",
  "last_command": "",
  "updated_at": ""
}
```

## 4. Command Flow

### 4.1 Plan Flow

1. 读取 `goal`
2. 冻结 `scope`
3. 拆 `goal_registry`
4. 生成计划
5. 写入 `stage_run`
6. 创建 JSON 快照（可选）

### 4.2 Status Flow

1. 读取 `stage_run`
2. 汇总 `goal_progress`
3. 展示当前 goal 与下一 goal
4. 展示最近一次回归结果

### 4.3 Next Flow

1. 读取当前 goal
2. 执行当前 goal 的任务批次
3. 跑该 goal 触发的回归集合
4. 若通过，推进到下一 goal
5. 若失败，停在当前 rollback point
6. 记录命令日志与审查证据

### 4.4 Verify Flow

1. 读取当前状态
2. 检查 goal registry 是否完整
3. 检查回归是否定义
4. 检查回退点是否明确
5. 检查是否需要 fresh reviewer
6. 输出 go / no-go

## 5. Output Contract

每个命令都应返回一个结构化结果，至少包含：

- `command`
- `status`
- `summary`
- `goal_progress`
- `rollback_point`
- `next_action`
- `evidence`

如果命令执行涉及 LLM 校验，还应附带：

- `review_packet_path`
- `reviewer_kind`
- `review_state`

## 6. UX Rules

- 用户不需要知道内部步骤名
- 用户只需要知道当前 goal 总数、当前进度和下一步
- 用户不能手工跳过回归
- 用户不能在 verify 失败时继续 next
- 用户看到的状态必须和 run-state 一致
- 用户可以通过 `--json` 拿到机器可读结果

## 7. Natural Language Routing

自然语言输入先归类到以下意图之一：

- `plan`
- `status`
- `next`
- `verify`

如果一句话包含多个意图，优先级如下：

1. `verify`
2. `next`
3. `plan`
4. `status`

如果自然语言无法映射到单一意图，则返回 `blocked`，要求用户重述。

## 8. Examples

### 8.1 Plan

输入：

```txt
帮我把这个 goal 拆成 implementation 计划
```

等价命令：

```txt
uv run plb stage implementation plan
```

可选参数：

- `--project crm-web`
- `--goal "帮我开始 implementation"`
- `--dry-run`

### 8.2 Status

输入：

```txt
现在我们拆了几个 goal？
```

等价命令：

```txt
uv run plb stage implementation status
```

### 8.3 Next

输入：

```txt
继续下一个 goal，并先跑回归
```

等价命令：

```txt
uv run plb stage implementation next
```

### 8.4 Verify

输入：

```txt
检查现在能不能进入真实编码
```

等价命令：

```txt
uv run plb stage implementation verify
```
