# Command Reference

> 这是一份面向实现的最终命令参考表。  
> 它把 `uv run plb` 的全局入口、阶段命令和 review 命令收敛成一张可实现的清单。  
> 命令顺序必须服务于业务流：安装 -> 初始化 -> 查看契约 -> 定义边界 -> 分类资产 -> 分阶段推进 -> 收尾分享。

## 1. Global Entry

### 1.1 `uv run plb init`

用途：

- 初始化 project space
- 创建 `.project-launch-blueprint/` 运行目录
- 建立 state DB、projections、audits、exports、logs、backups
- 为后续 stage 和 review 流程建立基础状态

参数：

- `--root <path>` / `-C <path>`: explicitly choose the project root
- `--project <project_key>`
- `--name <project_name>`
- `--brief-file <path>`
- `--brief <text>`
- `--force`
- `--dry-run`

状态变化：

- `uninitialized -> initialized`

### 1.2 `uv run plb status`

用途：

- 展示当前项目状态
- 汇总 stage 进度
- 显示当前阻塞点、下一步和最近一次 review 结果
- 用于“查看安装后契约”和“查看当前推进位置”

参数：

- `--root <path>` / `-C <path>`: explicitly choose the project root
- `--project <project_key>`
- `--json`
- `--verbose`

状态变化：

- 无

### 1.3 `uv run plb publish`

用途：

- 打包当前 blueprint
- 导出 skill bundle
- 生成发布清单和分享材料

参数：

- `--project <project_key>`
- `--output <path>`
- `--dry-run`

状态变化：

- `implemented -> published`

## 2. Stage Commands

所有阶段都遵守同一套模式，且必须按顺序推进：

```txt
uv run plb stage <stage_name> plan
uv run plb stage <stage_name> status
uv run plb stage <stage_name> next
uv run plb stage <stage_name> verify
uv run plb stage <stage_name> set <status>
```

### 2.1 Discovery

- `plan`：冻结安装后输入与 project boundary 的 discovery 目标
- `status`：查看 discovery 进度
- `next`：生成 discovery packet，执行 review loop，完成后推进到 domain
- `verify`：只检查 discovery 产物是否可进入 domain
- `set`：手动写入阶段状态，便于推进、阻塞或回退

### 2.2 Domain

- `plan`：基于 approved discovery 冻结 domain 边界和 final deliverables
- `status`：查看 domain revision
- `next`：生成 domain packet，执行 review loop，完成后推进到 state
- `verify`：只检查 domain 是否可进入 state

### 2.3 State

- `plan`：冻结 domain + discovery 的输入范围
- `status`：查看状态机 revision 和回退点
- `next`：生成 state packet，执行 review loop，完成后推进到 api
- `verify`：只检查 state 是否可进入 api

### 2.4 API

- `plan`：冻结 state + domain + discovery 的输入范围
- `status`：查看 API contract revision
- `next`：生成 API packet，执行 review loop，完成后推进到 design
- `verify`：只检查 api 是否可进入 design

### 2.5 Design

- `plan`：冻结 API contract 和 validation report
- `status`：查看 design system revision
- `next`：生成 design packet，执行 review loop，完成后推进到 slice
- `verify`：只检查 design 是否可进入 slice

### 2.6 Slice

- `plan`：冻结 api + design + state
- `status`：查看 vertical slice revision
- `next`：生成 slice packet，执行 review loop，完成后推进到 gates
- `verify`：只检查 slice 是否可进入 gates

### 2.7 Gates

- `plan`：冻结全部已批准上游输出
- `status`：查看 quality gate map 和 readiness
- `next`：生成 gates packet，执行 review loop，完成后推进到 implementation
- `verify`：只检查 gates 是否可进入 implementation

### 2.8 Implementation

- `plan`：冻结 quality-gates 输出，拆 goal registry
- `status`：查看 goal_progress
- `next`：执行当前 goal、跑回归、推进下一 goal
- `verify`：只检查是否可进入真实编码

## 3. Review Commands

### 3.1 `uv run plb review packet`

用途：

- 生成只读审查包
- 固化当前阶段和已批准上游输入
- 为 `review run` 提供冻结输入

参数：

- `--project <project_key>`
- `--stage <stage_name>`
- `--output <path>`

### 3.2 `uv run plb review run`

用途：

- 把 packet 交给 fresh reviewer
- 使用隔离上下文执行审查
- 落盘审查结果
- 这是“真的审查”的一步，不是只看摘要

参数：

- `--project <project_key>`
- `--stage <stage_name>`
- `--fork-context false`
- `--provider host`

### 3.3 `uv run plb review record`

用途：

- 根据 worker verdict 自动写回审查结果
- 自动更新 review_state 为 `passed` / `needs_revision` / `failed`
- 把 review 结果从执行态变成权威状态记录

参数：

- `--project <project_key>`
- `--stage <stage_name>`
- `--result <path>`

### 3.4 `uv run plb review approve`

用途：

- 基于当前 worker verdict 做最终批准落库
- 仅当 worker verdict 为 `passed` 时，才会把 review state 落成 `passed`
- 不能绕过 worker verdict 手动把不通过的结果改成 `passed`

参数：

- `--project <project_key>`
- `--stage <stage_name>`

### 3.5 `uv run plb review reject`

用途：

- 基于当前 worker verdict 做最终拒绝落库
- `needs_revision` 和 `failed` 都会按 worker verdict 原样落库
- 不能用 reject 手工改写 worker verdict

参数：

- `--project <project_key>`
- `--stage <stage_name>`
- `--reason <text>`

## 4. Output Rules

所有命令输出都应保持统一风格：

- 机器可读时输出 JSON
- 人类可读时输出短摘要
- 每条输出都要有明确 `status`
- 每条输出都要有 `rollback_point`
- 每条输出都要说明是否推进状态
- `review packet` 输出必须说明冻结了哪些上游输入
- `review run` 输出必须说明审查是否在隔离上下文中执行
- `review record` 输出必须说明最终写回的 verdict

## 5. Failure Rules

命令失败时必须明确是：

- 参数错误
- 状态不允许
- 上游未批准
- 校验失败
- 审查失败
- 回归失败
- review packet / run / record 任一步失败，都不应假装下一步已完成

不得把失败混成“泛泛的异常”。
