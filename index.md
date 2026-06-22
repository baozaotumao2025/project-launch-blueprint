# Project Launch Blueprint

> 项目启动蓝图的方法论总览。
> 这里说明从原始 `analysis/` 到工业可用前端项目的 8 个蓝图阶段（7 个生成层 + 1 个质量门禁层），以及质量门禁之后如何进入实现桥接和发布。
> 这里也定义这套模板的 CLI、状态机和发布约束，确保 `project-launch-blueprint/` 可以作为可分发 skill 模板使用。
> 本目录下的所有路径与链接默认都以 `project-launch-blueprint/` 为根，只使用相对路径。
>
> 如果你第一次接触这套方法论，先读 `README.md`。
>
> 这套蓝图遵循三条硬原则：
> - 先验证，再抽象。任何阶段都只能在已验证输入上继续加工。
> - 主输入优先，辅助证据只用于核验、补漏和反例攻击。
> - 每层只做一件事。上游负责定义事实，下游负责翻译，不允许跨层重建。

## 1. Flow

`analysis -> discovery -> domain model -> state machine -> api contract -> design system -> vertical slice -> quality gates -> implementation bridge -> publish`

## 1.1 CLI and State

- CLI 通过 `uv` 运行，命令层只推进状态，不重新定义语义
- 状态库是权威真相，`analysis/` 只是原始输入层，派生投影放在 `.project-launch-blueprint/projections/`
- 每个阶段都必须经过结构校验、隔离 LLM 校验和显式批准
- 上游 revision 变化会让下游已批准产物变 `stale`
- `implementation` 只能在 `quality gates` 已批准后进入
- `publish` 负责把模板和规范作为 skill bundle 分发出去

## 1.2 Project Space

用户项目里至少要分出两类落点：

- `project space`：正式代码、阶段产物、测试、配置、必要状态记录和可追踪的中间产物
- `temporary execution space`：纯本机缓存、敏感信息和可完全重建的噪音文件

`implementation` 的输出必须落到 `project space` 里，并且其过程产物也应该默认保留为项目历史的一部分。

## 1.3 Reuse Strategy

这套蓝图不是只给当前项目用的。为了让未来新项目可以直接复制整套方法论，我们把它拆成两层：

- `project-launch-blueprint/` 负责定义本项目的完整方法链和阶段顺序。
- `template-spec.md` 负责定义这套方法链在新项目里如何被复制、裁剪和重新命名。

这意味着：
- 蓝图本体回答“怎么做”
- 模板规范回答“怎么复制”

## 1.4 Quick Entry

- `README.md` 适合第一次打开的人，先给最短路径。
- `index.md` 适合想看完整结构的人，先给方法论总览。
- `cli-architecture.md` 适合想看命令、状态和发布的人，先给操作入口。
- `workflow-state.md` 适合想看权威状态模型的人，先给状态真相。
- `command-reference.md` 适合想看完整命令表的人，先给可实现的入口清单。
- `template-spec.md` 适合要复制到新项目的人，先给复制规则。

## 2. Design Principles

### 2.1 Method Contract

- 每一层都必须有明确的 `Inputs`、`Output`、`Workflow`、`Validation` 和 `Rollback` 语义。
- 每一层都必须能被正向测试和负向测试同时验证。
- 每一层输出都必须能追溯回上一层或辅助证据，不能只凭推断成立。
- 每一层都必须声明哪些内容属于主输入，哪些内容只允许作为辅助证据。
- 每一层都必须有可执行的回退点，避免模型一旦出错就无法收敛。

### 2.2 Layering Logic

- 先做 `discovery`，因为没有稳定能力，后面的边界、状态和契约都会建立在流沙上。
- 再做 `domain model`，因为能力只有进入边界和对象责任，才会变成可演化的业务模型。
- 再做 `state machine`，因为流程阶段和转移必须在契约之前被显式化，否则接口会偷跑业务决策。
- 再做 `api contract`，因为外部交换语义必须以已验证的能力、边界和状态为依据，不能反向塑形上游模型。
- 再做 `design system`，因为 UI 的 token、组件和状态样式应当服务于已验证契约，而不是提前把页面审美当成体系。
- 再做 `vertical slice`，因为只有在前面语义稳定之后，切片实现才不会把局部实现误写成方法论。
- 最后做 `quality gates`，因为门禁的职责是拦截回归和幻觉，不是替代前面的建模工作。

