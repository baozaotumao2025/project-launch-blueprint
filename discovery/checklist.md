# Checklist

> 用来快速检查 `discovery capability map` 和 `discovery validation report` 是否完成。

## 1. Read

- [ ] `analysis/brief.md`
- [ ] `analysis/story-maps/*.md`
- [ ] `analysis/pages/*.md`
- [ ] `analysis/features/index.md`
- [ ] `analysis/gwt/*.feature`
- [ ] `analysis/relations/*.md`

## 2. Build

- [ ] 已归并能力候选
- [ ] 每条能力有来源
- [ ] 每条能力有 actor
- [ ] 每条能力有 outcome
- [ ] 没有 UI 化描述
- [ ] 没有技术化描述
- [ ] 没有跨阶段混写

## 3. Validate

- [ ] 核心 feature 全覆盖
- [ ] 核心 page 全覆盖
- [ ] 关键 story step 全覆盖
- [ ] 关键 GWT 例子全覆盖
- [ ] 关系矩阵无明显漏项
- [ ] 幻觉和重名已审查
- [ ] 正向测试通过
- [ ] 负向测试通过
- [ ] 至少 3 个反例已被主动构造并击穿
- [ ] LLM 能明确说出回退点
- [ ] 同词异义已显式处理

## 4. Decide

- [ ] `discovery capability map` 已通过
- [ ] 否则回退到 `analysis`
