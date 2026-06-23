# Checklist

> 用来快速检查 `design system map` 和 `design-system validation report` 是否完成。

## 1. Read

- [ ] 已读取 `api contract map`
- [ ] 已读取 `api-contract validation report`
- [ ] 已冻结已批准的上游输入 inventory
- [ ] 已读取辅助证据中的 `state machine map`
- [ ] 已读取辅助证据中的 `domain model map`
- [ ] 已读取辅助证据中的 `discovery capability map`

## 2. Build

- [ ] 已定义 design system 目标和范围
- [ ] 已定义 tokens
- [ ] 已定义语义色彩
- [ ] 已定义排版体系
- [ ] 已定义布局规则
- [ ] 已定义动效规则
- [ ] 已定义组件库
- [ ] 已定义组件状态
- [ ] 已定义无障碍规则
- [ ] 已定义响应式规则
- [ ] 已定义使用规范
- [ ] 已对上游输入逐项对账
- [ ] 辅助证据只用于核验，不用于重新抽象

## 3. Validate

- [ ] 每个 token 都有明确语义
- [ ] 每个 component 都可复用或有明确边界
- [ ] 每个 component 都有状态矩阵
- [ ] 没有页面化 token
- [ ] 没有一次性组件
- [ ] 没有状态缺失
- [ ] 没有语义冲突
- [ ] 无障碍规则成立
- [ ] 响应式规则成立
- [ ] 动效规则有必要
- [ ] 正向测试通过
- [ ] 负向测试通过
- [ ] 至少 3 个反例已被主动构造并击穿
- [ ] LLM 能明确说出回退点
- [ ] 没有把辅助证据当成新的主输入

## 4. Decide

- [ ] `design system map` 已通过
- [ ] 否则回退到 `api contract map` 或组件重切