### 2.3 Validation Philosophy

- 正向验证的作用是确认抽象不是空话。
- 负向验证的作用是确认抽象没有被页面、按钮、接口、表单、技术结构或审美偏好污染。
- 反例攻击不是附加项，而是每一层必须内建的证明机制。
- 如果一个阶段不能明确说出回退点，那它还不是一个可交付阶段。

## 3. Stages

### 2.1 业务能力地图

- 作用：从 `analysis` 里归并出稳定的业务能力
- 来源：`brief`、`story maps`、`pages`、`features`、`gwt`、`relations`
- 方法：见 `discovery/`
- 输出：能力地图和验证报告
- 为什么先做：先把原始材料压缩成可验证的能力事实，后续阶段才有稳定主输入。

### 2.2 领域模型

- 作用：把已验证的能力收敛成稳定的业务边界、对象和聚合
- 生成方式：基于通过验证的 capability map 提炼 bounded context 和 aggregate
- 输出：领域对象、边界、关系
- 为什么接在 discovery 后：能力稳定了，才能判断哪些能力属于同一语言体系和一致边界。

### 2.3 状态机

- 作用：把关键流程的阶段变化、事件和守卫显式化
- 生成方式：基于 `discovery capability map`、`domain model map`、story maps、features 和 gwt 提炼
- 输出：`state machine map`、状态、事件、守卫、转移、终态
- 为什么在 contract 前：流程阶段必须先明确，接口才不会绕过业务状态直接暴露结果。

### 2.4 API 契约

- 作用：定义数据如何在页面、服务和后端之间流动
- 生成方式：基于 `discovery capability map`、`domain model map`、`state machine map` 和辅助证据生成
- 输出：`api contract map`、接口、请求、响应、错误、鉴权、幂等
- 为什么在 design system 前：先冻结外部交换语义，再让 UI 组件围绕这些语义做统一表达。

### 2.5 设计系统

- 作用：把 API 契约翻译成可复用的视觉、交互和组件语言
- 生成方式：基于 `api contract map`、`api-contract validation report` 和辅助证据，抽取跨切片共性 UI 规则和组件模式
- 输出：token、组件、状态样式、布局规则、无障碍规则、响应式规则
- 为什么在 vertical slice 前：设计系统先统一，再让具体页面实现复用，而不是每个切片重新发明样式。

### 2.6 垂直切片实现

- 作用：按能力完整打通页面、状态、接口、mock 和业务逻辑
- 生成方式：基于 contract 和 schema 按功能切片实现
- 输出：页面、hook、service、repository、mock、UI
- 为什么在 quality gates 前：实现要先出现，再由门禁验证能否发布。
- 方法：见 `vertical-slice/`

### 2.6.1 垂直切片的方法论

- 垂直切片采用 `single capability end-to-end` 的方法论，也就是一条业务能力从入口到结果只走一条完整路径。
- 垂直切片采用 `contract-first` 方法论，页面和逻辑必须以已验证的 API 契约为边界，不能自己发明数据结构。
- 垂直切片采用 `design-system driven implementation` 方法论，页面必须消费已验证的组件、状态样式和交互规则，不能绕开设计系统另起炉灶。
- 垂直切片采用 `state-machine aligned flow` 方法论，页面状态、错误态、成功态和重试态必须和上游状态机一致，不能跳过阶段。
- 垂直切片采用 `boundary-separated architecture` 方法论，`page / hook / service / repository / mock` 各自只做一件事。
- 垂直切片采用 `validation-gated delivery` 方法论，只有通过正向测试、负向测试和反例攻击的切片才允许进入质量门禁。

#### 为什么这样做

- 如果不按单能力切片，页面就会退化成功能拼盘，后续无法稳定复用。
- 如果不以契约为边界，页面会重新发明请求结构和错误语义，和上游脱节。
- 如果不以设计系统为约束，页面会在切片里重写视觉语言，导致局部最优和全局失控。
- 如果不以状态机为约束，页面会绕过业务阶段直接展示最终结果，破坏可解释性。
- 如果不把职责拆到 `page / hook / service / repository / mock`，所有逻辑都会糊在一起，无法测试也无法替换。
- 如果没有验证门禁，所谓“切片完成”只会变成“能看见”，而不是“能交付”。

### 2.7 质量门禁

