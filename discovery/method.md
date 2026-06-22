# Discovery Method

> 用 `analysis` 生成能力地图的执行协议。

## 1. Goal

把 `analysis` 里的现成工件，规范化汇总成可验证的 `discovery capability map`。

## 2. Inputs

- `analysis/brief.md`
- `analysis/story-maps/*.md`
- `analysis/pages/*.md`
- `analysis/features/index.md`
- `analysis/gwt/*.feature`
- `analysis/relations/*.md`

## 3. Output

- discovery capability map
- discovery validation report

> 其中 `discovery capability map` 内部包含每条能力的 evidence、positive_tests、negative_tests、rollback_point 和 assumptions。

## 4. Workflow

| Step | Input | Action | Output | Can Roll Back |
| --- | --- | --- | --- | --- |
| Collect | `analysis` 全量工件 | 收集已有结构化信息 | 原始材料清单 | Yes |
| Extract | `brief` / `story-maps` / `pages` / `features` / `gwt` / `relations` | 分别提取目标、阶段、职责、候选能力、例子、覆盖关系 | 提取片段 | Yes |
| Merge | 提取片段 | 合并语义一致内容，去重，拆分多阶段内容 | capability 候选 | Yes |
| Attach Evidence | capability 候选 | 补齐 actor、trigger、input、outcome、lifecycle_stage 等字段 | 带证据的 capability | Yes |
| Counterexample Sweep | 带证据的 capability | 用反例攻击候选能力，查页面化、技术化、混阶段、漏项、同词异义 | 反例审查记录 | Yes |
| Validate | 带证据的 capability | 用 `validation-rules.md` 检查来源、覆盖、纯度、生命周期、可测试性、关系 | discovery validation report | Yes |
| Decide | discovery validation report | 通过则进入下一阶段，不通过则回退 | go / no-go | Yes |

## 5. Rules

- 一个业务动作只保留一个主名称
- 页面标题不等于能力
- 技术动作不进入能力地图
- 多阶段内容要拆开
- 同词异义必须显式拆分或标注
- 只是“看起来相关”不能作为合并依据
- 不通过就回退到 `analysis` 补齐或重写

## 6. Design Heuristics

### 6.1 先看证据，再看命名

如果一个候选能力找不到至少一条清晰证据链，就不应进入输出。

### 6.2 先看生命周期，再看相似度

相似的页面、相似的按钮、相似的描述，不代表同一个能力。

### 6.3 先看反例，再信合并

能通过反例攻击的合并，才算合并；否则只是把噪音压缩成了更大的噪音。

## 7. Execution Order

1. `../index.md`
2. `method.md`
3. `validation-rules.md`
4. `prompt-templates.md`
5. `output-schema.md`
6. `checklist.md`
