# Discovery Implementation Tutorial

> 目标：把当前 discovery 阶段的实现拆开讲清楚，帮助后来者理解“为什么 discovery 不能自动生成输入、为什么 review 必须走 subagent、为什么 init 会物化文档、为什么 stage 状态必须落库”。

## 1. Discovery 在整条流水线里的位置

`discovery` 是整条 stage 流的第一阶段，也是最容易被误用的阶段。

它的作用不是直接产出代码，而是把用户已经准备好的分析材料，整理成后续阶段可以稳定消费的输入边界。

在当前实现里，discovery 的责任主要有四个：

- 接收用户准备好的 `analysis/` 输入
- 冻结当前 stage 的目标、回退点和审查包
- 把 review 交给独立 worker 或 subagent
- 把生命周期和审查状态持久化到数据库和审计记录里

这意味着 discovery 不是“写一段 prompt 就结束”，而是一个完整的、可恢复的业务阶段。

## 2. 为什么 discovery 不能自动生成输入

这一步最重要的约束是：`analysis` 目录里的关键文件必须由用户自己准备，不能由 LLM 或 IDE 助手补造。

当前实现要求至少存在这些输入：

- `analysis/brief.md`
- `analysis/story-maps/*.md`
- `analysis/pages/*.md`
- `analysis/features/index.md`
- `analysis/gwt/*.feature`
- `analysis/relations/*.md`

除此之外，系统还会在 `analysis/` 下做一次文件级 inventory，把所有文件逐个列出来，并生成一份逐文件覆盖模板。这样后续生成和审查就不是笼统地说“看过 analysis”，而是可以检查“每个文件都已经对账，或者被显式排除”。
如果你要看这条规则最后落在哪里，答案不是 prompt，而是：

- `analysis_inventory` 和 `analysis_coverage_template` 在代码里生成
- review packet 把它们一起冻结
- worker 逐条检查 inventory 和 coverage 是否一致
- validation report 把 `unmapped_files` 明确暴露出来

原因很直接：

- discovery 的输入本身就是业务分析结果，不是可推导的模板
- 如果让模型代写这些文件，后续阶段会建立在伪输入上
- 伪输入会让 `domain`、`state`、`api` 之后的所有产物失真
- 如果不做文件级 inventory，就无法证明有没有遗漏某个 `analysis` 文件
- 如果 coverage matrix 里少了一行，worker 会直接把 review 判回修订

所以当前实现采用的是“closed world”策略：

- 输入存在，继续
- 输入缺失，直接阻断并告诉用户自己准备

对应代码在：

- [`src/plb/workflow/prompting.py`](../../src/plb/workflow/prompting.py)
- [`src/plb/commands/stage.py`](../../src/plb/commands/stage.py)
- [`src/plb/commands/review.py`](../../src/plb/commands/review.py)
- [`src/plb/review/worker.py`](../../src/plb/review/worker.py)

## 3. 初始化时为什么要物化文档

用户在目标项目里执行 `uv run plb init` 后，初始化不会生成业务代码，但会把项目级的最小发行包写入：

- `records/project-launch-blueprint/`
- `records/project-launch-blueprint/adr/`

这样做的目的不是“复制仓库”，而是让项目本地拥有一份可追踪、可审阅、可继续推进的操作契约。

这样 discovery 在后续执行时就可以优先读取项目本地文档，而不是依赖安装目录里的 skill 本体。

这个设计有几个好处：

- 文档和项目状态在同一个项目空间里
- 后续 review 能看到项目本地的 stage 资料
- 用户可以把这份文档连同项目一起提交、传阅、复盘

实现入口在：

- [`src/plb/commands/root.py`](../../src/plb/commands/root.py)
- [`src/plb/workflow/materialize.py`](../../src/plb/workflow/materialize.py)

## 4. Discovery 的 stage 生命周期是怎么记录的

这个阶段不是只写一个 status，而是记录一整条生命周期链。

