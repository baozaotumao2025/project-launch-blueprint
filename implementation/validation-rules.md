# Validation Rules

> 用来判断 `Codex goal` 驱动的 implementation 计划是否可以进入真实编码。

## 1. Validation Strategy

实现桥接验证分两层：

1. 目标冻结：先确认 `Codex goal` 是否足够明确，能否变成可执行范围。
2. 落地审查：再确认骨架、任务、验证和回退点是否真的能支撑一键生成原型代码。

辅助证据只能用于补足工程约束，不能把新的业务概念塞回实现层。

已批准的上游输入必须先冻结成 inventory / coverage matrix，不能在实现时临时补写。

## 2. Pass Table

| Check | Look At | Pass When | Fail When |
| --- | --- | --- | --- |
| Goal Clarity | `Codex goal` | 目标能被改写成单一、可执行的实现范围 | 目标含糊，无法判断要生成什么 |
| Goal Registry | frozen scope | goal 被拆成可追踪的 registry，且总数、顺序、依赖都清楚 | 只说“有几个步骤”，但没有 goal 级别拆解 |
| Scope Freeze | goal + quality gates | 已经明确哪些内容进入这次实现，哪些内容不进入 | 边界漂移，边做边改题 |
| Upstream Input Coverage | frozen upstream input inventory | 每个已批准上游输入都被显式对账 | 有输入未进入 inventory 或 coverage |
| Artifact Mapping | 上游产物 | 每个上游产物都有明确代码落点 | 产物悬空，没有对应目录或文件 |
| Scaffold First | code scaffold map | 先生成目录、文件和骨架，再填行为 | 先写散点代码，后补结构 |
| Slice Coherence | task batches | 每个批次都能完成一条能力闭环 | 一个批次混入多个无关能力 |
| Boundary Separation | implementation tasks | `schema / repository / service / hook / component / page` 职责分离 | 逻辑互相穿透，边界混乱 |
| Verification Coverage | verification plan | 正向与负向检查都存在 | 只有“能跑”的检查，没有反例 |
| Rollback Safety | rollback_point | 每个关键步骤都知道回退到哪里 | 失败后无法恢复 |
| Regression Safety | regression_checks | 每完成一个 goal 都会回归前序已完成能力 | 只测新功能，不回归旧功能 |

## 3. Positive Test Matrix

| Signal | Good Example | Why It Passes |
| --- | --- | --- |
| 目标清晰 | “生成客户邀请原型页和相关骨架” | 能直接落到目录和文件 |
| 骨架先行 | 先有 `features/invite/` 和相关 type / test 壳 | 后续实现有边界 |
| 批次可执行 | 一个批次只负责一个 vertical slice | 能拆给 LLM 或人类连续执行 |
| 验证完整 | 有 mock / real 同构校验 | 可以切换实现而不改页面 |
| 可回退 | 每个批次都有 rollback point | 出错可退回上游层 |

## 4. Negative Test Matrix

| Failure Mode | Bad Example | Why It Fails |
| --- | --- | --- |
| 目标不清 | “帮我把项目做起来” | 无法判断要生成什么 |
| 直接写码 | 没有 scaffold map 就开始改组件 | 结构失控，后续难维护 |
| 混写职责 | 页面里直接 fetch 和校验 | 边界被打穿 |
| 假验证 | 只有 happy path，没有反例 | 不能证明实现可靠 |
| 无回退点 | 一个任务把所有层都改了 | 出错无法局部回滚 |

## 5. Go Rules

- `Codex goal` 必须能被翻译成单一实现目标。
- 已批准的上游输入必须完成 inventory / coverage 对账。
- 至少有一个明确的 `code_scaffold_map` 条目。
- 至少有一个明确的 `task_batch_list` 批次。
- 至少有一个明确的 `goal_registry` 条目。
- 至少有一条正向检查和一条负向检查。
- 至少有一条 `regression_checks`。
- 每个关键实现动作都必须有回退点。
- 输出必须符合 `output-schema.md`。

## 6. No-Go Rules

出现以下任一情况，直接回退：

- goal 仍然含糊
- 上游质量门禁没过
- 产物没有明确代码落点
- 先实现后补结构
- 没有负向验证
- 没有回归验证
- mock 和 real 不能同构
- 不能说明回退点
- 试图重建新的业务语义
