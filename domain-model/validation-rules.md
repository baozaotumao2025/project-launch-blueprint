# Validation Rules

> 用来判断 `domain model map` 能不能进入下一阶段。

## 1. Validation Strategy

领域模型验证分两层：

1. 正向测试：确认模型确实表达了正确的业务边界和对象职责。
2. 负向测试：专门找错，确认模型没有把页面、接口、流程、数据表和技术结构混进来。

辅助证据只能用来核验和补漏，不能把它们再次抽象成新的主流程。

LLM 审查时必须同时执行两层验证。只做正向通过，不算通过。

为了避免“看起来对、实际上错”，验证必须按“证据 -> 结构 -> 反例 -> 回退”的顺序执行。
任何一个环节无法明确说明，都视为未通过。

## 2. Pass Table

| Check | Look At | Pass When | Fail When |
| --- | --- | --- | --- |
| Traceability | `discovery capability map` / `discovery validation report` / 辅助证据 | 每个 bounded context 都能回指至少一个已验证 capability | 只能靠推断，回不去能力地图 |
| Language | names / glossary | 每个 context 内术语统一，不同 context 的同词异义被显式区分 | 同一个词多种含义混在一个 context 里 |
| Boundary | context map | 每个 context 只覆盖一组一致的业务责任 | 把注册、报价、收资料、签字、归档硬塞一块 |
| Aggregate Integrity | aggregates | 每个 aggregate 有清晰的不变量、修改入口和所有权 | aggregate 只是文件夹，或没有任何一致性约束 |
| Behavioral Richness | entities / services | 核心规则在 domain object 内，服务层只做协调 | 所有规则都堆到 service，模型变成贫血对象 |
| Identity Clarity | entities / value objects | entity 与 value object 的职责清楚，身份和属性边界明确 | 不区分 identity 和 value，所有对象都像 DTO |
| Relationship Design | context relations | 上下游、ACL、shared kernel、published language 有明确选择 | 上下文之间关系含糊，默认共享同一模型 |
| Technical Purity | names / schema | 没有页面、按钮、接口、表单、数据库表名污染领域语言 | 用 page、screen、form、table、api 等命名领域对象 |
| Testability | examples / invariants | 每个 aggregate 和 context 都能写出可验证的例子和不变量 | 说不清怎么验证，规则只能口头描述 |
| Evolution Fit | model shape | 模型允许分拆、合并、重命名，避免过度承诺 | 过早锁死为最终实现结构 |
| Positive Test Evidence | examples / invariants | 每个 context / aggregate 都有可执行的正向验证样例 | 只有抽象结论，没有可判定样例 |

## 3. Positive Test Matrix

以下是通过信号。出现时应提高置信度，但仍需通过负向测试确认。

| Signal | Good Example | Why It Passes |
| --- | --- | --- |
| 单一语义边界 | `Customer Intake` 只管客户信息采集，不管报价或签字 | 一个 context 只承接一段一致的业务语言 |
| 明确根实体 | `Case` 作为 aggregate root 管理案件状态和关键不变量 | 修改入口集中，能保护一致性 |
| 值对象纯粹 | `Money` / `Address` / `Period` 只表达值语义 | 无身份、可替换、规则局部化 |
| 领域行为内聚 | `Quote` 自己计算、校验、确认条件 | 规则在对象内部，不漂到 service |
| 上下文隔离 | `Client Registry` 与 `Document Review` 分开 | 语言和约束不同，避免一锅炖 |
| 明确关系 | `Intake` 通过 published language 向 `Billing` 发送契约化信息 | 关系可解释，便于演化 |
| 能写出例子 | “客户提交资料后，Case 进入待审阅” | 可测试、可回放、可验证 |

## 4. Positive Tests

以下情况出现，说明模型方向正确：

- 一个 bounded context 只覆盖一段一致的业务语言。
- 一个 aggregate 可以清楚说出“谁能改它、改什么、什么时候改”。
- 同一个业务词在不同 context 中有不同定义，并且被显式标注。
- 核心行为能落到实体方法、值对象规则或领域服务，而不是 UI handler。
- 上下文之间通过明确的关系类型连接，而不是直接共享所有对象。
- 能从领域对象反推出对应的业务能力。
- 能把能力地图中的每条关键能力落到至少一个 context 或 aggregate。

