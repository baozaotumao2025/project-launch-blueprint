# Domain Model Method

> 用 `discovery capability map` 生成领域模型的执行协议。

## 1. Goal

把已经通过 `discovery` 验证的业务能力，收敛成稳定、可演化、可实现的领域边界与领域对象。

## 2. Inputs

- 主输入：
  - `discovery capability map`
  - `discovery validation report`
- 辅助证据：
  - `analysis` 里的 persona / story map / page / feature / relations

## 2.1 Input Rules

- `discovery capability map` 和 `discovery validation report` 是主输入，已经包含经过验证的能力与证据结论。
- `analysis` 只作为辅助证据，不得重新作为主分析对象处理。
- 上游已经抽象过的数据不得在本阶段重新归并、重新拆分或重新命名，只能用于校验、补证和反例攻击。
- `analysis` 里的信息只能用于核验、补漏和反例攻击，不得提升为新的主概念。

## 3. Output

- domain model map
- domain-model validation report

> 其中 `domain model map` 内部包含 bounded contexts、aggregates、entities、value objects、domain services、domain events、context map、正向测试和负向测试。

## 4. Workflow

| Step | Input | Action | Output | Can Roll Back |
| --- | --- | --- | --- | --- |
| Read | `discovery capability map` + `discovery validation report` + 辅助证据 | 读取主输入，确认哪些能力可以继续抽象，哪些还不稳定；辅助证据只用于校验，不重新加工 | 输入摘要 | Yes |
| Collect | `discovery capability map` + `discovery validation report` + 辅助证据 | 逐项枚举所有输入，生成 inventory 和覆盖模板 | input inventory | Yes |
| Group | `discovery capability map` 中的 capabilities | 按业务意图、语义一致性、生命周期、协作边界进行分组 | 候选领域簇 | Yes |
| Name | 候选领域簇 | 为每个簇提炼稳定术语，统一业务语言，去掉页面化/技术化命名 | bounded context 候选 | Yes |
| Split / Merge | bounded context 候选 | 检查是否混入多个职责，必要时拆分或合并 | context map 草案 | Yes |
| Design | context map 草案 | 在每个 context 内识别 aggregate、entity、value object、domain service、domain event | 领域对象清单 | Yes |
| Invariant Check | 领域对象清单 | 明确每个 aggregate 的不变量、事务边界、修改入口和所有权 | invariants and ownership rules | Yes |
| Relationship Check | 领域对象清单 | 定义上下文之间的 upstream / downstream、ACL、shared kernel、published language 等关系 | context relationships | Yes |
| Counterexample Sweep | 全部输出 | 用负向样例逐项攻击模型，查页面化、技术化、贫血化、混边界、混生命周期、同词异义 | 反例审查记录 | Yes |
| Validate | 全部输出 | 用 `validation-rules.md` 做正向和负向验证，检查边界纯度、对象职责、术语一致性、可实现性 | domain-model validation report | Yes |
| Decide | domain-model validation report | 通过则进入状态机阶段，不通过则回退到 `discovery capability map` 或领域边界重切 | go / no-go | Yes |

## 5. Core Rules

- 先分边界，再做对象，不允许反过来。
- 主输入优先于辅助证据。
- 上游已经处理过的能力、边界、例子和关系，在本阶段只能复核，不得重做一遍。
- 一个 bounded context 只能表达一套一致的业务语言。
- 一个 aggregate 只负责一组强一致性不变量。
- entity 负责身份和值变化，不负责跨边界协调。
- value object 只表达值语义，不承载身份和生命周期。
- domain service 只放无法自然归属到单一实体或值对象的领域规则。
- domain event 只描述已经发生的领域事实，不描述 UI 行为或技术实现。
- 不允许把 API、页面、表单、数据库表直接当成领域对象。
- 不允许为了实现方便而合并语义不同的 context。
- 不允许把高频查询视图、报表视图、审批流程强行塞进同一个模型。
- 任何进入模型的输入都必须在 inventory 里出现一次，并且在覆盖矩阵里有明确去向。

## 6. Design Heuristics

### 6.1 先看语言，不先看代码

如果同一个词在不同场景中含义不同，优先拆 context，而不是强行统一成一个对象。

### 6.2 先看行为，再看名词

一个候选对象只有在能清楚说明“它做什么、约束什么、谁拥有它”时，才值得进入领域模型。

### 6.3 先看不变量，再看结构

如果一组数据需要一起被保护、一起被修改、一起保持一致，它更可能属于同一个 aggregate。

### 6.4 先看变化频率，再看复用幻想

变化节奏不同、责任不同、协作对象不同的能力，不应为了“看起来复用”而塞进一个模型。

### 6.5 先看边界，再看技术映射

bounded context 是业务边界，不是包名边界、接口边界或数据库边界，但最终应能映射到这些技术边界。

### 6.6 先问反例，再信正例

如果一个模型只能通过“看起来合理”的正向检查，却经不起最简单的反向提问，就说明它只是叙述，不是模型。

## 7. Execution Order

1. `../index.md`
2. `method.md`
3. `validation-rules.md`
4. `output-schema.md`
5. `prompt-templates.md`
6. `checklist.md`
