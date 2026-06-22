# Bootstrap Plan

> 这份文件专门回答：拿到蓝图以后，真实仓库应该按什么顺序开工。
> 如果你要用 `Codex goal` 一键生成原型代码，这里就是最小启动顺序。

## 1. Recommended Order

1. 冻结 `goal` 和范围
2. 拆出 `goal registry`
3. 生成目录骨架
4. 生成 bootstrap manifest
5. 落 `schemas`
6. 落 `api` / `repository`
7. 落 `service`
8. 落 `hook`
9. 落 `component` / `page`
10. 接 `MSW`
11. 接测试
12. 对每个 goal 跑回归
13. 接真实后端

## 2. Why This Order

- 先冻结范围，避免实现过程中重新开题
- 先拆 goal registry，避免后面不知道当前完成了几个 goal
- 先落 schema 和契约，避免前后端各写一套结构
- 先落边界层，再落 UI 层，避免组件直接吃原始数据
- 先接 mock，再接真实后端，避免早期被外部依赖卡住
- 每个 goal 后跑回归，避免新改动破坏旧能力
- 先补测试，再放行发布，避免“能跑但不能交付”

## 3. Branch / Commit Guidance

- 一个能力切片尽量对应一个分支或一组连续提交
- 一个提交只引入一类变化：骨架、契约、行为、UI、测试、集成
- 不要把大改和验证改混在同一个提交里

## 4. Handoff Rule

如果某个上游阶段还没通过，不要启动对应实现，只能先准备目录、注释和待办。  
如果 `goal` 不清晰，也不要开始生成原型代码，先把 goal 改写成可执行范围。

## 5. Good Start Shape

最稳的起步方式是：

- 先实现一个最小 vertical slice
- 再验证 mock / real 同构
- 再复制到其他能力
