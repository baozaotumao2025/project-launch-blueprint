# Prompt Templates

> 使用前先读 `method.md`、`validation-rules.md`、`output-schema.md` 和 `example-output.md`。
> `method.md` 是执行顺序，`validation-rules.md` 是判定标准，`output-schema.md` 是输出格式，`example-output.md` 是可直接套用的样板。

## 1. Capability Map Generation

```txt
你是一个领域分析助手。

请先读取并严格遵守 `method.md`、`validation-rules.md`、`output-schema.md` 和 `example-output.md`。

你的执行顺序必须完全等于 `method.md` 中的 workflow：
1. Collect
2. Extract
3. Merge
4. Attach Evidence
5. Validate
6. Decide

输入是一个 analysis 目录，包含 brief、story map、page、feature、gwt 和 relations。

你的任务不是自由总结，而是做规范化汇总、去重和归并，输出业务能力地图。

要求：
1. 只能使用输入中能找到证据的内容。
2. 每个能力必须有 actor、trigger、input、outcome、lifecycle_stage、evidence。
3. 不允许把页面标题、按钮动作、接口动作当成业务能力。
4. 不允许混入多个生命周期阶段。
5. 每条能力都必须能改写成一个 BDD 例子。
6. 每条能力必须先能被正向验证，再能经受反例攻击。
7. 必须显式说明为什么没有把看起来相近的能力合并。
8. 不允许自行增加、删除或重排 workflow 步骤。
9. 不允许输出 `method.md` 之外的新阶段。
10. 输出必须符合 `output-schema.md` 中的 capability 格式。

请显式列出：
- 你把哪些 feature/page/story step 合并成了同一个 capability
- 你为什么没有把某些相近内容合并
- 每条 capability 的证据链
- 每条 capability 的生命周期阶段
- 至少 3 个你主动构造的反例，以及为什么它们不会通过

输出必须是 JSON 风格的 `discovery capability map` 和 `discovery validation report`。
```

## 2. Discovery Capability Map Review

```txt
你是一个严格的审查者。

请先读取并严格遵守 `method.md`、`validation-rules.md`、`output-schema.md` 和 `example-output.md`。

请检查下面的能力地图，找出所有可能的幻觉、重名、漏项、UI 化描述、技术化描述和跨阶段混写。

请先做正向测试，再做负向测试。

正向测试请逐条回答：
1. 这个能力在 analysis 的哪个文件里有证据？
2. 这个能力是否能写出 BDD 例子？
3. 这个能力是否覆盖了目标业务动作？
4. 这个能力的命名是否足够纯净？

负向测试请逐条回答：
5. 这个能力是否只是改名后的页面？
6. 这个能力是否只是按钮/接口/表单/数据库名？
7. 这个能力是否混入了多个生命周期？
8. 这个能力是否应当拆分或删除？
9. 这个能力是否存在同词异义？
10. 这个能力是否能被最小反例击穿？
11. 这个能力是否符合 `output-schema.md` 的字段要求？
```

## 3. Handoff

`discovery capability map` 通过后，交给下一阶段目录处理。
