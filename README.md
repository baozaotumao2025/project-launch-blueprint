# Project Launch Blueprint

> 这是 `project-launch-blueprint` 的快速入口。  
> 如果你第一次接触这套方法论，先读这里，再读 `index.md` 和 `template-spec.md`。

## What This Is

这是一套面向前端项目启动的分层方法论，用来把原始 `analysis/` 逐层收敛成：

1. 业务能力
2. 领域模型
3. 状态机
4. API 契约
5. 设计系统
6. 垂直切片实现
7. 质量门禁
8. 实现桥接
9. 发布为 skill 模板

其中 `implementation` 不是附属说明，而是把已验证的中间产物真正翻译成用户项目里的原型代码、目录、测试和配置的最后落地层。

这套蓝图同时定义了：

- `uv` 管理的 CLI 入口
- revision-aware 的状态机
- fresh subagent 的隔离校验规则
- 模板打包和发布方式
- 命令参考表和阶段推进约束
- `analysis/` 只承载原始素材，派生稿写入 `.project-launch-blueprint/projections/`
- 用户项目里的正式代码、阶段产物、过程产物和必要状态记录
- 默认把可追踪的中间产物也作为项目资产保留
- 只排除纯本机缓存、敏感信息和可完全重建的噪音文件

本目录下的所有链接都默认以 `records/project-launch-blueprint/` 为根目录，只使用相对路径。

其中前 7 项是生成层，质量门禁负责放行，实现桥接负责把已放行的产物翻译成真实代码。

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
