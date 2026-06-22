# Vertical Slice Method

> 用 `api contract map`、`design system map` 和 `state machine map` 生成垂直切片的执行协议。

## 1. Goal

把已验证的契约、设计系统和状态语义组装成可运行、可测试、可替换 mock/real 的功能切片，确保页面实现直接消费稳定语义，而不是在组件里重新发明业务。

## 2. Inputs

- 主输入：
  - `api contract map`
  - `api-contract validation report`
  - `design system map`
  - `design-system validation report`
- 辅助证据：
  - `state machine map`
  - `domain model map`
  - `discovery capability map`
  - `analysis` 里的 story maps / features / gwt / relations

## 2.1 Input Rules

- `api contract map` 和 `design system map` 是主输入，已经分别稳定了交换语义和 UI 语义。
- `state machine map` 只作为辅助证据，用于确认流程状态、可达状态和禁止转移，不得重新作为主分析对象处理。
- `domain model map` 和 `discovery capability map` 只作为辅助证据，用于核验边界和能力来源，不得重新作为主分析对象处理。
- `analysis` 只作为辅助证据，不得重新作为主分析对象处理。
- 上游已经抽象过的数据不得在本阶段重新归并、重新拆分或重新命名，只能用于校验、补证和反例攻击。
- 垂直切片只组装主输入，不重新定义业务能力、契约、状态机或设计系统。

## 3. Output

- vertical slice map
- vertical-slice validation report

> 其中 `vertical slice map` 内部包含 slice inventory、route map、page map、feature module map、hook map、service map、repository map、mock map、data adapter map、state wiring rules、error handling rules、loading / empty / success / error flow rules、integration boundaries、acceptance criteria、正向测试和负向测试。

## 4. Workflow

| Step | Input | Action | Output | Can Roll Back |
| --- | --- | --- | --- | --- |
| Read | 主输入 + 辅助证据 | 读取契约、设计系统和状态语义，确认哪些能力可以组合成完整切片 | 输入摘要 | Yes |
| Select Slice | 主输入 | 选择一个明确的业务能力切片，过滤掉跨切片拼接和一次性演示内容 | slice candidate | Yes |
| Map Surface | api contract map + design system map | 把接口、状态和 UI 语义映射到 route、page、module、hook、service、repository 和 mock | slice blueprint | Yes |
| Wire Data | slice blueprint | 定义数据流、状态流、错误流、加载流、空态流和乐观更新/回滚规则 | data wiring map | Yes |
| Build Boundaries | slice blueprint | 明确哪些逻辑在 UI，哪些在 hook，哪些在 service，哪些在 repository，哪些在 mock | layer boundary map | Yes |
| Define Acceptance | 主输入 | 为每个切片定义可执行验收条件和端到端结果 | acceptance criteria | Yes |
| Counterexample Sweep | 全部输出 | 用反例攻击切片，检查页面化逻辑、接口直连、设计系统失配、状态绕过、mock 假真混淆 | 反例审查记录 | Yes |
| Validate | 全部输出 | 用 `validation-rules.md` 检查可运行性、边界清晰度、状态一致性、可替换性和可测试性 | vertical-slice validation report | Yes |
| Decide | vertical-slice validation report | 通过则进入质量门禁，不通过则回退到 `api contract map` 或切片重切 | go / no-go | Yes |

## 5. Core Rules

- 垂直切片负责“把语义跑起来”，不负责重新定义语义。
- route 和 page 是承载方式，不是业务本体。
- hook 负责组织页面动作和状态连接，不负责写业务本体。
- service 负责业务流程和协调，不负责 UI 细节。
- repository 负责数据获取和边界适配，不负责业务决策。
- mock 负责开发和验证，不负责改变契约。
- 页面必须消费已验证契约和设计系统，不得直接揉进临时结构。
- 切片必须能在 mock 和 real 之间切换，而不改页面逻辑。
- 切片必须显式处理 loading、empty、success、error 和 retry。
- 不允许把页面拼接成“能看不能跑”的演示壳。
- 不允许把接口调用散落在组件里。
- 不允许把一个切片的临时实现提升为全局标准。

## 6. Design Heuristics

### 6.1 先看完整链路，再看单页

一个切片只有在 route -> page -> hook -> service -> repository -> data source 的链路都能说明白时，才算成立。

### 6.2 先看语义映射，再看代码组织

先确认契约和设计系统如何落地，再决定目录结构和文件拆分。

### 6.3 先看状态流，再看交互细节

如果一个切片说不清 loading、empty、error 和 retry 怎么流转，就不算可交付。

### 6.4 先看可替换性，再看实现便利

mock 和 real 的切换应该是边界层的事情，不应污染页面和业务逻辑。

### 6.5 先看反例，再信“完整打通”

如果切片只能在理想路径成立，而对缺失数据、错误响应和状态冲突无能为力，就说明它还没准备好进入质量门禁。

## 7. Execution Order

1. `../index.md`
2. `method.md`
3. `validation-rules.md`
4. `output-schema.md`
5. `example-output.md`
6. `prompt-templates.md`
7. `checklist.md`
