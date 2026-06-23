# Validation Rules

> 用来判断 `design system map` 能不能进入下一阶段。

## 1. Validation Strategy

设计系统验证分两层：

1. 正向测试：确认 token、组件、状态、布局和交互规则能够覆盖来自 API 契约的实际 UI 需求。
2. 负向测试：主动寻找页面化组件、一次性样式、语义冲突、可访问性缺失、响应式失效和动效滥用。

辅助证据只能用来核验和补漏，不能把它们再次抽象成新的主流程。

`upstream input inventory` 必须覆盖所有已批准的上游阶段输入，并在 `coverage matrix` 中逐项对账，不能漏记、重记或临时补写。

LLM 审查时必须同时执行两层验证。只做正向通过，不算通过。

验证必须遵循顺序：
1. 先看来源
2. 再看语义
3. 再看 token / component / state
4. 再做反例攻击
5. 最后决定回退或通过

任何一步不能明确说明，都视为未通过。

## 2. Pass Table

| Check | Look At | Pass When | Fail When |
| --- | --- | --- | --- |
| Traceability | `api contract map` / `api-contract validation report` / 辅助证据 | 每个 token、组件、状态都能回指契约或状态语义 | 只能靠猜测，回不去上游产物 |
| Upstream Input Coverage | `upstream input inventory` / `coverage matrix` | 每个已批准上游输入都被显式对账 | 有上游输入未进入 inventory 或 coverage |
| Token Purity | tokens | token 是语义变量，不是页面常量 | 把页面专属颜色、间距、字号直接提成全局 token |
| Semantic Consistency | color / typography / layout / motion | 同一语义在全局保持一致 | 同一状态不同页面出现不同表达 |
| Component Reusability | components | 组件可跨切片复用，有明确变体和状态 | 一次性页面组件、只服务单页的视觉碎片 |
| State Coverage | component states | loading / empty / error / success / disabled 等状态齐全 | 只设计“正常态” |
| Accessibility Fit | accessibility rules | 对比度、焦点、触控、语义标签和读屏都成立 | 只能看不能用，或只能鼠标操作 |
| Responsive Fit | responsive rules | 断点、重排和收缩策略清楚 | 只适配桌面，或靠缩放硬撑 |
| Motion Clarity | motion rules | 动效服务于反馈、层级和状态变化 | 动效只是装饰，或干扰操作 |

## 3. Positive Test Matrix

| Signal | Good Example | Why It Passes |
| --- | --- | --- |
| 语义 token | `color.intent.primary` 统一表示主行动 | token 表达业务语义而不是页面 |
| 状态完整 | 按钮有 default / hover / focus / disabled / loading | 能覆盖真实交互 |
| 组件可复用 | `DataTable` 可用于多个能力切片 | 跨场景一致、可组合 |
| 空态明确 | 无数据时有专门 empty state | 能表达业务上“没有数据”的语义 |
| 可访问 | 焦点态明显、对比度达标 | 可键盘和读屏使用 |
| 响应式明确 | 小屏从双列降为单列 | 能跨设备稳定工作 |

## 4. Negative Test Matrix

| Failure Mode | Bad Example | Why It Fails |
| --- | --- | --- |
| 页面化 token | `invitePageBlue` | 这是页面常量，不是全局 token |
| 一次性组件 | `CustomerInviteSpecialCard` 只服务一页 | 不是可复用组件 |
| 状态缺失 | 只设计默认态，没有 error / empty / loading | 不能承接真实交互 |
| 语义冲突 | 成功和危险都用同一种颜色 | 状态语义混乱 |
| 无障碍缺失 | 只有颜色区分，没有文字/图标/焦点 | 不可访问 |
| 响应式失效 | 小屏直接横向溢出 | 无法适配移动端 |
| 动效滥用 | 每个组件都在抖动或弹跳 | 干扰操作，降低可用性 |
| 文案硬编码 | 组件内部写死某个业务文案 | 组件失去通用性 |
| 纯推断 | 没有契约或状态证据，只靠审美判断 | 没有证据链 |

## 5. LLM Review Questions

审查设计系统时，LLM 必须逐项回答：

1. 这个 token 或组件对应哪条已验证契约或状态语义？
2. 这个 token 是否只是页面常量换名？
3. 这个组件是否只服务单页？
4. 这个状态是否覆盖了 loading / empty / error / disabled / success？
5. 这个颜色语义是否一致？
6. 这个设计是否可访问？
7. 这个设计是否响应式明确？
8. 这个动效是否有必要？
9. 这份输出是否符合 `output-schema.md`？
10. 你能否构造一个最小反例直接击穿它？
11. 如果把页面名删掉，它是否还成立？
12. 哪个组件最容易被误判为可复用，为什么？

如果任一问题无法被明确回答，就视为不通过。

## 6. Go Rules

- 至少有一条来自 `api contract map` 的契约佐证。
- 至少有一条来自 `state machine map` 的状态佐证。
- 至少有一条来自已批准上游输入的输入佐证。
- 辅助证据只用于核验，不得变成新的主输入。
- 每个 token 都有明确语义。
- 每个组件都能跨场景复用或明确说明仅适用边界。
- 每个组件都能描述状态矩阵。
- 每个设计都明确无障碍与响应式策略。
- 每个设计都能写出可验证例子。

## 7. No-Go Rules

出现以下任一情况，直接回退：

- 证据不足
- token 只是页面常量
- 组件是一次性页面碎片
- 状态不完整
- 可访问性不成立
- 响应式不成立
- 动效没有语义
- 不能构造可执行反例
- 不能明确说明回退点
- 辅助证据被当成了新的主分析对象
