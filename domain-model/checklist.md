# Checklist

> 用来快速检查 `domain model map` 和 `domain-model validation report` 是否完成。

## 1. Read

- [ ] 已读取 `discovery capability map`
- [ ] 已读取 `discovery validation report`
- [ ] 已读取辅助证据中的 persona / story map / feature / relations
- [ ] `domain_input_inventory` 已生成且逐项对账
- [ ] inventory 中没有未覆盖或未显式排除的输入

## 2. Build

- [ ] 已划分 bounded contexts
- [ ] 每个 context 都有稳定业务语言
- [ ] 已识别 aggregates
- [ ] 每个 aggregate 都有 root entity
- [ ] 已识别 entities
- [ ] 已识别 value objects
- [ ] 已识别 domain services
- [ ] 已识别 domain events
- [ ] 已定义 context map
- [ ] 已定义不变量和所有权
- [ ] 辅助证据只用于核验，不用于重新抽象
- [ ] 覆盖矩阵已生成，且每个输入只有一条记录

## 3. Validate

- [ ] 每个 context 都能回指 capability
- [ ] 每个 aggregate 都有不变量
- [ ] 没有页面化命名
- [ ] 没有技术化命名
- [ ] 没有跨阶段混写
- [ ] 没有贫血模型倾向
- [ ] 正向测试通过
- [ ] 负向测试通过
- [ ] 至少 3 个反例已被主动构造并击穿
- [ ] LLM 能明确说出回退点
- [ ] 关键歧义已拆解
- [ ] 没有把辅助证据当成新的主输入
- [ ] 无未对账输入

## 4. Decide

- [ ] `domain model map` 已通过
- [ ] 否则回退到 `discovery capability map` 重切
