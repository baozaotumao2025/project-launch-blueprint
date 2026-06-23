# Domain Implementation Tutorial

> 目标：讲清楚 domain 阶段如何在 discovery 之后收敛业务边界，并把边界写成可审查、可回退、可推进的阶段状态。

## 1. Domain 的职责

`domain` 不再回答“项目里有哪些分析材料”，而是回答“这个项目真正要做什么边界内的事情”。

它承接 discovery 的结果，开始稳定化这些内容：

- 用户问题域
- 核心业务对象
- 业务范围边界
- 永久性命名
- 后续阶段要共享的业务语义

这一步的核心不是生成更多想法，而是把已经被 discovery 验证过的输入，变成后续所有 stage 的共同前提。

在更严格的版本里，domain 还会先冻结自己的 stage 文档 inventory，并对自己的输入做一次文件级或条目级 inventory，生成覆盖矩阵，确保每个进入建模的输入都能被映射、排除或标记为待澄清。这样就不会只说“看过 discovery 输出和辅助证据”，而是能明确说明每一项输入最终去了哪里。

## 2. 它依赖什么

domain 阶段应该依赖：

- 已批准的 discovery 输出
- 已冻结的项目定义和最终交付物
- `domain-model/` 目录下的方法论文件
- 冻结后的 stage 文档 inventory 和 coverage matrix
- stage 状态库中的前置阶段完成状态
- 领域建模前的输入 inventory 和 coverage matrix

如果 discovery 没有通过，domain 不应该假装进入下一步。

## 3. 当前实现怎么工作

domain 阶段沿用与 discovery 相同的工作节奏：

1. `plan`
2. `status`
3. `review packet`
4. `review run`
5. `review record`
6. `approve` / `reject`
7. `next`

在代码层，它和 discovery 共享同一套 stage 命令、review 命令、生命周期记录和 prompt bundle 装配逻辑。区别只在于 stage 目录和审查目标不同。

理解成一句话就是：

> discovery 决定“看什么”，domain 决定“边界是什么”。

## 4. 产物长什么样

domain 阶段通常要形成：

- domain boundary 说明
- 核心对象和术语
- 状态边界前提
- 可进入 state 阶段的业务定义

它不是最终代码，而是后续 state / api / design / slice 都会引用的稳定语义层。

## 5. 审查为什么仍然要隔离

domain 仍然必须走 isolated worker / subagent。

原因和 discovery 一样：

- 不能让当前对话里的生成上下文污染审查
- 不能把“我刚刚想出来的”当成 domain 的权威结论
- 不能让审查结果只存在于聊天历史里
- 输入 inventory 和 coverage matrix 也要冻结，不能在审查时悄悄补写。
- stage 文档 inventory 和 coverage matrix 也要冻结，不能在审查时悄悄补写。

审查包必须冻结输入，worker 只看冻结包。

## 6. 关键代码路径

- [`src/plb/commands/stage.py`](../../src/plb/commands/stage.py)
- [`src/plb/commands/review.py`](../../src/plb/commands/review.py)
- [`src/plb/workflow/prompting.py`](../../src/plb/workflow/prompting.py)
- [`domain-model/method.md`](../../domain-model/method.md)
- [`domain-model/validation-rules.md`](../../domain-model/validation-rules.md)

## 7. 测试重点

domain 的测试应该验证：

- stage 顺序不被跳过
- review packet 会携带 prompt bundle
- 通过后的状态才能推进到下一阶段
- 生命周期记录会写入数据库

## 8. 常见误区

- 把 domain 当成 discovery 的重复版
- 在边界未冻结时就开始 state 设计
- 让审查结果停留在上下文里而不是落库

## 9. 进入下一步

domain 通过后，下一步是 state。

state 的任务不是重申 domain，而是把边界翻译成可执行的状态转换。
