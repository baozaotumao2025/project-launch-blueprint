# Step 04: User Manual

> 目标：给第一次使用这个 skill 的用户一份最短、最清晰的使用手册。

## 1. How To Install The Skill

先把这套 skill 安装到 Codex 的全局 skill 区。

安装后，Codex 才能识别这套蓝图提供的命令、阶段和实现桥接规则。

安装完成后，用户就可以在自己的项目里通过这套 skill 推进工作。

## 2. How To Initialize A Project

在目标项目根目录下执行初始化。

优先使用下面这条 canonical 写法：

```bash
uv run plb init
```

如果你的环境里已经安装了 `plb` 可执行命令，也可以把它当作可选 alias 使用：

```bash
plb init
```

如果你想明确指定目标项目根目录，可以使用：

```bash
uv run plb --root /path/to/project init
```

初始化后会发生这些事：

- 创建 `.project-launch-blueprint/` 运行目录
- 把最小发行包 materialize 到 `records/project-launch-blueprint/`，包括 stage 方法论文件和 `adr/`
- 建立 `state.db`
- 建立 `logs/`、`audits/`、`exports/`、`backups/`、`projections/`
- 把项目状态置为 `initialized`
- 准备 stage registry 和 review 记录空间
- 为每个 stage 写入生命周期种子记录，方便后续恢复、排障和审计

初始化后，用户可以再运行：

```bash
uv run plb status
```

如果你的环境里已经安装了 `plb` 可执行命令，也可以使用：

```bash
plb status
```

或者：

```bash
uv run plb --root /path/to/project status
```

用来查看当前项目状态。

如果你想用自然语言推进同一条流程，也可以运行：

```bash
uv run plb route "开始 discovery"
```

或者：

```bash
uv run plb route "生成 discovery 审查包"
```

## 3. What The User Should Do Next

初始化不会直接生成业务代码。

它只会建立 skill 的运行态和项目状态基础。

下一步应该按业务流往下推进：

1. 查看安装后契约和项目边界
2. 定义最终交付物
3. 分类正式资产、持久运行记录、临时执行物
4. 依次推进 `discovery`、`domain`、`state`、`api`、`design`、`slice`、`gates`、`implementation`
5. 在每一阶段使用 `plan -> status -> review packet -> review run -> review record -> approve/reject -> next`

`implementation` 才会进入实现桥接，开始产出代码骨架、测试计划、配置草案和交付收束信息。当前项目本身并不直接“凭空画出”一个已经渲染好的交互式 UI；如果你想得到真正可交互的原型，还需要目标项目自己的前端运行时和页面生成路径配合。

如果你想系统学习每个 stage 是怎么实现的，先看 `docs/tutorial/index.md`，再回到具体代码和测试。

从 `discovery` 开始，`review` 一律走独立 worker / subagent，不允许在当前上下文里直接审查。
同时，`discovery` 只有在用户准备好 `analysis/brief.md`、`analysis/story-maps/*.md`、`analysis/pages/*.md`、`analysis/features/index.md`、`analysis/gwt/*.feature`、`analysis/relations/*.md` 后才允许继续。
另外，`discovery` 会先对 `analysis/` 做文件级 inventory，再生成逐文件覆盖矩阵。你可以把它理解成“每个文件都必须被对账，或者被显式排除”，不能只说“看过这个目录”。

## 5. Strict E2E Checklist

如果你要按照当前项目做一次严格的端到端验证，推荐这样走：

1. 在 `/tmp` 下创建一个临时项目根目录，测试完就删除
2. `uv run plb init`
3. 先跑一个负向用例，确认 `analysis/` 不完整时 `discovery` 会阻断
4. 补齐一个很小的 mock `analysis/`，但额外再放几份非必需文件，验证 inventory 不会漏
5. 跑完整的 `discovery -> domain -> state -> api -> design -> slice -> gates -> implementation`
6. 在 `discovery` 和 `domain` 上各做一次 coverage 篡改，确认隔离 reviewer 会拒绝
7. 在自然语言入口上做一次歧义输入测试，确认不会被错误解释成成功完成
8. 在 `implementation` 上做一次缺 `--goal` 测试，确认会被阻断
9. 最后用一个小目标把 `implementation` 跑到 `verify --strict`

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
- `analysis/` 里有文件没进入 inventory 或没进入 coverage matrix，就不应该放行 discovery
- `implementation` 没有 `--goal` 时不应该进入真正的实施计划
- 自然语言输入过于模糊时，不应该被系统假装成成功执行

## 6. Verification Checklist

- 能成功初始化一个空项目
- 能在初始化后读取到 `initialized`
- 能确认 `.project-launch-blueprint/` 被建立
- 能确认 `records/project-launch-blueprint/adr/` 被建立
- 能确认 `src/`、`tests/` 这类业务源码目录没有被初始化命令无端创建
- 能确认初始化阶段没有越权进入实现阶段
- 能按 stage 顺序推进
- 能看懂每一阶段的 review packet / review run / review record / approve / reject / next
- 能理解 discovery 的 file inventory / coverage matrix / unmapped files 是怎么工作的
