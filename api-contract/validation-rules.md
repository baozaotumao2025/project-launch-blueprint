# Validation Rules

> 用来判断 `api contract map` 能不能进入下一阶段。

## 1. Validation Strategy

API 契约验证分两层：

1. 正向测试：确认契约确实表达了业务能力、领域边界和状态流转的对外交换方式。
2. 负向测试：主动寻找资源错分、方法错用、错误码混乱、重复业务规则、状态泄漏和 UI 化命名。

辅助证据只能用来核验和补漏，不能把它们再次抽象成新的主流程。

LLM 审查时必须同时执行两层验证。只做正向通过，不算通过。

验证必须遵循顺序：
1. 先看来源
2. 再看接口语义
3. 再看请求、响应、错误和幂等
4. 再做反例攻击
5. 最后决定回退或通过

任何一步不能明确说明，都视为未通过。

## 2. Pass Table

| Check | Look At | Pass When | Fail When |
| --- | --- | --- | --- |
| Traceability | `discovery capability map` / `domain model map` / `state machine map` / 辅助证据 | 每个契约都能回指业务能力、领域对象或状态阶段 | 只能靠推断，回不去上游产物 |
| Boundary Purity | contract scope | 契约只覆盖一个明确边界或资源族 | 一个接口同时揉进多个边界 |
| Method Fit | HTTP method / action | GET/POST/PATCH/PUT/DELETE 等用法与语义一致 | 把读写语义混乱使用 |
| Status Semantics | response status / headers | 成功响应的状态码、头部和内容类型与动作语义一致 | 只有内容字段，没有可判定的 HTTP 成功语义 |
| Request Clarity | request schema | 请求体只包含完成当前动作所需字段 | 把 UI 状态、临时计算结果或内部结构暴露出来 |
| Response Clarity | response schema | 响应体只返回契约需要的状态与数据 | 把不相关内部结构全量泄露 |
| Error Semantics | errors | 错误可区分、可恢复、可观测 | 只有一个泛用错误或错误语义混乱 |
| Auth Clarity | auth rules | 权限与角色/范围/边界清楚 | 访问控制模糊，或与业务规则混在一起 |
| Idempotency Fit | mutating endpoints | 需要重放控制的写接口有明确幂等策略 | 重复提交会产生不可控副作用 |
| State Alignment | state machine | 接口动作与状态机阶段一致，不越界 | 接口绕过状态，直接做最终结果 |
| Versioning Fit | versioning / compatibility / deprecation | 契约能说明演进、兼容和废弃边界 | 版本演进只能靠口头约定 |
| Testability | examples / invariants | 每个契约都能写出可验证请求/响应/错误例子 | 说不清怎么测，规则只能口头描述 |
| Evolution Fit | model shape | 契约允许版本化和局部扩展 | 过早锁死实现细节 |

## 3. Positive Test Matrix

| Signal | Good Example | Why It Passes |
| --- | --- | --- |
| 资源清晰 | `GET /clients/{id}` 只读客户档案 | 路径和语义一致 |
| 动作清晰 | `POST /quotes/{id}/confirm` 表达明确决策动作 | 动作与领域阶段一致 |
| 错误可区分 | `400 invalid_payload` vs `409 state_conflict` | 错误语义可操作 |
| 幂等明确 | 提交类接口有 idempotency key | 防止重复调用副作用 |
| 边界清楚 | 一个契约只服务一个 bounded context | 不把多个模型拼一起 |
| 能写例子 | Given 合法请求 When 调用接口 Then 返回可验证响应 | 可测试、可回放 |

## 4. Negative Test Matrix

| Failure Mode | Bad Example | Why It Fails |
| --- | --- | --- |
| 页面化接口 | `POST /register-page-open` | 这是页面状态，不是业务契约 |
| 直接暴露 UI 状态 | `screenMode=edit` | 这是 UI 细节，不是 API 语义 |
| 读写混乱 | `GET /close-case` | GET 不应该承载副作用 |
| 把业务规则写死在接口 | 接口层重复实现领域校验并与领域层冲突 | 契约层不应重建业务逻辑 |
| 错误泛化 | 所有失败都返回 `400 error` | 无法区分冲突、拒绝、缺失、重试 |
| 幂等缺失 | 重复提交产生重复记录 | 写接口不可控 |
| 响应缺语义 | 只有 response body，没有 status/headers/content-type | 无法判断成功是什么 |
| 越界返回 | 响应把所有内部关联对象一次性吐出 | 破坏边界与演化 |
| 状态绕过 | 直接提供“最终完成”接口绕过中间状态 | 与状态机不一致 |
| 演进缺失 | 新旧版本只能靠实现者记忆区分 | 无法做兼容迁移 |
| 纯推断 | 没有上游映射或辅助证据 | 没有证据链 |

## 5. LLM Review Questions

审查 API 契约时，LLM 必须逐项回答：

1. 这个契约对应哪条已验证 capability？
2. 这个契约对应哪个 bounded context 或 state machine 阶段？
3. 这个 endpoint/method 是否只是页面名或按钮名换皮？
4. 请求和响应是否只包含当前动作需要的内容？
5. 这个错误是否能区分可恢复、不可恢复、冲突和拒绝？
6. 这个响应是否有清晰的 status / headers / content-type 语义？
7. 这个接口是否有幂等策略？
8. 这个契约是否绕过了状态机？
9. 这个契约是否越过了领域边界？
10. 这个契约是否定义了 versioning / compatibility / deprecation？
11. 是否存在同一个业务概念在接口层被重新命名并拆散？
12. 是否能构造一个最小反例直接击穿它？

如果任一问题无法被明确回答，就视为不通过。

## 6. Go Rules

- 至少有一条来自 `discovery capability map` 的能力佐证。
- 至少有一条来自 `domain model map` 的边界或对象佐证。
- 至少有一条来自 `state machine map` 的阶段佐证。
- 辅助证据只用于核验，不得变成新的主输入。
- 每个契约都能明确表达方法、路径、请求、响应、错误、鉴权或幂等。
- 每个契约都能明确表达成功响应的 status / headers / content-type。
- 每个契约都能说明 versioning / compatibility / deprecation。
- 每个 mutating endpoint 都有明确副作用边界。
- 每个契约都能写出可验证例子。

## 7. No-Go Rules

出现以下任一情况，直接回退：

- 证据不足
- 边界不清
- 方法语义不对
- 请求/响应语义混乱
- 错误语义不清
- 幂等缺失
- 契约绕过状态机
- 契约越过领域边界
- 不能构造可执行反例
- 不能明确说明回退点
- 辅助证据被当成了新的主分析对象
