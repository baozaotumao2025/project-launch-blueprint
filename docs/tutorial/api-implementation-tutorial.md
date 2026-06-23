# API Implementation Tutorial

> 目标：讲清 API 阶段如何把 domain 和 state 的约束转成稳定的契约层。

## 1. API 的职责

API 阶段不是“把接口先写出来再说”，而是把已经批准的业务边界、状态机和输出规则，整理成可执行的契约。

它关心的是：

- 接口形状
- 输入输出字段
- 契约稳定性
- 校验规则
- 与 state 的兼容性

## 2. 它依赖什么

API 阶段应该建立在：

- 已批准的 discovery
- 已批准的 domain
- 已批准的 state
- `api-contract/` 目录下的方法论文件

如果上游边界没定，API 很容易变成和业务语义脱节的空接口。

## 3. 当前实现怎么工作

API 阶段仍然遵循统一的 stage / review 节奏：

- `plan` 冻结契约目标
- `status` 查看契约进度
- `review packet` 固定约束和上下游输入
- `review run` 交给隔离 worker
- `review record` / `approve` / `reject` 写回数据库
- `next` 推进到 design

它与 discovery 的一致性在于：流程相同，换的是审查目标和 stage 文档。

## 4. 产物长什么样

API 阶段通常应该形成：

- 接口定义
- 字段约束
- 校验规则
- 错误语义
- 与 state 一致的契约说明

## 5. 为什么要和 state 一起看

API 并不是独立存在的。

如果 state 里没有明确的生命周期，API 很容易出现：

- 状态字段不稳定
- 错误码和状态含义对不上
- 业务流程无法在接口层表达

所以 API review 其实是在确认“契约有没有忠实表达上游语义”。

## 6. 关键代码路径

- [`src/plb/commands/stage.py`](../../src/plb/commands/stage.py)
- [`src/plb/commands/review.py`](../../src/plb/commands/review.py)
- [`src/plb/workflow/prompting.py`](../../src/plb/workflow/prompting.py)
- [`api-contract/method.md`](../../api-contract/method.md)
- [`api-contract/validation-rules.md`](../../api-contract/validation-rules.md)

## 7. 测试重点

API 的测试应该验证：

- stage 顺序受控
- prompt bundle 会把契约文件带入审查
- review 结果会进入持久化状态
- 通过前不能进入 design

## 8. 常见误区

- 把 API 当成和业务边界无关的接口草稿
- 忽略 state 约束
- 让接口设计先于业务语义冻结

## 9. 进入下一步

API 通过后，下一步是 design。

design 会把契约转成可实现的系统表达方式。
