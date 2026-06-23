# Checklist

> 用来快速检查 `state machine map` 和 `state-machine validation report` 是否完成。

## 1. Read

- [ ] 已读取 `discovery capability map`
- [ ] 已读取 `domain model map`
- [ ] 已冻结已批准的上游输入 inventory
- [ ] 已读取辅助证据中的 `story maps`
- [ ] 已读取辅助证据中的 `features`
- [ ] 已读取辅助证据中的 `gwt`

## 2. Build

- [ ] 已选择关键业务流程
- [ ] 每个状态机都有明确业务目标
- [ ] 已识别 states
- [ ] 已识别 events
- [ ] 已识别 guards
- [ ] 已识别 transitions
- [ ] 已识别 terminal states
- [ ] 已定义进入条件和退出条件
- [ ] 已绑定 capabilities
- [ ] 已绑定 domain objects
- [ ] 已对上游输入逐项对账
- [ ] 辅助证据只用于核验，不用于重新抽象

## 3. Validate

- [ ] 每个状态都有业务语义
- [ ] 每个事件都有业务事实
- [ ] 每个守卫都明确
- [ ] 每个终态都成立
- [ ] 没有页面化命名
- [ ] 没有技术化命名
- [ ] 没有 UI 状态混入业务状态
- [ ] 没有跨流程混写
- [ ] 正向测试通过
- [ ] 负向测试通过
- [ ] 至少 3 个反例已被主动构造并击穿
- [ ] LLM 能明确说出回退点
- [ ] 没有把辅助证据当成新的主输入

## 4. Decide

- [ ] `state machine map` 已通过
- [ ] 否则回退到 `domain model map` 或流程拆分
