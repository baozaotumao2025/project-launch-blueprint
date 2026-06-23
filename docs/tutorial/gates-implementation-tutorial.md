# Gates Implementation Tutorial

> 目标：讲清 gates 阶段如何成为进入 implementation 前的最后门禁。

## 1. Gates 的职责

gates 阶段不是再写一轮内容，而是做最后确认：

- 上游阶段是否都批准了
- 状态是否稳定
- 风险是否可接受
- implementation 是否可以开始

这一步是整个流程里最像“放行门”的地方。

## 2. 它依赖什么

gates 阶段应该建立在：

- 已批准的 discovery
- 已批准的 domain
- 已批准的 state
- 已批准的 API
- 已批准的 design
- 已批准的 slice
- `quality-gates/` 目录下的方法论文件

如果 gates 没过，implementation 不应该启动。

## 3. 当前实现怎么工作

gates 依然遵循统一的 stage 节奏：

- `plan`
- `status`
- `review packet`
- `review run`
- `review record`
- `approve` / `reject`
- `next`

它的关键不同是：review 关注的是“是否可以进入 implementation”，而不是再定义新的业务语义。

## 4. 产物长什么样

gates 阶段通常应该形成：

- 放行检查清单
- 风险项
- 必要的回退点
- implementation 前置条件

## 5. 为什么 gates 是最后闸门

gates 的意义在于把上游所有决策汇总成一个二元判断：

- 过了，就进 implementation
- 没过，就停在这里修正

这能避免 implementation 变成“边做边找借口”的灰区。

## 6. 关键代码路径

- [`src/plb/commands/stage.py`](../../src/plb/commands/stage.py)
- [`src/plb/commands/review.py`](../../src/plb/commands/review.py)
- [`src/plb/workflow/prompting.py`](../../src/plb/workflow/prompting.py)
- [`quality-gates/method.md`](../../quality-gates/method.md)
- [`quality-gates/checklist.md`](../../quality-gates/checklist.md)

## 7. 测试重点

gates 的测试应该验证：

- 审查仍然走隔离 worker
- 通过前不能进入 implementation
- 生命周期和状态会被落库
- 放行失败时能给出可理解的阻断信号

## 8. 常见误区

- 把 gates 当成一个可以跳过的形式步骤
- 让 implementation 先跑再说
- 把风险检查和业务语义混在一起

## 9. 进入下一步

gates 通过后，下一步才是 implementation。

implementation 会开始把已批准的 stage 产物翻译成真实代码。
