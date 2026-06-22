# Design System Method

> 用 `api contract map` 生成设计系统的执行协议。

## 1. Goal

把已验证的 API 契约翻译成可复用、可组合、可访问、可响应式适配的设计系统，确保页面实现与业务语义保持一致。

## 2. Inputs

- 主输入：
  - `api contract map`
  - `api-contract validation report`
- 辅助证据：
  - `state machine map`
  - `domain model map`
  - `discovery capability map`
  - `analysis` 里的 story maps / features / gwt / relations

## 2.1 Input Rules

- `api contract map` 和 `api-contract validation report` 是主输入，已经包含对外语义、状态语义和演进约束。
- `state machine map`、`domain model map` 和 `discovery capability map` 只作为辅助证据，用于核验状态语义、对象语义和能力语义，不得重新作为主分析对象处理。
- `analysis` 只作为辅助证据，不得重新作为主分析对象处理。
- 上游已经抽象过的数据不得在本阶段重新归并、重新拆分或重新命名，只能用于校验、补证和反例攻击。
- 设计系统只翻译主输入，不重新定义业务能力、领域边界、状态机或 API 契约。

## 3. Output

- design system map
- design-system validation report

> 其中 `design system map` 内部包含 tokens、color system、typography、spacing、radius / elevation / shadow rules、layout rules、iconography rules、components、states、interaction patterns、accessibility rules、responsive rules、motion rules、usage guidelines、anti-patterns、正向测试和负向测试。

## 4. Workflow

| Step | Input | Action | Output | Can Roll Back |
| --- | --- | --- | --- | --- |
| Read | 主输入 + 辅助证据 | 读取已验证契约与状态语义，确认哪些 UI 规则必须统一，哪些只适合局部实现 | 输入摘要 | Yes |
| Extract Semantics | api contract map | 提取请求、响应、错误、鉴权、幂等、状态与空态等 UI 需要承载的语义 | 语义清单 | Yes |
| Cluster Surfaces | 语义清单 | 按颜色、排版、布局、反馈、输入、导航、数据展示、空态、错误态进行聚类 | surface clusters | Yes |
| Define Tokens | surface clusters | 定义设计 tokens、语义 tokens 与主题规则 | token map | Yes |
| Design Components | token map + 语义清单 | 定义可复用组件、组件变体、组件状态和组合规则 | component inventory | Yes |
| Define States | 组件库存 | 设计 loading / empty / success / warning / error / disabled / focused 等状态样式 | component states | Yes |
| Define Rules | 组件库存 + token map | 设计响应式、密度、无障碍、动效、内容和布局规则 | design rules | Yes |
| Counterexample Sweep | 全部输出 | 用反例攻击设计系统，检查页面化组件、一次性样式、语义冲突、可访问性缺失、响应式失效 | 反例审查记录 | Yes |
| Validate | 全部输出 | 用 `validation-rules.md` 检查语义纯度、复用性、可访问性、响应式、动效、测试性 | design-system validation report | Yes |
| Decide | design-system validation report | 通过则进入垂直切片阶段，不通过则回退到 `api contract map` 或组件重切 | go / no-go | Yes |

## 5. Core Rules

- 设计系统负责“怎么长得稳定、怎么交互一致”，不负责“业务应该怎么演进”。
- token 是全局语义，不是页面常量。
- component 是可复用单元，不是页面专属片段。
- component state 必须覆盖业务可见状态，不得漏掉错误、空态、加载态和禁用态。
- 颜色必须首先表达语义，其次才是品牌审美。
- 排版必须首先服务信息层级，其次才是风格。
- 响应式规则必须明确断点、布局重排和内容收缩策略。
- 无障碍规则必须默认存在，而不是补丁式添加。
- 动效必须服务于状态变化和注意力引导，不得仅为装饰。
- 不允许把单个页面的临时视觉方案提升为全局 token。
- 不允许把业务规则塞进组件内部。
- 不允许把 API 字段名直接作为 UI 文案或组件名。

## 6. Design Heuristics

### 6.1 先看语义，再看风格

先确定状态、反馈、层级、密度和优先级，再决定颜色和排版。

### 6.2 先做 token，再做组件

先定义可复用 token 和语义层，再组装组件，避免组件反向绑死样式。

### 6.3 先做状态矩阵，再做外观

一个组件如果说不清 loading / empty / error / disabled / success 的表现，就不算成熟。

### 6.4 先看跨切片一致性，再看局部最优

设计系统要能跨多个能力切片复用，而不是只对当前页面好看。

### 6.5 先看可访问性，再看审美

如果对比度、键盘焦点、屏幕阅读器和触控区域不成立，风格再好也不能进入下一阶段。

### 6.6 先问反例，再信组件库

如果一个组件只能在“理想状态”成立，就说明它还不是设计系统。

## 7. Execution Order

1. `../index.md`
2. `method.md`
3. `validation-rules.md`
4. `output-schema.md`
5. `example-output.md`
6. `prompt-templates.md`
7. `checklist.md`
