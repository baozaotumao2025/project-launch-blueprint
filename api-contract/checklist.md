# Checklist

> 用来快速检查 `api contract map` 和 `api-contract validation report` 是否完成。

## 1. Read

- [ ] 已读取 `discovery capability map`
- [ ] 已读取 `discovery validation report`
- [ ] 已读取 `domain model map`
- [ ] 已读取 `state machine map`
- [ ] 已冻结已批准的上游输入 inventory
- [ ] 已读取辅助证据中的 story maps / features / gwt / relations

## 2. Build

- [ ] 已选择需要对外暴露的能力
- [ ] 每个契约都有明确业务目标
- [ ] 已识别 endpoint
- [ ] 已识别 method
- [ ] 已识别 request
- [ ] 已识别 response
- [ ] 已识别 response status / headers / content-type
- [ ] 已识别 errors
- [ ] 已识别 auth rules
- [ ] 已识别 idempotency rules
- [ ] 已识别 pagination / filtering / sorting
- [ ] 已识别 versioning / compatibility / deprecation
- [ ] 已绑定 capabilities
- [ ] 已绑定 domain objects
- [ ] 已绑定 state machine 阶段
- [ ] 已对上游输入逐项对账
- [ ] 辅助证据只用于核验，不用于重新抽象

## 3. Validate

- [ ] 每个契约都有业务语义
- [ ] 每个 endpoint / method 都合理
- [ ] 每个 request / response 都不过度暴露内部结构
- [ ] 每个 response 都有明确 status / headers / content-type
- [ ] 每个 error 都可区分
- [ ] 每个 mutating endpoint 都有幂等策略或明确无需幂等理由
- [ ] 每个契约都有 versioning / compatibility / deprecation 说明
- [ ] 没有页面化命名
- [ ] 没有技术化命名
- [ ] 没有把 UI 状态直接翻译成契约
- [ ] 没有绕过状态机
- [ ] 没有跨边界混写
- [ ] 正向测试通过
- [ ] 负向测试通过
- [ ] 至少 3 个反例已被主动构造并击穿
- [ ] LLM 能明确说出回退点
- [ ] 没有把辅助证据当成新的主输入

## 4. Decide

- [ ] `api contract map` 已通过
- [ ] 否则回退到 `state machine map` 或契约重切
