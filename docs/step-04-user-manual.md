# Step 04: User Manual

> 目标：给第一次使用这个 skill 的用户一份最短、最清晰的使用手册。

## 1. How To Install The Skill

先把这套 skill 安装到 Codex 的全局 skill 区。

安装后，Codex 才能识别这套蓝图提供的命令、阶段和实现桥接规则。

安装完成后，用户就可以在自己的项目里通过这套 skill 推进工作。

## 2. How To Initialize A Project

在目标项目根目录下执行初始化。

如果你在本仓库里本地开发，可以使用：

```bash
uv run plb init
```

如果你已经把它安装成可执行命令，也可以使用：

```bash
plb init
```

如果你想明确指定目标项目根目录，可以使用：

```bash
plb -C /path/to/project init
```

初始化后会发生这些事：

- 创建 `.project-launch-blueprint/` 运行目录
- 建立 `state.db`
- 建立 `logs/`、`audits/`、`exports/`、`backups/`、`projections/`
- 把项目状态置为 `initialized`
- 准备 stage registry 和 review 记录空间

初始化后，用户可以再运行：

```bash
uv run plb status
```

或者：

```bash
plb status
```

或者：

```bash
plb -C /path/to/project status
```

用来查看当前项目状态。

## 3. What The User Should Do Next

初始化不会直接生成业务代码。

它只会建立 skill 的运行态和项目状态基础。

下一步应该按业务流往下推进：

1. 查看安装后契约和项目边界
2. 定义最终交付物
3. 分类正式资产、持久运行记录、临时执行物
4. 依次推进 `discovery`、`domain`、`state`、`api`、`design`、`slice`、`gates`、`implementation`
5. 在每一阶段使用 `plan -> status -> review packet -> review run -> review record -> approve/reject -> next`

`implementation` 才会进入原型代码、目录、测试和配置的正式生成。

## 4. Positive Scenarios

- 安装 skill 后，用户可以在目标项目里运行 `init`
- `init` 之后，项目状态变为 `initialized`
- `status` 可以读到初始化后的状态
- 初始化只创建 skill 运行态目录，不会污染业务源码树
- 用户可以按 stage 顺序推进，而不是跳过前置步骤
- 每一阶段都能先看 `status`，再做 review，再决定是否 `approve`

## 5. Negative Scenarios

- 没有安装 skill 时，用户不应该期待本地 CLI 可用
- 在 `init` 之前，项目状态不应该被误判为已初始化
- 初始化不应该自动生成业务源码目录
- 初始化不应该直接产生原型代码
- 没有先 `review packet` 就不应该直接假装完成审查
- 没有 `review run` 就不应该把结果当成已经审过
- 没有 `review record` 就不应该把结果当成已落库

## 6. Verification Checklist

- 能成功初始化一个空项目
- 能在初始化后读取到 `initialized`
- 能确认 `.project-launch-blueprint/` 被建立
- 能确认 `src/`、`tests/` 这类业务源码目录没有被初始化命令无端创建
- 能确认初始化阶段没有越权进入实现阶段
- 能按 stage 顺序推进
- 能看懂每一阶段的 review packet / review run / review record / approve / reject / next
