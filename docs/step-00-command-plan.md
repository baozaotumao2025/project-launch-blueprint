# Step 00: Command Plan

> 目标：先把整套 `plb` 需要执行的命令顺序规划清楚，再按这份清单边做边测试。

## 1. Planning Principle

这套命令不是按“功能按钮”堆起来的，而是按业务流推进的。

先完成安装与初始化，再进入 stage 处理，最后收束到实施、手册和分享准备。

这套能力有两种入口：

- `CLI`：适合确定性执行、自动化和测试
- 自然语言：适合意图表达、流程引导和交互式使用

两种入口必须共享同一套内部实现，不能各写一套状态逻辑。

## 2. Canonical Command Flow

### 2.1 Bootstrapping

1. `uv run plb init`
2. `uv run plb status`

用途：

- 初始化 project space
- 建立运行目录、状态库和审查目录
- 确认初始化结果

### 2.2 Stage Progression

每个 stage 都按同一节奏推进：

```text
plan -> status -> review packet -> review run -> review record -> approve/reject -> next
```

Stage 顺序固定为：

1. `discovery`
2. `domain`
3. `state`
4. `api`
5. `design`
6. `slice`
7. `gates`
8. `implementation`

### 2.3 Finalization

当 `implementation` 完成后，再进入收尾文档：

1. `docs/step-04-user-manual.md`
2. `docs/step-05-install-from-github-link.md`
3. `docs/step-06-share-readiness-checklist.md`

## 3. Command Responsibilities

### 3.0 Entry Surfaces

- `plb init` 和“初始化这个项目”应映射到同一条内部初始化逻辑
- `plb status` 和“查看当前状态”应映射到同一条内部状态读取逻辑
- stage 命令和自然语言里的“开始某个阶段”“查看某个阶段”“继续下一步”应映射到同一套 stage 服务

### 3.1 Read-Only Commands

- `uv run plb status`
- `uv run plb stage <stage> status`
- `uv run plb stage <stage> verify`
- `uv run plb review packet` 只是在冻结输入，不推进业务完成度

### 3.2 State-Mutating Commands

- `uv run plb init`
- `uv run plb stage <stage> plan`
- `uv run plb stage <stage> next`
- `uv run plb stage <stage> set <status>`
- `uv run plb review run`
- `uv run plb review record`
- `uv run plb review approve`
- `uv run plb review reject`

## 4. What Each Review Step Does

- `review packet`: 冻结当前 stage 的输入，生成可审查包
- `review run`: 把 packet 交给隔离 reviewer 执行
- `review record`: 把 reviewer verdict 写回状态
- `review approve`: 将通过结果固化为最终批准
- `review reject`: 将不通过结果固化为最终拒绝

## 5. Suggested Test Order

### 5.1 Bootstrap Tests

- 初始化空项目
- 初始化后读取状态
- 确认运行目录存在
- 确认业务源码目录没有被误创建

### 5.2 Stage Tests

- 每个 stage 的 `plan` 能否创建或更新 stage 记录
- `status` 是否只读
- `verify` 是否阻止未满足前置条件的推进
- `next` 是否只在前置条件满足时推进到下一阶段

### 5.3 Review Tests

- `review packet` 是否冻结正确的上游输入
- `review run` 是否真的在隔离上下文执行
- `review record` 是否写回 verdict
- `approve` / `reject` 是否遵守 worker verdict

### 5.4 Finalization Tests

- `implementation` 是否只在 gates 通过后推进
- 用户手册是否与命令行为一致
- GitHub 安装说明和分享清单是否与最终流程一致

## 6. Failure Rules

出现失败时，必须明确归类为下面之一：

- 参数错误
- 状态不允许
- 上游未批准
- 校验失败
- 审查失败
- 回归失败

不能把失败混成模糊异常，也不能跳过中间状态。

## 7. Next Step

下一步建议先做两件事：

1. 用这份命令清单验证 `init -> status` 的基础链路
2. 选一个 stage 跑完整的 `plan -> packet -> run -> record -> approve -> next` 闭环
