# Project Launch Blueprint

> 这是 `project-launch-blueprint` 的快速入口。  
> 如果你第一次接触这套方法论，先读这里，再读 `index.md` 和 `template-spec.md`。

## What This Is

`project-launch-blueprint` 是一套面向前端项目启动的分层方法论，也是一个可分发的 Codex skill 模板。它将原始 `analysis/` 逐层收敛为：

1. 业务能力
2. 领域模型
3. 状态机
4. API 契约
5. 设计系统
6. 垂直切片实现
7. 质量门禁
8. 实现桥接
9. 发布为 skill 模板

其中 `implementation` 负责将已验证的中间产物转译为用户项目中的原型代码、目录、测试与配置，并完成最终落地。

本仓库同时定义了：

- `uv` 管理的 CLI 入口
- revision-aware 的状态机
- fresh subagent 的隔离校验规则
- 模板打包和发布方式
- 命令参考表和阶段推进约束
- `analysis/` 只承载原始素材，派生稿写入 `.project-launch-blueprint/projections/`
- 用户项目里的正式代码、阶段产物、过程产物和必要状态记录
- 默认把可追踪的中间产物也作为项目资产保留
- 只排除纯本机缓存、敏感信息和可完全重建的噪音文件

本目录下的所有链接默认以 `records/project-launch-blueprint/` 为根目录，只使用相对路径。

其中前 7 项是生成层，质量门禁负责放行，实现桥接负责把已放行的产物翻译成真实代码。

## Distribution

通过 GitHub 链接访问时，这个仓库可作为协作入口，供查看、克隆或继续开发。

作为 Codex skill 分发时，仓库中的 `SKILL.md` 与 `agents/openai.yaml` 提供了可识别的入口。

当前仓库已经包含了可识别的 skill 入口：

- `SKILL.md`
- `agents/openai.yaml`

直接克隆到本地时，它仍然可以作为项目仓库继续开发；在 Codex 中作为 skill 使用时，应通过 GitHub 分享/安装入口导入。

当前使用手册见 [docs/step-04-user-manual.md](./docs/step-04-user-manual.md)。

## Release Checklist

在对外分享该仓库之前，建议确认：

- 不要把 `.venv/`、`__pycache__/`、`.pytest_cache/` 这类本机开发产物提交到仓库
- 不要把敏感信息放进仓库
- 保留 `SKILL.md`、`agents/openai.yaml`、`README.md` 和 `docs/` 里的使用说明
- 如果要作为 skill 安装入口分享，确保仓库内容已整理为稳定、可读的状态

## Core Rules

- 先验证，再抽象
- 主输入优先，辅助证据只用于核验、补漏和反例攻击
- 每层只做一件事
- 每层都必须有正向测试和负向测试
- 每层都必须有可执行回退点

## Start Here

1. 先读 [index.md](./index.md)
2. 再读 [cli-architecture.md](./cli-architecture.md)
3. 然后读 [workflow-state.md](./workflow-state.md)
4. 再读 [command-reference.md](./command-reference.md)
5. 再读 [template-spec.md](./template-spec.md)
6. 然后进入对应阶段目录

## Project Files

- [index.md](./index.md)
- [cli-architecture.md](./cli-architecture.md)
- [workflow-state.md](./workflow-state.md)
- [command-reference.md](./command-reference.md)
- [template-spec.md](./template-spec.md)
- [discovery/](./discovery/index.md)
- [domain-model/](./domain-model/index.md)
- [state-machine/](./state-machine/index.md)
- [api-contract/](./api-contract/index.md)
- [design-system/](./design-system/index.md)
- [vertical-slice/](./vertical-slice/index.md)
- [quality-gates/](./quality-gates/index.md)
- [implementation/](./implementation/index.md)

## For New Projects

如果你要复制这套方法论到新项目：

1. 先复制 `template-spec.md`
2. 再复制 `cli-architecture.md`
3. 再复制 `workflow-state.md`
4. 再复制 `command-reference.md`
5. 再创建新项目自己的 `README.md`
6. 然后按阶段生成各层目录
7. 最后替换成项目专属输入、命名和样板
8. 如果要落到真实编码，再读 `implementation/`
