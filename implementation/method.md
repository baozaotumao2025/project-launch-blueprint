# Implementation Bridge Method

> 用已验证的蓝图产物生成真实代码落地计划和实现路径的执行协议。

## 1. Goal

把已经通过验证的蓝图产物，翻译成可以直接在代码仓库中执行的实现计划、目录骨架、任务拆分和验证步骤。  
如果外部传入的是一个 `Codex goal`，就先把这个 goal 冻结成实现范围，再继续生成原型代码所需的骨架和验证动作。

## 2. Inputs

- 主输入：
  - `Codex goal`
  - `quality-gates validation report`
  - `vertical slice map`
  - `api contract map`
  - `design system map`
  - `state machine map`
  - `domain model map`
  - `discovery capability map`
- 辅助证据：
- `technical-solution.md`
- 当前代码仓库结构
- 现有 `analysis` 中的项目约束说明
- `../cli-architecture.md`
- `../workflow-state.md`
- 冻结后的上游输入 inventory / coverage matrix

## 2.1 Input Rules

- `Codex goal` 是入口级输入，用来决定这次实现到底要生成什么。
- `quality-gates validation report` 是最高优先级输入，表示哪些内容已经可以进入实现。
- 已批准的上游输入必须先冻结成 inventory / coverage matrix，不能在实现时临时补写。
- 上游已经验证过的能力、边界、状态、契约和组件，不得在本层重新抽象成新的业务概念。
- 辅助证据只允许用于工程约束、目录约束和实现约束，不得提升为新的业务语义。
- 如果上游仍有未通过项，本层只能停在实现计划，不得把未验证内容直接写进代码。

## 3. Output

- implementation plan
- goal breakdown / goal registry
- code scaffold map
- task batch list
- branch / commit plan
- verification plan
- implementation handoff report

## 4. Workflow

| Step | Input | Action | Output | Can Roll Back |
| --- | --- | --- | --- | --- |
| Read | Codex goal + 全部主输入 | 读取已验证产物，确认这次要生成什么 | 输入摘要 | Yes |
| Freeze Scope | goal + quality gates + vertical slice | 冻结当前可实现范围，标出未通过项 | implementation scope | Yes |
| Break Down Goals | frozen scope | 把本次实现按并列语义和实现层级拆成可追踪的 goal registry，标出总数、顺序和依赖 | goal registry | Yes |
| Map Artifacts | 上游产物 | 把能力、对象、状态、契约、组件和切片映射到代码目录 | code scaffold map | Yes |
| Scaffold | code scaffold map | 创建目录、文件、入口、类型和测试骨架 | scaffold plan | Yes |
| Implement | scaffold plan | 按垂直切片实现 hook / service / repository / component / page / mock | implementation tasks | Yes |
| Wire Validation | implementation tasks + goal registry | 补 schema、测试、错误处理、状态流和验收项 | verification plan | Yes |
| Review Counterexamples | verification plan | 用反例检查是否重新发明语义、越界实现或跳过验证 | review notes | Yes |
| Decide | implementation handoff report | 通过则进入编码提交，不通过则回退到最相关上游层 | go / no-go | Yes |

## 5. Core Rules

- 先把 goal 冻结成 scope，再开始生成代码骨架。
- 一个 goal registry 里必须能看清楚总共有多少个 goal、当前执行到哪一个、每个 goal 的依赖是什么。
- goal 的数量可以随 `Codex goal` 的复杂度变化，但必须保持稳定、可追踪、可回归。
- 只翻译已验证语义，不重建业务语义。
- 先 scaffold，再实现，再补验证，不允许先写散点代码再补结构。
- 代码边界必须服从上游边界，不能为了“写起来方便”打穿层级。
- `schema`、`repository`、`service`、`hook`、`component` 和 `page` 必须职责分离。
- 如果某项上游仍未通过，本层只允许停在计划或骨架，不允许假装完成。
- 所有实现都必须能回指到至少一个上游验证产物。
- 生成结果必须可以直接被 LLM 或人类按任务批次执行，不得只给概念性建议。
- 每完成一个 goal，都必须先跑回归验证，再允许进入下一个 goal。

## 6. Design Heuristics

### 6.1 先骨架，再行为

目录、文件、入口和测试壳先稳定，行为实现再填进去。

### 6.2 先边界，再技术

先确定每个文件属于哪一层，再决定用什么技术实现它。

### 6.3 先可验证，再可运行

不能被测试或检查确认的代码，不算真正完成。

### 6.4 先切片，再扩展

优先完成一个能力的闭环，再复制到其他能力。

### 6.5 先问反例，再提提交

如果一个实现只能通过正向路径而不能承受失败输入，就不能进入提交。

## 7. Execution Order

1. `index.md`
2. `artifact-map.md`
3. `bootstrap.md`
4. `checklist.md`