初始化时，每个 stage 都会被种下初始生命周期记录。之后 discovery 继续推进时，会不断追加：

- `planned`
- `packet_created`
- `review_running`
- `review_recorded`
- `approved`
- `rejected`
- `blocked`

这样做的原因是：

- 业务中断时可以恢复
- 状态异常时可以审计
- 后续阶段可以判断前置条件是否真的完成

从实现上看，生命周期记录和 stage 状态是分开的：

- `stage status` 表示当前业务阶段处于什么状态
- `lifecycle record` 表示这个状态是怎么来的、健康度如何、上一步发生了什么

这部分能力主要分布在：

- [`src/plb/state/store.py`](../../src/plb/state/store.py)
- [`src/plb/commands/stage.py`](../../src/plb/commands/stage.py)
- [`src/plb/commands/review.py`](../../src/plb/commands/review.py)

## 5. 为什么 review 必须走 subagent

你的要求里最关键的一条是：审查必须走独立 subagent，不能在当前上下文里直接审查。

这个要求在当前实现里被具体化成两层约束：

1. review packet 创建时就显式声明 `execution_policy: isolated_subagent`
2. review run 使用独立 worker / filesystem review runner 执行，不复用调用方上下文

这件事非常重要，因为它解决的是“上下文污染”问题。

如果 review 直接在主会话里做，会出现这些风险：

- 生成上下文污染审查结论
- 审查结论和用户指令混在一起
- 后续命令误以为已经完成独立审查

当前实现里，review 的输入会被组装成一个冻结包，再交给 worker：

- packet 里有 stage、payload、rollback point、approved inputs
- packet 里还会嵌入 prompt bundle
- worker 只看这份冻结包，不看主上下文的聊天历史

对应实现位于：

- [`src/plb/commands/review.py`](../../src/plb/commands/review.py)
- [`src/plb/review/worker.py`](../../src/plb/review/worker.py)
- [`src/plb/workflow/prompting.py`](../../src/plb/workflow/prompting.py)

## 6. Prompt bundle 是怎么统一的

当前 discovery 不再依赖散落在各处的 prompt 片段，而是统一通过 `StagePromptBundle` 汇总：

- `method.md`
- `validation-rules.md`
- `output-schema.md`
- `prompt-templates.md`
- `example-output.md`
- `checklist.md`

这意味着生成、验证、审查三类动作都能从同一个 stage 文档源头取材料。

`StagePromptBundle` 的价值在于：

- 统一输入格式
- 统一 stage 目录选择逻辑
- 统一给 worker 的 prompt 结构
- 让 CLI 和自然语言路由都走同一条链路

你可以把它理解成“stage 的装配层”。

对应实现位于：

- [`src/plb/workflow/prompting.py`](../../src/plb/workflow/prompting.py)

## 7. CLI 和自然语言为什么会走同一条实现链

当前设计要求 `uv run plb stage ...`、`uv run plb review ...` 和 `uv run plb route "<text>"` 最终都落到相同的 workflow 函数上。

这里的原则是：

- 入口可以不同
- 业务路径不能不同

所以自然语言入口只负责“识别意图”，不会自己重新实现 discovery。

例如：

- “开始 discovery” -> `plan_stage("discovery", ...)`
- “生成 discovery 审查包” -> `packet_review("discovery", ...)`
- “推进 discovery” -> `next_step("discovery", ...)`

对应实现位于：

- [`src/plb/commands/routing.py`](../../src/plb/commands/routing.py)
- [`src/plb/bootstrap.py`](../../src/plb/bootstrap.py)
- [`src/plb/cli.py`](../../src/plb/cli.py)

## 8. Discovery 的执行顺序应该怎么理解

如果只看用户视角，discovery 的完整节奏可以概括成：

1. 初始化项目
2. 准备 `analysis/` 输入
3. `plan discovery`
4. `review packet discovery`
5. `review run discovery`
6. `review record discovery`
7. `approve discovery` 或 `reject discovery`
8. `next discovery`

