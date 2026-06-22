# API Contract Method

> 用 `discovery capability map`、`domain model map` 和 `state machine map` 生成 API 契约的执行协议。

## 1. Goal

把业务能力、领域边界和状态流转翻译成稳定、可实现、可验证的 API 契约，明确前后端之间如何交换数据和语义。

## 2. Inputs

- 主输入：
  - `discovery capability map`
  - `domain model map`
  - `state machine map`
- 辅助证据：
  - `analysis` 里的 story maps / features / gwt / relations

## 2.1 Input Rules

- `discovery capability map`、`domain model map` 和 `state machine map` 是主输入，已经分别完成能力、边界与流程阶段的抽象。
- `analysis` 只作为辅助证据，不得重新作为主分析对象处理。
- 上游已经抽象过的数据不得在本阶段重新归并、重新拆分或重新命名，只能用于校验、补证和反例攻击。
- `analysis` 里的信息只能用于核验、补漏和反例攻击，不得提升为新的主概念。
- API 契约只翻译主输入，不重新定义业务能力、领域边界或状态机。

## 3. Output

- api contract map
- api-contract validation report

> 其中 `api contract map` 内部包含 api contracts、endpoints、methods、requests、responses、errors、auth、idempotency、pagination / filtering / sorting、versioning / compatibility / deprecation、正向测试和负向测试。

## 4. Workflow

| Step | Input | Action | Output | Can Roll Back |
| --- | --- | --- | --- | --- |
| Read | 主输入 + 辅助证据 | 读取上游已验证结果，确认哪些能力需要通过 API 暴露；辅助证据只用于核验 | 输入摘要 | Yes |
| Select | 主输入 | 选择需要对外暴露的数据流、动作流和查询流，过滤纯 UI 状态和内部实现细节 | 候选契约 | Yes |
| Translate | 候选契约 | 把能力、边界和状态语义翻译成 HTTP 资源、查询和写操作接口 | 契约草案 | Yes |
| Shape | 契约草案 | 设计 endpoint、method、request、response、status、headers、error、auth、idempotency、pagination、versioning 结构 | 接口结构清单 | Yes |
| Align | 接口结构清单 | 对齐领域对象、状态机节点和 API 边界，避免重复表达业务规则 | 对齐记录 | Yes |
| Invariant Check | 接口结构清单 | 明确每个接口的输入约束、输出约束、错误约束和幂等约束 | contract invariants | Yes |
| Counterexample Sweep | 全部输出 | 用反例攻击契约，检查资源错分、方法错用、错误码混乱、重复业务规则、状态泄漏 | 反例审查记录 | Yes |
| Validate | 全部输出 | 用 `validation-rules.md` 检查来源、边界、语义纯度、可实现性、可测试性、重放与幂等 | api-contract validation report | Yes |
| Decide | api-contract validation report | 通过则进入设计系统阶段，不通过则回退到 `state machine map` 或接口重切 | go / no-go | Yes |

## 5. Core Rules

- API 契约负责“怎么交换数据”，不负责“业务应该怎么演进”。
- endpoint 和 method 是资源与动作的公开形式，不是业务本体。
- request / response 是契约边界数据，不是领域对象本身。
- error 只能表达接口层可观测失败，不替代业务规则。
- auth 只表达谁能访问或执行，不重写业务权限模型。
- idempotency 只解决重复调用的可控性，不替代业务状态机。
- pagination / filtering / sorting 是查询契约，不是领域模型。
- status / headers / content-type 只表达 HTTP 响应语义，不替代领域状态。
- versioning / compatibility / deprecation 只管理演进，不改变业务能力边界。
- 不允许把页面、按钮、组件、表单状态直接映射成 API 资源。
- 不允许把 domain rule、state rule 原封不动复制到接口层再写一遍。
- 不允许把一个资源拆成多个相互矛盾的接口语义。

## 6. Design Heuristics

### 6.1 先看边界，不先看路由

先确定数据属于哪个业务边界，再决定 endpoint 怎么暴露。

### 6.2 先看语义，不先看 payload

request / response 的字段只承载契约语义，不应把领域内部结构原样搬运出来。

### 6.3 先看状态，再看幂等

幂等不是用来掩盖状态机缺失的；接口设计要先尊重状态，再讨论重复调用。

### 6.4 先看错误，再看成功

一个契约是否成熟，取决于它是否能明确表达失败、拒绝、冲突和重试。

### 6.5 先看主输入，再看辅助证据

如果某项信息已经被上游抽象过，这一层只能翻译和对齐，不允许重新定义它。

### 6.6 先问反例，再信接口

如果接口设计经不起“重复提交”“越权访问”“状态不一致”“字段缺失”“错误重放”五类反例，就不能进入下一阶段。

### 6.7 先翻译，不重建

API 契约的职责是把上游模型翻译成外部可消费的形式，不是重新开一套业务模型。

## 7. Execution Order

1. `../index.md`
2. `method.md`
3. `validation-rules.md`
4. `output-schema.md`
5. `prompt-templates.md`
6. `checklist.md`