- 作用：保证每个阶段都可验证、可回退、可发布
- 生成方式：为每个阶段定义验证规则和测试标准
- 输出：校验项、测试项、发布门槛
- 为什么放最后：门禁负责确认前面所有阶段没有走偏，而不是替代这些阶段。
- 方法：见 `quality-gates/`

### 2.7.1 质量门禁的方法论

- 质量门禁采用 `risk-based release gating` 方法论，也就是把最容易出错、影响最大的地方放在最严格的门槛里。
- 质量门禁采用 `test pyramid` 方法论，单元、集成、端到端测试各自承担不同责任，不把所有风险都塞进一种测试。
- 质量门禁采用 `continuous delivery gates` 方法论，只有通过自动化校验的构件才进入可发布状态。
- 质量门禁采用 `observability-first` 方法论，日志、指标、追踪和错误信号必须足够明确，才能证明能回滚、能定位、能恢复。
- 质量门禁采用 `rollback-aware release management` 方法论，任何发布前都要明确失败后的回退方案。
- 质量门禁采用 `shift-left quality engineering` 方法论，把质量问题尽量前置到构建和验证阶段，而不是等到上线后才发现。

#### 为什么这样做

- 如果没有风险分层，门禁会变成形式化清单，重要风险反而漏掉。
- 如果没有测试金字塔，所有压力都会堆到端到端测试，慢且脆弱。
- 如果没有连续交付门槛，所谓“可发布”只是人工感觉，不是可验证状态。
- 如果没有可观测性，问题出现后只能猜，没法定位、回滚和恢复。
- 如果没有回退意识，发布门禁就无法真正保护用户和系统。
- 如果不把质量前置，问题就会被拖到更晚，修复成本更高。

## 2.8 实现桥接

- 作用：把已经通过验证的蓝图产物翻译成真实代码、目录、任务和提交计划
- 生成方式：基于 `quality-gates validation report` 和上游全部已验证产物，映射到仓库结构和实现顺序
- 输出：implementation plan、code scaffold map、task batch list、branch / commit plan、verification plan
- 为什么单独放出来：因为它不是新的业务建模阶段，而是把前面所有阶段变成代码的工程桥接层
- 方法：见 `implementation/`

### 2.8.1 实现桥接的方法论

- 实现桥接采用 `specification-driven implementation` 方法论，也就是先把已验证规范翻译成代码任务，而不是直接凭感觉写实现。
- 实现桥接采用 `artifact-to-code mapping` 方法论，也就是每个蓝图产物都要找到明确的代码落点，不能悬空。
- 实现桥接采用 `scaffold-first` 方法论，也就是先生成目录、文件和骨架，再填行为。
- 实现桥接采用 `slice-first delivery` 方法论，也就是先完成一个能力的完整闭环，再复制到其他能力。
- 实现桥接采用 `test-backed handoff` 方法论，也就是每个实现动作都要有对应验证，不允许只看“能跑”。

#### 为什么这样做

- 如果不先冻结范围，代码会反向重写业务语义。
- 如果不先做 artifact 映射，目录和文件会变成随手起名。
- 如果不先 scaffold，后续实现会失去边界。
- 如果不按切片交付，代码会重新退化成横向层次堆叠。
- 如果没有测试背书，所谓“完成”只是暂时看起来能用。

## 4. Reading Order

1. 先读本页
2. 再读 `discovery/`
3. 再按阶段推进到 `quality-gates/`
4. 再读 `cli-architecture.md`
5. 再读 `workflow-state.md`
6. 再读 `command-reference.md`
7. 如果要进入真实编码，再读 `implementation/`

## 5. Why This Order

- 先定业务能力，再定边界
- 先定边界，再定状态
- 先定状态，再定契约
- 先定契约，再定 UI 体系
- 先切片实现，再加质量门禁

## 6. Template Spec

- 如果要创建一个新项目，优先复制 `template-spec.md` 规定的目录结构和方法论契约。
- 如果要为某个行业或团队做定制，只能改“输入来源”和“输出命名”，不能破坏层级顺序和验证规则。
- 如果某一层不适用，可以裁掉该层，但不能打乱上游到下游的依赖关系。
- 如果新增一层，必须同时补 `index.md`、`method.md`、`validation-rules.md`、`output-schema.md`、`prompt-templates.md`、`example-output.md` 和 `checklist.md`。
