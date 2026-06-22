# Checklist

> 用来快速检查实现桥是否已经可以进入真实编码。

## 1. Read

- [ ] 已读取 `cli-architecture.md`
- [ ] 已读取 `workflow-state.md`
- [ ] 已读取 `Codex goal`
- [ ] 已读取 `discovery capability map`
- [ ] 已读取 `domain model map`
- [ ] 已读取 `state machine map`
- [ ] 已读取 `api contract map`
- [ ] 已读取 `design system map`
- [ ] 已读取 `vertical slice map`
- [ ] 已读取 `quality-gates validation report`
- [ ] 已读取 `technical-solution.md`
- [ ] 已读取 `commands.md`
- [ ] 已读取 `validation-rules.md`
- [ ] 已读取 `output-schema.md`
- [ ] 已读取 `prompt-templates.md`
- [ ] 已读取 `example-output.md`

## 2. Build

- [ ] 已把 goal 冻结成实现范围
- [ ] 已拆出 goal registry
- [ ] 已标明 goal 总数、顺序和依赖
- [ ] 已生成目录骨架
- [ ] 已生成 directory tree
- [ ] 已生成 bootstrap manifest
- [ ] 已生成 schema / type 骨架
- [ ] 已生成 repository / service / hook / component / page 骨架
- [ ] 已生成测试骨架
- [ ] 已明确 mock / real 切换方式
- [ ] 已明确分支和提交策略
- [ ] 已定义每个 goal 完成后的回归范围

## 3. Validate

- [ ] 没有把未通过的上游内容直接写进实现
- [ ] 没有重建新的业务语义
- [ ] 没有打穿层级边界
- [ ] schema 在边界层校验
- [ ] service 不直接操作 UI
- [ ] component 不直接发请求
- [ ] mock 和 real 同构
- [ ] 每个 goal 完成后都跑了回归验证
- [ ] 至少能跑通一个最小 vertical slice
- [ ] 反例能击穿错误实现

## 4. Decide

- [ ] 可以进入真实编码
- [ ] 否则回退到最相关上游层