## 4.1 Input Discipline

- 辅助证据只用于核验，不得变成新的主输入。
- 上游已经处理过的能力、边界、例子和关系，在本阶段只能复核，不得重做一遍。
- 如果某项信息已经在 discovery 阶段完成抽象，这一层只允许使用它来校验，不允许再把它变成新的候选主概念。

## 5. Negative Test Matrix

以下是典型失败模式。LLM 审查时要主动构造这些反例来击穿模型。

| Failure Mode | Bad Example | Why It Fails |
| --- | --- | --- |
| 页面化命名 | `RegistrationPageModel` 作为 bounded context | 这是页面，不是业务边界 |
| 功能名冒充领域名 | `QuotePackage` 直接等于领域上下文 | 只是 feature 名字，没抽象出稳定边界 |
| 技术词污染 | `ApiResponse`, `TableRow`, `ScreenState` | 这是实现细节，不是领域语言 |
| 多生命周期混写 | 一个 context 同时包住注册、报价、签字、归档 | 把多个阶段塞进同一模型 |
| 贫血模型 | `CaseService` 里写完所有规则，实体只剩字段 | 领域对象没有行为，模型失去价值 |
| 错把 VO 当 Entity | `Address` 还带独立生命周期和仓储 | 值对象不该有身份和生命周期 |
| 错把 Entity 当 VO | `Client` 只用于传值，身份无意义 | 身份语义被抹掉，后续无法稳定演化 |
| 错置关系 | 所有 context 直接共享同一套 `Case` 对象 | 边界消失，耦合失控 |
| 假装有验证 | 只写“应该”“大概”“可能” | 没有证据链，也没有可判定结论 |

## 6. Negative Tests

以下任一情况都应判为失败或至少强制回退重构：

- 只是把页面标题换成业务名。
- 只是把 feature 名字换成领域名。
- 把按钮动作、API 路径、数据库表名当成领域概念。
- 一个 context 同时装下多个阶段的业务流转。
- 一个 aggregate 跨越多个强一致性边界。
- 所有规则都被写进 service，实体和值对象是空壳。
- value object 被赋予身份、生命周期或独立管理能力。
- 不同 context 中的同名词没有歧义消解。
- 领域模型只描述“有什么数据”，不描述“有什么行为和约束”。
- 领域模型无法说明上下游关系，只剩下平面清单。

## 7. LLM Review Questions

审查模型时，LLM 必须逐项回答：

1. 这个 bounded context 对应的是哪条已验证 capability？
2. 这个命名是否只是页面/功能的改名？
3. 这里是否把多个生命周期阶段混进来了？
4. 这个 aggregate 的不变量是什么？如果没有，就是失败信号。
5. 这个对象为什么是 entity，不是 value object？
6. 这个对象为什么是 value object，不是 entity？
7. 这个规则为什么放在 domain service，而不是实体方法？
8. 这个 context 与其他 context 是什么关系？
9. 是否存在同词异义没有拆开？
10. 是否有任何技术词混进了领域命名？
11. 如果把页面、接口、表单、数据库名全部删掉，这个模型还能成立吗？
12. 如果把 service 里的逻辑全部移走，是否还能指出哪些规则应该留在实体或值对象里？

如果任一问题无法被明确回答，就视为模型不稳。

## 8. Go Rules

- 至少有一个已验证 capability 作为证据。
- 每个 bounded context 都有明确边界、责任和语言。
- 每个 aggregate 都有明确不变量。
- 每个 entity 都有身份语义。
- 每个 value object 都可替换、无身份、值相等即相同。
- 每个 context 关系都能说明为什么这么连。
- 输出中没有页面、按钮、表单、接口、数据库表的直接命名污染。
- 每个 context / aggregate / entity / value object 都至少有一个正向测试和一个负向测试

## 9. No-Go Rules

出现以下任一情况，直接回退：

- 证据不足
- 边界重叠且无法解释
- 术语不统一
- 领域对象没有行为
- aggregate 无不变量
- 上下文关系未定义
- 技术概念污染领域命名
- 正向能过但负向测试一戳就破
- 不能构造任何可执行反例
- 只能得到模糊判断，不能给出明确回退点
- 辅助证据被当成了新的主分析对象
