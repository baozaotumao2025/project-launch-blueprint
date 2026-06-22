# Quality Gates Method

> 用前面所有阶段的已验证输出生成发布门禁的执行协议。

## 1. Goal

把 `discovery`、`domain model`、`state machine`、`api contract`、`design system` 和 `vertical slice` 的已验证成果，收敛成可执行的发布门槛、风险控制、回退方案和可观测性要求，保证上线不是“感觉可以”，而是“证据充分且可回滚”。

## 2. Inputs

- 主输入：
  - `discovery capability map`
  - `discovery validation report`
  - `domain model map`
  - `domain-model validation report`
  - `state machine map`
  - `state-machine validation report`
  - `api contract map`
  - `api-contract validation report`
  - `design system map`
  - `design-system validation report`
  - `vertical slice map`
  - `vertical-slice validation report`
- 辅助证据：
  - `analysis` 里的 story maps / features / gwt / relations

## 2.1 Input Rules

- 所有上游的已验证输出都是主输入，因为质量门禁的职责是验收整个链路，而不是重新抽象其中任何一层。
- `analysis` 只作为辅助证据，不得重新作为主分析对象处理。
- 上游已经抽象过的数据不得在本阶段重新归并、重新拆分或重新命名，只能用于校验、补证和反例攻击。
- 质量门禁只做验证与发布决策，不重新定义业务能力、领域边界、状态机、契约、设计系统或垂直切片。

## 3. Output

- quality gate map
- quality-gates validation report

> 其中 `quality gate map` 内部包含 release criteria、risk register、test matrix、observability requirements、rollback plan、deployment checklist、release readiness report、正向测试和负向测试。

## 4. Workflow

| Step | Input | Action | Output | Can Roll Back |
| --- | --- | --- | --- | --- |
| Read | 全部主输入 + 辅助证据 | 读取各阶段验证结果，确认发布门槛必须覆盖哪些风险 | 输入摘要 | Yes |
| Classify Risk | 各阶段 validation report | 按业务风险、技术风险、体验风险、回退风险、可观测性风险分级 | risk register | Yes |
| Build Gates | risk register | 为每类风险定义具体门槛、责任方和触发条件 | quality gate map | Yes |
| Build Tests | 前面各阶段的输出 | 建立单元、集成、契约、端到端和回归测试矩阵 | test matrix | Yes |
| Define Observability | vertical slice + api contract | 定义日志、指标、追踪、错误告警和健康检查要求 | observability requirements | Yes |
| Define Rollback | release + deployment context | 定义灰度、回滚、降级和修复流程 | rollback plan | Yes |
| Compose Checklist | 全部输出 | 汇总部署前必须满足的检查项 | deployment checklist | Yes |
| Counterexample Sweep | 全部输出 | 用反例攻击发布门槛，检查是否存在“看起来通过但实际危险”的情况 | 反例审查记录 | Yes |
| Validate | 全部输出 | 用 `validation-rules.md` 检查门槛是否覆盖风险、测试是否分层、回退是否可执行、观测是否充分 | quality-gates validation report | Yes |
| Decide | quality-gates validation report | 通过则允许发布或进入上线门禁；不通过则回退到最相关阶段重切 | go / no-go | Yes |

## 5. Core Rules

- 质量门禁负责“是否可以发布”，不负责重新定义产品。
- 发布门槛必须覆盖高风险、高影响、高回退成本的部分。
- 单元测试、集成测试、契约测试和端到端测试各自承担不同风险，不能互相替代。
- 任何上线前决策都必须知道失败如何定位、如何降级、如何回滚。
- 质量门禁必须默认把可观测性当作发布条件，而不是上线后补救。
- 质量门禁必须默认把回归测试当作发布条件，而不是“有空再补”。
- 质量门禁必须把安全、权限、性能、可访问性和数据一致性纳入门槛。
- 质量门禁不能接受“人工看过了”作为唯一证据。
- 质量门禁不能接受“本地没问题”作为发布理由。
- 质量门禁不能接受没有回退方案的变更。

## 6. Design Heuristics

### 6.1 先分风险，再定门槛

不是所有问题都用同样严格的门槛处理，先把风险按影响和概率分层。

### 6.2 先分测试层级，再谈通过

单元、集成、契约、端到端各自要覆盖不同风险面，避免所有压力堆到一种测试上。

### 6.3 先看回退，再看上线

一个变更如果回滚、降级和定位都说不清，就不该进入发布流程。

### 6.4 先看观测，再看放行

没有日志、指标、追踪和告警的发布，不算真正安全的发布。

### 6.5 先看反例，再信绿灯

如果门禁经不起“假绿灯”“局部通过”“回滚不可执行”“观测不足”这些反例，就说明门禁本身有漏洞。

## 7. Execution Order

1. `../index.md`
2. `method.md`
3. `validation-rules.md`
4. `output-schema.md`
5. `example-output.md`
6. `prompt-templates.md`
7. `checklist.md`
