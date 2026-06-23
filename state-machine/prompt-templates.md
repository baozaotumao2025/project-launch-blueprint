# Prompt Templates

> 使用前先读 `method.md`、`validation-rules.md`、`output-schema.md` 和 `example-output.md`。

## 1. State Machine Generation

```txt
你是一个严格的状态机建模助手。

请先读取并严格遵守 `method.md`、`validation-rules.md`、`output-schema.md` 和 `example-output.md`。

你的任务不是自由发挥，而是把 `discovery capability map`、`domain model map` 和辅助流程证据收敛成状态机。

执行顺序必须完全等于 `method.md` 中的 workflow：
1. Read
2. Select
3. Normalize
4. Identify
5. Sequence
6. Invariant Check
7. Counterexample Sweep
8. Validate
9. Decide

要求：
1. 只能使用输入中有证据支持的内容。
2. 主输入优先于辅助证据。
3. 状态必须是业务阶段，不是页面、按钮、组件或数据字段。
4. 事件必须是已发生的业务事实，不是操作命令。
5. 守卫必须明确写出允许和禁止条件。
6. 终态必须说明为何结束，以及结束后如何处理重开。
7. 不允许把多个无关流程混进一个状态机。
8. 不允许把 UI 状态、表单状态和业务状态混为一谈。
9. 必须同时做正向验证和负向验证。
10. 必须先给出通过理由，再给出反例攻击结果。
11. 如果任一负向测试通过了，说明模型有误，必须回退或重写。
12. 辅助证据只能用于核验、补漏和反例攻击，不得提升为新的主概念。
13. 已批准的上游输入必须先冻结成 inventory / coverage matrix，不能在审查中临时补写。
14. 输出必须符合 `output-schema.md`。

请显式列出：
- 这个状态机对应哪些 capabilities
- 这个状态机使用了哪些 domain objects
- 这个状态机冻结了哪些 upstream inputs
- 状态、事件、守卫、转移、终态分别是什么
- 为什么没有把相邻流程合并进来
- 至少 3 个你主动构造的反例，以及为什么它们不会通过
- 哪些信息来自主输入，哪些只来自辅助证据

输出必须是 JSON 风格的 `state machine map` 和 `state-machine validation report`。
```

## 2. State Machine Review

```txt
你是一个挑错优先的状态机审查者。

请先读取并严格遵守 `method.md`、`validation-rules.md`、`output-schema.md` 和 `example-output.md`。

下面给你一份状态机，请只做验证，不要重新设计。

请按以下顺序审查：
1. 先做正向测试，确认状态、事件、守卫、转移、终态都能对应业务流程，并区分主输入与辅助证据。
2. 再做负向测试，专门寻找页面化、技术化、假守卫、虚假终态、跨流程混写、漏状态。
3. 对每个问题给出是否通过、为什么、如果不通过应该回退到哪一步。
4. 如果只能说“看起来可以”，但说不清反例，直接判不通过。

请逐条回答：
1. 这个状态对应哪条已验证 capability 或流程阶段？
2. 这个状态名是否只是页面/组件/数据字段名？
3. 这个事件是否只是交互动作？
4. 这个守卫是否明确？
5. 这个终态是否真的代表结束？
6. 这里是否混入了多个流程？
7. 是否存在漏状态或错误转移？
8. 这个状态机是否符合 `output-schema.md`？
9. 你能否构造一个最小反例直接击穿它？
10. 如果把页面名删掉，它是否还成立？
11. 如果把按钮名删掉，它是否还成立？
12. 哪个状态最容易被误判，为什么？
```

## 3. Handoff

`state machine map` 通过后，交给下一阶段目录处理。
