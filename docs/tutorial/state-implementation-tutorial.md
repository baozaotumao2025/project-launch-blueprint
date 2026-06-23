# State Implementation Tutorial

> 目标：讲清 state 阶段如何把 domain 边界转成稳定的状态机、生命周期和回退点。

## 1. State 的职责

state 阶段关心的是：

- 系统有哪些状态
- 状态之间怎么迁移
- 哪些迁移被允许
- 失败时怎么回退
- 哪些状态要长期记录到数据库

它不是业务需求收敛，而是业务运行秩序的定义。

## 2. 它依赖什么

state 阶段应该建立在：

- discovery 已批准
- domain 已批准
- 项目边界和交付物已经明确
- `state-machine/` 目录的 stage 文档已存在

如果 domain 还没定稳，state 只能产生伪状态机。

## 3. 当前实现怎么工作

state 仍然沿用同一条 stage 流程：

- `plan` 冻结状态机目标
- `status` 看当前状态和生命周期
- `review packet` 固化状态机输入
- `review run` 交给隔离 worker 审查
- `review record` / `approve` / `reject` 落库
- `next` 推进到 API

state 的核心实现依赖数据库里的两类记录：

- `StageRecord`
- `StageLifecycleRecord` / `StageLifecycleEvent`

这让 state 不只是一次性生成，而是能被恢复、复查和审计。

## 4. 产物长什么样

state 阶段通常应产出：

- 状态机边界说明
- 状态转移规则
- 回退点
- 失败处理规则
- 供 api 和 design 复用的生命周期术语

## 5. 为什么要强调数据库落库

state 阶段特别需要数据库，因为它一旦出问题，后续阶段会跟着失真。

数据库记录能帮助我们回答：

- 当前状态是什么
- 上一步发生了什么
- 这次变更是 planned 还是 blocked
- 哪个 review verdict 造成了状态变化

## 6. 关键代码路径

- [`src/plb/commands/stage.py`](../../src/plb/commands/stage.py)
- [`src/plb/commands/review.py`](../../src/plb/commands/review.py)
- [`src/plb/state/store.py`](../../src/plb/state/store.py)
- [`state-machine/method.md`](../../state-machine/method.md)
- [`state-machine/output-schema.md`](../../state-machine/output-schema.md)

## 7. 测试重点

state 的测试应该确认：

- 生命周期事件会连续追加
- review 结论能改变状态
- 状态变更可以被 next 检查到
- 错误状态能被标记为 blocked 或 needs_revision

## 8. 常见误区

- 把 state 当成单纯的字段枚举
- 只记录当前状态，不记录演化过程
- 忽略回退点和健康度

## 9. 进入下一步

state 通过后，下一步是 API。

API 会把状态机约束转成对外契约。
