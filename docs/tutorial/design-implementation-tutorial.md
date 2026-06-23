# Design Implementation Tutorial

> 目标：讲清 design 阶段如何把 API 契约转成可复用的设计系统约束。

## 1. Design 的职责

design 阶段关心的不是“做漂亮一点”，而是“做成统一、可复用、可实现的系统规则”。

它要收敛的是：

- 设计系统约定
- 组件边界
- 样式和交互规则
- 与 API 一致的表达方式

## 2. 它依赖什么

design 阶段应该建立在：

- 已批准的 API
- 已批准的 state
- 已批准的 domain
- `design-system/` 目录下的方法论文件

如果 API 没冻结，design 很容易被反复改写。

## 3. 当前实现怎么工作

design 仍然使用同一套 stage 流程：

- `plan`
- `status`
- `review packet`
- `review run`
- `review record`
- `approve` / `reject`
- `next`

审查依然走隔离 worker，只有输入不同：

- 上游是 API 和 state
- stage 文档是 design system 文件
- 审查重点是系统表达是否和契约一致

## 4. 产物长什么样

design 阶段通常应该形成：

- 设计系统规则
- 组件约束
- 视觉表达原则
- 交互一致性要求
- 给 slice 阶段的实现前提

## 5. 为什么 design 是 slice 前的闸门

design 不先稳住，slice 会直接进入“边实现边定设计”的混乱状态。

所以 design 的作用是：

- 先冻结系统表达
- 再允许垂直切片把表达落进代码

## 6. 关键代码路径

- [`src/plb/commands/stage.py`](../../src/plb/commands/stage.py)
- [`src/plb/commands/review.py`](../../src/plb/commands/review.py)
- [`src/plb/workflow/prompting.py`](../../src/plb/workflow/prompting.py)
- [`design-system/method.md`](../../design-system/method.md)
- [`design-system/checklist.md`](../../design-system/checklist.md)

## 7. 测试重点

design 的测试应该验证：

- 审查包包含 design system 文档
- review 仍然是 isolated worker
- 通过后才能推进到 slice
- 生命周期记录能正确反映设计阶段

## 8. 常见误区

- 把 design 当成纯视觉工作
- 让设计规则和 API 契约脱钩
- 在系统规则未冻结时就做实现切片

## 9. 进入下一步

design 通过后，下一步是 slice。

slice 会把设计和契约装配成跨层实现单元。
