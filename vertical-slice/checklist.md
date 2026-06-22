# Checklist

> 用来快速检查 `vertical slice map` 和 `vertical-slice validation report` 是否完成。

## 1. Read

- [ ] 已读取 `api contract map`
- [ ] 已读取 `api-contract validation report`
- [ ] 已读取 `design system map`
- [ ] 已读取 `design-system validation report`
- [ ] 已读取 `state machine map`
- [ ] 已读取辅助证据中的 `domain model map`
- [ ] 已读取辅助证据中的 `discovery capability map`

## 2. Build

- [ ] 已选择单一业务能力切片
- [ ] 已定义 route
- [ ] 已定义 page
- [ ] 已定义 feature modules
- [ ] 已定义 hooks
- [ ] 已定义 services
- [ ] 已定义 repositories
- [ ] 已定义 mocks
- [ ] 已定义 state wiring rules
- [ ] 已定义错误处理规则
- [ ] 已定义 loading / empty / success / error 流程
- [ ] 已定义验收条件
- [ ] 辅助证据只用于核验，不用于重新抽象

## 3. Validate

- [ ] 每个切片都能回指 capability
- [ ] 每个切片都能回指 api contract
- [ ] 每个切片都能回指 design system component
- [ ] 没有页面壳
- [ ] 没有接口直连散落在组件里
- [ ] 没有状态绕过
- [ ] 没有设计失配
- [ ] mock/real 同构
- [ ] 正向测试通过
- [ ] 负向测试通过
- [ ] 至少 3 个反例已被主动构造并击穿
- [ ] LLM 能明确说出回退点
- [ ] 没有把辅助证据当成新的主输入

## 4. Decide

- [ ] `vertical slice map` 已通过
- [ ] 否则回退到 `api contract map` 或切片重切

