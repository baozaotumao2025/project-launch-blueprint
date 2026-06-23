# Validation Rules

> 用来判断 `quality gate map` 能不能进入下一阶段。

## 1. Validation Strategy

质量门禁验证分两层：

1. 正向测试：确认门禁确实覆盖了发布所需的风险、测试、回退和观测要求。
2. 负向测试：主动寻找假绿灯、单一测试替代全部风险、回退不可执行、观测不足和人工拍脑袋放行。

辅助证据只能用来核验和补漏，不能把它们再次抽象成新的主流程。

`upstream input inventory` 必须覆盖所有已批准的上游阶段输入，并在 `coverage matrix` 中逐项对账，不能漏记、重记或临时补写。

LLM 审查时必须同时执行两层验证。只做正向通过，不算通过。

验证必须遵循顺序：
1. 先看来源
2. 再看风险分层
3. 再看测试金字塔和观测要求
4. 再看回退
5. 最后决定回退或通过

任何一步不能明确说明，都视为未通过。

## 2. Pass Table

| Check | Look At | Pass When | Fail When |
| --- | --- | --- | --- |
| Traceability | all upstream validation reports | 每个门槛都能回指具体阶段风险 | 只有抽象结论，没有来源 |
| Upstream Input Coverage | `upstream input inventory` / `coverage matrix` | 每个已批准上游输入都被显式对账 | 有上游输入未进入 inventory 或 coverage |
| Risk Coverage | risk register | 高风险、高影响、高回退成本都被覆盖 | 关键风险没门槛 |
| Test Pyramid Balance | test matrix | 单元、集成、契约、端到端各有职责 | 所有风险都压到一种测试上 |
| Observability Fit | observability requirements | 有日志、指标、追踪、告警和健康检查要求 | 只能靠人工盯着看 |
| Rollback Fit | rollback plan | 回滚、降级、修复、重放路径明确 | 失败后不知道怎么退 |
| Release Criteria Clarity | release criteria | 放行条件可判定、可执行 | 只能说“差不多可以” |

## 3. Positive Test Matrix

| Signal | Good Example | Why It Passes |
| --- | --- | --- |
| 风险分层 | 支付/权限/数据丢失类门槛比视觉文案更严格 | 风险优先 |
| 测试分层 | 单元测规则、契约测接口、E2E测主路径 | 各层承担不同风险 |
| 观测充分 | 有错误码、日志、指标、追踪和告警 | 能定位与恢复 |
| 回退明确 | 灰度失败可回滚到前一版本 | 失败可控 |
| 放行条件清晰 | “通过全部契约测试且 0 阻断缺陷” | 可判定 |

## 4. Negative Test Matrix

| Failure Mode | Bad Example | Why It Fails |
| --- | --- | --- |
| 假绿灯 | 只有人工看一眼就说可以发 | 不可重复、不可审计 |
| 单测万能 | 只有单元测试，没有契约和 E2E | 风险覆盖不完整 |
| 回退缺失 | 出问题后“再说” | 发布不可控 |
| 观测缺失 | 没有日志/指标/追踪 | 出问题无法定位 |
| 风险漏项 | 权限和数据一致性没门槛 | 高风险未覆盖 |
| 只看代码 | 不看运行行为和用户路径 | 不能代表可发布 |
| 纯推断 | 没有上游证据，只靠经验 | 没有证据链 |

## 5. LLM Review Questions

审查质量门禁时，LLM 必须逐项回答：

1. 这个门槛对应哪类风险？
2. 这个风险来源于哪一层的验证结果？
3. 这个门槛是否只是人工印象？
4. 测试金字塔是否平衡？
5. 观测要求是否足够？
6. 回退方案是否可执行？
7. release criteria 是否可判定？
8. 这份输出是否符合 `output-schema.md`？
9. 你能否构造一个最小反例直接击穿它？
10. 如果去掉人工参与，这套门禁是否还成立？
11. 哪个门槛最容易被误判为“已经覆盖”，为什么？

如果任一问题无法被明确回答，就视为不通过。

## 6. Go Rules

- 至少有一条来自每个上游阶段 validation report 的风险佐证。
- 至少有一条来自已批准上游输入的输入佐证。
- 每个高风险项都要有明确门槛。
- 每个门槛都要有对应测试或观测要求。
- 每个发布动作都要有回退方案。
- release criteria 必须可判定、可执行。

## 7. No-Go Rules

出现以下任一情况，直接回退：

- 风险覆盖不全
- 测试层级失衡
- 观测要求不足
- 回退方案不可执行
- release criteria 不可判定
- 假绿灯
- 只能人工拍脑袋
- 不能构造可执行反例
- 不能明确说明回退点
- 辅助证据被当成了新的主分析对象
