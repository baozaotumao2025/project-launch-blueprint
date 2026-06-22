# Project Launch Blueprint

`project-launch-blueprint` is a Codex skill for turning raw project analysis into validated blueprint artifacts, implementation plans, and prototype code.

## Codex Quick Start

1. Read [`SKILL.md`](./SKILL.md).
2. Install the skill from the GitHub link in Codex.
3. In the target project, run:

```bash
uv run plb init
```

4. Then inspect the project state:

```bash
uv run plb status
```

5. For the full operating flow, read [docs/step-04-user-manual.md](./docs/step-04-user-manual.md).

## Install

Install this skill from the GitHub link in Codex. After installation, use it on the target project with `plb init` and `plb status`.

## First Run

Run `uv run plb init` in the target project, then `uv run plb status`.

## What It Does

This skill turns raw `analysis/` into:

1. 业务能力
2. 领域模型
3. 状态机
4. API 契约
5. 设计系统
6. 垂直切片实现
7. 质量门禁
8. 实现桥接
9. 发布为 skill 模板

`implementation` translates approved artifacts into prototype code, directories, tests, and configuration inside the target project.

It also defines:

- `uv` 管理的 CLI 入口
- revision-aware 的状态机
- fresh subagent 的隔离校验规则
- 模板打包和发布方式
- 命令参考表和阶段推进约束
- `analysis/` as the raw input layer
- `.project-launch-blueprint/projections/` for derived working copies
- project assets, process artifacts, and required state records
- default retention of traceable intermediate artifacts
- exclusion only of local caches, secrets, and fully reproducible noise

All links in this repository are relative to `records/project-launch-blueprint/`.

## Skill Entry

- `SKILL.md`
- `agents/openai.yaml`

## Repository Contents

- `README.md` for the public overview
- `docs/` for installation, sharing, and internal operating notes
- `cli-architecture.md` and `command-reference.md` for command behavior
- `workflow-state.md` for state and revision rules
- `implementation/` for the final bridge into prototype code

## More

- [User manual](./docs/step-04-user-manual.md)
- [Install from GitHub link](./docs/step-05-install-from-github-link.md)
- [Share readiness checklist](./docs/step-06-share-readiness-checklist.md)

## Core Rules

- 先验证，再抽象
- 主输入优先，辅助证据只用于核验、补漏和反例攻击
- 每层只做一件事
- 每层都必须有正向测试和负向测试
- 每层都必须有可执行回退点

## Release Checklist

Before sharing this repository, confirm the following:

- `.venv/`, `__pycache__/`, and `.pytest_cache/` are not committed
- secrets are not stored in the repository
- `SKILL.md`, `agents/openai.yaml`, `README.md`, and `docs/` are present
- the repository is stable enough for another reader or Codex session to follow without extra explanation
