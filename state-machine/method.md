# State Machine Method

> 用 `discovery capability map` 和 `domain model map` 生成状态机的执行协议。

## 1. Goal

把关键业务能力和领域对象之间的阶段变化、事件触发、守卫条件和终态收敛成可验证的状态机模型。

## 2. Inputs

- 主输入：
  - `discovery capability map`
  - `domain model map`
- 辅助证据：
  - `analysis` 里的 story maps / features / gwt / relations

## 2.1 Input Rules

- `discovery capability map` 是主输入，已经包含可用于状态建模的 `related_story_steps` 和 `gwt_examples`。
- `domain model map` 只用于确认状态机所属的业务边界、对象责任和状态所有权。
- `analysis` 只作为辅助证据，不得重新作为主分析对象处理。
- 上游已经抽象过的数据不得在本阶段重新归并、重新拆分或重新命名，只能用于校验、补证和反例攻击。

## 3. Output

- state machine map
- state-machine validation report

> 其中 `state machine map` 内部包含 states、events、guards、transitions、terminal states、entry / exit conditions、正向测试和负向测试。

## 4. Workflow

| Step | Input | Action | Output | Can Roll Back |
| --- | --- | --- | --- | --- |
| Read | `discovery capability map` + `domain model map` + 辅助证据 | 读取主输入，确认哪些流程需要显式建模；辅助证据只用于校验，不重新加工 | 输入摘要 | Yes |
| Select | 辅助证据中的 story maps / features / gwt | 选择具有明确阶段变化的关键流程，只挑能被主输入复核的流程片段，过滤纯展示或纯静态内容 | 候选流程 | Yes |
| Normalize | 候选流程 | 统一流程语言，把页面步骤、角色动作和领域事件对齐为状态语义 | 状态语义草案 | Yes |
| Identify | 状态语义草案 | 识别状态、事件、守卫、转移、终态 | 状态元素清单 | Yes |
| Sequence | 状态元素清单 | 组织合法转移顺序，标记前置条件、后置结果和禁止转移 | transition map | Yes |
| Invariant Check | transition map | 明确每个状态的进入条件、退出条件、停留条件和不可越过的约束 | invariants and exit criteria | Yes |
| Counterexample Sweep | 全部输出 | 用反例攻击状态机，检查遗漏状态、虚假转移、终态误判、守卫缺失、跨流程串线 | 反例审查记录 | Yes |
| Validate | 全部输出 | 用 `validation-rules.md` 检查来源、覆盖、单一职责、可触发性、可测试性、终态合理性 | state-machine validation report | Yes |
| Decide | state-machine validation report | 通过则进入 API 契约阶段，不通过则回退到 `domain model map` 或流程拆分 | go / no-go | Yes |

## 5. Core Rules

- 主输入优先于辅助证据。
- 上游已经处理过的能力、边界、例子和关系，在本阶段只能复核，不得重做一遍。
- 状态描述的是“系统当前处于什么业务阶段”，不是 UI 外观。
- 事件描述的是“发生了什么业务事实”，不是点击、跳转或请求。
- 守卫描述的是“什么条件下允许转移”，不是实现细节。
- 转移必须有明确的起点、终点和触发条件。
- 终态必须能解释为什么结束，以及结束后还能做什么。
- 一个状态机只建模一条连贯的业务流程，不混多个无关流程。
- 不允许把页面名称、按钮名称、接口名称直接当成状态名。
- 不允许把领域对象的属性变化误写成业务状态变化。
- 不允许把所有异常都塞进一个“其他”状态。
- 不允许把展示态、编辑态、提交态和业务态混在一起不加区分。

## 6. Design Heuristics

### 6.1 先看阶段，不先看页面

状态机的第一判断标准是业务阶段切换是否真实存在，而不是页面是否有切换。

### 6.2 先看事件，不先看动作

只有能改变业务阶段的事实才值得成为事件，纯操作动作不一定值得上状态机。

### 6.3 先看守卫，不先看转场

没有守卫的转移通常只是幻想流程，不是可执行状态机。

### 6.4 先看终态，不先看收尾按钮

如果无法说清业务何时结束、结束后是否允许重开，就不要定义终态。

### 6.5 先看单流程，不先看全局

一个状态机只解决一条业务主线；跨流程协同应由上下游状态机或事件驱动关系表达。

### 6.6 先问反例，再信流程图

如果一个状态机经不起“跳过状态”“重复触发”“错误终态”“逆向转移”四类反例，就不能进入下一阶段。

### 6.7 先复核，不重做

如果某个信息已经在 discovery 或 domain model 阶段被抽象过，这一层只允许拿来验证，不允许再次抽象成新的主概念。

## 7. Execution Order

1. `../index.md`
2. `method.md`
3. `validation-rules.md`
4. `output-schema.md`
5. `prompt-templates.md`
6. `checklist.md`
