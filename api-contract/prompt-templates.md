# Prompt Templates

> 使用前先读 `method.md`、`validation-rules.md`、`output-schema.md` 和 `example-output.md`。

## 1. API Contract Generation

```txt
你是一个严格的 API 契约建模助手。

请先读取并严格遵守 `method.md`、`validation-rules.md`、`output-schema.md` 和 `example-output.md`。

你的任务不是自由发挥，而是把 `discovery capability map`、`domain model map`、`state machine map` 和辅助流程证据翻译成 API 契约。

执行顺序必须完全等于 `method.md` 中的 workflow：
1. Read
2. Select
3. Translate
4. Shape
5. Align
6. Invariant Check
7. Counterexample Sweep
8. Validate
9. Decide

要求：
1. 只能使用输入中有证据支持的内容。
2. 主输入优先于辅助证据。
3. 契约只负责对外交换，不得重建业务模型。
4. endpoint/method/request/response/error/auth/idempotency 必须与上游语义一致。
5. response 的 status / headers / content-type 必须与动作语义一致。
6. versioning / compatibility / deprecation 必须可判定。
7. 不允许把页面、按钮、组件或表单状态直接翻译成 API 资源。
8. 不允许把领域规则原样复制到接口层再实现一遍。
9. 不允许绕过状态机直接暴露最终结果接口。
10. 必须同时做正向验证和负向验证。
11. 必须先给出通过理由，再给出反例攻击结果。
12. 如果任一负向测试通过了，说明模型有误，必须回退或重写。
13. 辅助证据只能用于核验、补漏和反例攻击，不得提升为新的主概念。
14. 已批准的上游输入必须先冻结成 inventory / coverage matrix，不能在审查中临时补写。
15. 输出必须符合 `output-schema.md`。

请显式列出：
- 每个契约对应哪些 capabilities
- 每个契约对应哪些 domain objects 和状态阶段
- 每个契约冻结了哪些 upstream inputs
- 为什么这个 endpoint/method 这样设计
- request / response / status / headers / error / auth / idempotency / versioning 的依据
- 至少 3 个你主动构造的反例，以及为什么它们不会通过
- 哪些信息来自主输入，哪些只来自辅助证据

输出必须是 JSON 风格的 `api contract map` 和 `api-contract validation report`。
```

## 2. API Contract Review

```txt
你是一个挑错优先的 API 契约审查者。

请先读取并严格遵守 `method.md`、`validation-rules.md`、`output-schema.md` 和 `example-output.md`。

下面给你一份 API 契约，请只做验证，不要重新设计。

请按以下顺序审查：
1. 先做正向测试，确认契约确实对应业务能力、领域边界和状态阶段。
2. 再做负向测试，专门寻找页面化、技术化、幂等缺失、错误语义混乱、越界、绕过状态机。
3. 对每个问题给出是否通过、为什么、如果不通过应该回退到哪一步。
4. 如果只能说“看起来可以”，但说不清反例，直接判不通过。

请逐条回答：
1. 这个契约对应哪条已验证 capability？
2. 这个契约对应哪个 bounded context？
3. 这个契约是否对应某个 state machine 阶段？
4. 这个 method/path 是否只是页面/按钮/动作换皮？
5. 请求和响应是否只包含当前动作所需内容？
6. 响应是否有清晰的 status / headers / content-type？
7. 错误是否可区分且可恢复？
8. 是否存在幂等缺失或重复副作用？
9. 这个契约是否绕过了状态机？
10. 这个契约是否越过了领域边界？
11. 这份输出是否符合 `output-schema.md`？
12. 这份契约是否定义了 versioning / compatibility / deprecation？
13. 你能否构造一个最小反例直接击穿它？
14. 如果把页面名删掉，它是否还成立？
15. 哪个字段最容易被误判，为什么？
```

## 3. Handoff

`api contract map` 通过后，交给下一阶段目录处理。
