# Validation Rules

> 用来判断 `discovery capability map` 能不能进入下一阶段。

## 1. Pass Table

| Check | Look At | Pass When | Fail When |
| --- | --- | --- | --- |
| Source | `analysis` | 每个能力都能追溯到 `feature`，最好还能追到 `page`、`story step`、`gwt` | 没来源、只有推断、只写结论 |
| Coverage | `brief` / `story map` / `page` / `feature` / `gwt` / `relations` | 核心内容都被能力地图接住 | 有核心内容漏掉 |
| Purity | capability name | 是业务动词 + 业务结果 | 是页面标题、按钮、接口、数据库、视觉动作 |
| Lifecycle | capability scope | 单条能力只描述一个阶段 | 一条能力混了注册、报价、收资料、签字等多个阶段 |
| Testability | `GWT` | 每条能力都能写出一个 `Given / When / Then` | 写不出业务例子 |
| Relationship | persona / story / page / feature | 能落回对应角色、旅程、页面、能力 | 落不回去、边界不清 |
| Positive Test Evidence | capability examples | 每条能力都有可执行的正向验证样例 | 只有结论，没有可判定样例 |

## 2. Validation Strategy

Discovery 验证分两层：

1. 正向测试：确认 `discovery capability map` 真的覆盖了 analysis 中的核心业务能力。
2. 负向测试：主动寻找幻觉、重名、页面化、技术化、跨阶段混写、漏项和同词异义。

LLM 审查时必须同时执行两层验证。只做正向通过，不算通过。

验证必须遵循顺序：
1. 先看证据
2. 再看结构
3. 再做反例攻击
4. 最后才决定回退或通过

任何一步不能明确说明，都视为未通过。

## 3. Positive Test Matrix

| Signal | Good Example | Why It Passes |
| --- | --- | --- |
| 单一能力 | `客户基础信息采集` 只描述采集注册所需信息 | 一个能力只覆盖一段清晰动作 |
| 清楚证据链 | 能直接追到 `feature`、`page`、`gwt` | 不是凭空归纳出来的 |
| BDD 可写 | “Given 客户已打开邀请页…” | 能转成业务例子 |
| 命名纯净 | `资料完整性核验` 而不是 `ReviewPage` | 用业务动词和业务结果命名 |
| 生命周期单一 | `邀请信任入口` 不混入报价或建档 | 一条能力只管一个阶段 |
| 关系可回指 | 能落回 persona / story / page / feature | 不是孤立名词 |

## 4. Negative Test Matrix

| Failure Mode | Bad Example | Why It Fails |
| --- | --- | --- |
| 页面化命名 | `ClientRegistrationPage` 作为 capability | 这是页面，不是能力 |
| 按钮化命名 | `SubmitButtonClick` 作为 capability | 这是交互动作，不是业务能力 |
| 技术化命名 | `POST /invite/verify` 作为 capability | 这是接口，不是能力 |
| 生命周期混写 | 一个能力同时包含注册、报价、收资料 | 把多个阶段糊成一条 |
| 纯推断 | 没有 feature / page / gwt 佐证 | 没有证据链 |
| 同词异义未拆 | `客户确认` 同时指报价确认和资料确认 | 术语歧义没解决 |
| 过度合并 | `客户全流程管理` 试图包住所有行为 | 失去可验证颗粒度 |
| 过度拆分 | `点击邀请码验证按钮` 和 `提交邀请码` 被拆成两个能力 | 把交互碎片误当业务能力 |

## 5. Go Rules

- 至少有一个 `feature` 佐证
- 最好同时有 `page`、`story step`、`gwt` 佐证
- 来源必须明确写出
- 不允许 UI 化或技术化命名
- 不允许跨阶段混写
- 不允许把页面标题直接提升为能力
- 不允许把接口、按钮、表单、数据库表名直接提升为能力
- 不允许基于“相似”而不基于“证据”合并
- 能力地图要能被写成业务例子
- 每条能力都能给出至少一个正向测试和一个负向测试

## 6. LLM Review Questions

审查能力地图时，LLM 必须逐项回答：

1. 这个能力对应哪条已存在的 feature？
2. 这个能力是否只是页面或按钮的改名？
3. 这个能力是否混入了多个生命周期阶段？
4. 这个能力是否能写出一个最小 BDD 例子？
5. 这个能力为什么不能和另一个相近能力合并？
6. 如果把页面名删掉，这个能力是否还成立？
7. 如果把技术词删掉，这个能力是否还能成立？
8. 这个能力的证据链是否完整？
9. 这个能力是否存在同词异义？
10. 是否能构造一个反例直接击穿它？

如果任一问题无法被明确回答，就视为不通过。

## 7. No-Go Rules

出现以下任一情况，直接回退：

- 证据不足
- 覆盖不足
- 纯度不足
- 例子不足
- 边界不清
- 不能构造可执行反例
- 不能明确说明回退点
- 反例攻击一击即破