但在实现层，真正发生的是：

- `plan` 会先验证输入存在，然后把 stage 标成 active，并写 lifecycle
- `packet` 会冻结输入、写审查包、记录 packet_created
- `run` 会把冻结包交给独立 worker，记录 review_running
- `record` / `approve` / `reject` 会把 worker verdict 落库并改变 stage 状态
- `next` 会检查前置条件，只有 review 通过且前置阶段完成时才允许推进

这就是为什么这套实现不是“一个命令完成所有事”，而是故意拆成多个可审计步骤。

## 9. 代码里对应的关键文件

想理解 discovery 的实现，建议按这个顺序读：

1. [`src/plb/core/models.py`](../../src/plb/core/models.py)
2. [`src/plb/core/paths.py`](../../src/plb/core/paths.py)
3. [`src/plb/state/store.py`](../../src/plb/state/store.py)
4. [`src/plb/workflow/materialize.py`](../../src/plb/workflow/materialize.py)
5. [`src/plb/workflow/prompting.py`](../../src/plb/workflow/prompting.py)
6. [`src/plb/commands/root.py`](../../src/plb/commands/root.py)
7. [`src/plb/commands/stage.py`](../../src/plb/commands/stage.py)
8. [`src/plb/commands/review.py`](../../src/plb/commands/review.py)
9. [`src/plb/commands/routing.py`](../../src/plb/commands/routing.py)
10. [`src/plb/review/worker.py`](../../src/plb/review/worker.py)

这个顺序的逻辑是：

- 先看数据模型
- 再看路径和存储
- 再看初始化如何物化
- 再看 prompt 怎么统一
- 最后看命令入口如何拼起来

## 10. 相关测试在验证什么

为了防止 discovery 只是“文档上说得好看”，当前实现配了几类测试。

### 10.1 输入预检测试

验证 discovery 在缺少 `analysis/` 输入时会直接阻断。

### 10.2 Prompt 编排测试

验证 `StagePromptBundle` 会把 stage 方法论文件、模板、schema 和 checklist 装配起来。

### 10.3 生命周期测试

验证 discovery 的计划、审查、落库和推进会留下可恢复的状态痕迹。

### 10.4 初始化测试

验证 `init` 会把项目文档和 ADR 物化到项目目录，而不会污染业务源码树。

相关测试文件包括：

- [`tests/test_discovery_inputs.py`](../../tests/test_discovery_inputs.py)
- [`tests/test_prompt_orchestration.py`](../../tests/test_prompt_orchestration.py)
- [`tests/test_discovery_lifecycle.py`](../../tests/test_discovery_lifecycle.py)
- [`tests/test_bootstrap_cli.py`](../../tests/test_bootstrap_cli.py)
- [`tests/test_user_manual.py`](../../tests/test_user_manual.py)

## 11. 常见误区

### 11.1 以为 discovery 可以自动补输入

不可以。缺失输入应该提示用户准备，而不是让模型代写。

### 11.2 以为 review 可以直接在当前会话完成

不可以。review 必须走独立 worker / subagent。

### 11.3 以为 init 会顺手生成业务代码

不可以。init 只负责准备项目运行态和最小发行包。

### 11.4 以为 stage status 就够了

不够。stage status 只能看当前状态，真正排障还要看 lifecycle record 和 review 记录。

## 12. 如果你要继续扩展到其他 stage

后续推广到 `domain`、`state`、`api`、`design`、`slice`、`gates` 时，建议复用同一套模式：

- 先定义 stage 目录里的方法论文件
- 再把 prompt bundle 接到统一编排层
- 再把输入预检和生命周期写进 state store
- 再让 review 固定走 subagent
- 最后补齐正向和负向测试

这样每一层都能保持一致的工程节奏，而不会出现某个 stage 走捷径、另一个 stage 走完整流程的情况。
