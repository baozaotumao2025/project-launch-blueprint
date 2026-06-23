# Validation Rules

> 用来判断 `vertical slice map` 能不能进入下一阶段。

## 1. Validation Strategy

垂直切片验证分两层：

1. 正向测试：确认一个切片确实把业务能力、契约、状态和设计系统串起来了。
2. 负向测试：主动寻找页面壳、接口直连、状态绕过、设计系统失配、mock 假真混淆和跨切片拼接。

辅助证据只能用来核验和补漏，不能把它们再次抽象成新的主流程。

`upstream input inventory` 必须覆盖所有已批准的上游阶段输入，并在 `coverage matrix` 中逐项对账，不能漏记、重记或临时补写。

LLM 审查时必须同时执行两层验证。只做正向通过，不算通过。

验证必须遵循顺序：
1. 先看来源
2. 再看切片完整性
3. 再看状态与数据流
4. 再做反例攻击
5. 最后决定回退或通过

任何一步不能明确说明，都视为未通过。

## 2. Pass Table

| Check | Look At | Pass When | Fail When |
| --- | --- | --- | --- |
| Traceability | `api contract map` / `design system map` / `state machine map` / 辅助证据 | 每个切片都能回指能力、契约、状态和组件语义 | 只能靠猜测，回不去上游产物 |
| Upstream Input Coverage | `upstream input inventory` / `coverage matrix` | 每个已批准上游输入都被显式对账 | 有上游输入未进入 inventory 或 coverage |
| Slice Cohesion | slice scope | 一个切片只承载一条连贯能力链路 | 多个无关功能拼在一起 |
| Route Cohesion | route / page | 一个 route/page 对应清晰业务目的 | 路由只是演示壳或功能拼盘 |
| State Alignment | state machine | 页面和交互状态与状态机一致 | 绕过状态机直接到最终结果 |
| Contract Alignment | api contracts | 页面消费已验证契约，不直接散写请求 | 组件里到处直连接口 |
| Design System Alignment | design system components | 使用已验证组件与状态样式 | 重新造样式，失去复用性 |
| Mock/Real Parity | mocks / repositories | mock 和 real 的数据结构、错误语义一致 | mock 只是演示，real 重新写一套 |
| Testability | acceptance criteria | 每个切片可写端到端验收 | 说不清怎么测 |

## 3. Positive Test Matrix

| Signal | Good Example | Why It Passes |
| --- | --- | --- |
| 单切片闭环 | 一个“客户邀请”切片同时包含路由、页面、表单、接口、错误态 | 一条能力链路完整 |
| 状态一致 | 页面 loading / error / success 与状态机一致 | 交互与业务阶段不冲突 |
| 契约一致 | 页面字段和 API response 字段一一对应 | 没有随手改结构 |
| 组件复用 | 页面使用设计系统里的表单和卡片组件 | 复用而不是重写 |
| mock/real 同构 | 只是数据源切换，页面不改 | 可平滑切换 |
| 可验收 | Given 有效请求 When 提交 Then 跳转到正确结果页 | 能端到端验证 |

## 4. Negative Test Matrix

| Failure Mode | Bad Example | Why It Fails |
| --- | --- | --- |
| 页面壳 | 只有静态 UI，没有真实状态流转 | 不能算功能切片 |
| 接口直连 | 组件内部直接 fetch，绕过 service/repository | 边界混乱 |
| 状态绕过 | 直接展示“成功”，不处理 loading/error | 没有完整链路 |
| 设计失配 | 使用未验证的新样式和新组件 | 破坏统一语义 |
| mock 假真混淆 | mock 返回比真实 API 更多字段 | 后续切换必炸 |
| 跨切片拼接 | 一个页面同时装多个业务能力 | 切片不再垂直 |
| 纯推断 | 没有契约或设计系统证据，只靠实现习惯 | 没有证据链 |

## 5. LLM Review Questions

审查垂直切片时，LLM 必须逐项回答：

1. 这个切片对应哪条已验证 capability？
2. 这个切片对应哪些 api contracts？
3. 这个切片对应哪些 design system components？
4. 这个切片是否对应某个 state machine？
5. 页面是否只是展示壳？
6. 页面是否直接直连接口？
7. loading / error / empty / success 是否完整？
8. mock 和 real 是否同构？
9. 这份输出是否符合 `output-schema.md`？
10. 你能否构造一个最小反例直接击穿它？
11. 如果把页面名删掉，它是否还成立？
12. 哪个切片最容易被误判为“已经完成”，为什么？

如果任一问题无法被明确回答，就视为不通过。

## 6. Go Rules

- 至少有一条来自 `api contract map` 的契约佐证。
- 至少有一条来自 `design system map` 的组件或状态佐证。
- 至少有一条来自 `state machine map` 的状态佐证。
- 至少有一条来自已批准上游输入的输入佐证。
- 每个切片都能说明 route、page、hook、service、repository、mock 各自职责。
- 每个切片都能说明 mock/real 切换方式。
- 每个切片都能写出可执行验收条件。

## 7. No-Go Rules

出现以下任一情况，直接回退：

- 证据不足
- 切片不是单一业务能力链路
- 页面壳没有状态流转
- 接口直连散落在组件里
- 状态绕过
- 设计系统失配
- mock/real 不同构
- 不能构造可执行反例
- 不能明确说明回退点
- 辅助证据被当成了新的主分析对象
