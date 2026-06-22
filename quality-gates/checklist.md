# Checklist

> 用来快速检查 `quality gate map` 和 `quality-gates validation report` 是否完成。

## 1. Read

- [ ] 已读取 `discovery capability map`
- [ ] 已读取 `discovery validation report`
- [ ] 已读取 `domain model map`
- [ ] 已读取 `domain-model validation report`
- [ ] 已读取 `state machine map`
- [ ] 已读取 `state-machine validation report`
- [ ] 已读取 `api contract map`
- [ ] 已读取 `api-contract validation report`
- [ ] 已读取 `design system map`
- [ ] 已读取 `design-system validation report`
- [ ] 已读取 `vertical slice map`
- [ ] 已读取 `vertical-slice validation report`
- [ ] 已读取辅助证据中的 `analysis`

## 2. Build

- [ ] 已分类风险
- [ ] 已建立门槛
- [ ] 已建立测试矩阵
- [ ] 已定义可观测性要求
- [ ] 已定义回退方案
- [ ] 已定义部署前检查项
- [ ] 已定义发布动作
- [ ] 辅助证据只用于核验，不用于重新抽象

## 3. Validate

- [ ] 每个高风险项都有门槛
- [ ] 单元/集成/契约/E2E 测试职责清楚
- [ ] 可观测性要求清楚
- [ ] 回退方案可执行
- [ ] release criteria 可判定
- [ ] 没有假绿灯
- [ ] 没有单测万能
- [ ] 没有回退缺失
- [ ] 没有观测缺失
- [ ] 正向测试通过
- [ ] 负向测试通过
- [ ] 至少 3 个反例已被主动构造并击穿
- [ ] LLM 能明确说出回退点
- [ ] 没有把辅助证据当成新的主输入

## 4. Decide

- [ ] `quality gate map` 已通过
- [ ] 否则回退到最相关阶段重切

