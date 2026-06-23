# Slice Implementation Tutorial

> 目标：讲清 slice 阶段如何把 domain、state、API 和 design 组合成垂直切片的实现顺序。

## 1. Slice 的职责

slice 阶段不再只看单层抽象，而是开始把多层成果装配成一个能落地的纵向单元。

它关心的是：

- 哪些功能要一起实现
- 哪些层要按什么顺序落地
- 哪些文件和目录会一起变化
- 这些变化如何形成可交付的垂直切片

## 2. 它依赖什么

slice 阶段应该建立在：

- 已批准的 domain
- 已批准的 state
- 已批准的 API
- 已批准的 design
- `vertical-slice/` 目录的方法论文件

如果上游没有冻结，slice 就会变成“什么都想带一点”的拼盘。

## 3. 当前实现怎么工作

slice 和前面的阶段一样，使用统一流程：

- `plan`
- `status`
- `review packet`
- `review run`
- `review record`
- `approve` / `reject`
- `next`

它的 review 重心是：

- 垂直切片是否覆盖了上游约束
- 实现顺序是否合理
- 代码和测试是否能按切片推进

## 4. 产物长什么样

slice 阶段通常应该形成：

- 切片拆分顺序
- 目录和文件计划
- 业务功能与实现层的映射
- 后续 implementation goal registry 的基础

## 5. 为什么 slice 很重要

slice 是从“讨论协议”走向“工程执行”的临界点。

如果它做不好，implementation 会出现：

- 目录混乱
- 任务顺序混乱
- 跨层依赖无法收口

## 6. 关键代码路径

- [`src/plb/commands/stage.py`](../../src/plb/commands/stage.py)
- [`src/plb/commands/review.py`](../../src/plb/commands/review.py)
- [`src/plb/workflow/prompting.py`](../../src/plb/workflow/prompting.py)
- [`vertical-slice/method.md`](../../vertical-slice/method.md)
- [`vertical-slice/output-schema.md`](../../vertical-slice/output-schema.md)

## 7. 测试重点

slice 的测试应该验证：

- 仍然遵循同一套 stage / review 节奏
- 审查包带着垂直切片约束
- 通过后才能进入 gates
- 生命周期能反映 slice 的阶段推进

## 8. 常见误区

- 把 slice 当成单一层的任务
- 忽略跨层依赖
- 在设计未冻结时就分片实现

## 9. 进入下一步

slice 通过后，下一步是 gates。

gates 会做最后一轮放行判断。
