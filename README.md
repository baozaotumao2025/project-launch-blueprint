# Project Launch Blueprint

`project-launch-blueprint` is a Codex skill for turning a user project from installation into a shareable blueprint, staged contracts, and implementation-ready assets.

## What This Project Builds

This repository defines a complete launch protocol:

1. Install the skill
2. Initialize the project space
3. Inspect the post-install contract
4. Define the project boundary and final deliverables
5. Classify permanent assets, persistent runtime records, and disposable execution artifacts
6. Advance stage by stage through `discovery`, `domain`, `state`, `api`, `design`, `slice`, `gates`, and `implementation`
7. Finish with the user manual, GitHub installation guidance, and the share readiness checklist

The operating sequence is intentionally simple:

```text
plan -> status -> review packet -> review run -> review record -> approve/reject -> next
```

`implementation` is the last bridge. It turns approved stage outputs into real prototype code, tests, and configuration inside the target project.

The same internal workflow should be reachable through two surfaces:

- `CLI` for deterministic execution and testing
- natural language for guided operation and intent routing

The bootstrap entry is dependency-light and should fail hard when the target root is invalid. Use `-C/--root` or `PLB_ROOT_DIR` when you want to point at a project explicitly.

## Codex Quick Start

1. Read [`SKILL.md`](./SKILL.md).
2. Install the skill from the GitHub link in Codex.
3. In the target project, run:

```bash
uv run plb init
```

If you want to point at a specific project root, run:

```bash
plb -C /path/to/project init
```

4. Inspect the project state:

```bash
uv run plb status
```

Or:

```bash
plb -C /path/to/project status
```

5. Then follow the stage flow and review loop described in [docs/step-04-user-manual.md](./docs/step-04-user-manual.md).

## Install

Install this skill from the GitHub link in Codex. After installation, the target project should use `plb init`, `plb status`, stage commands, and review commands as the canonical operating surface. The bootstrap entry should work without making the user guess the root directory or recover from a silent fallback.

## First Run

Run `uv run plb init` in the target project, then `uv run plb status`.

## Stage Flow

The canonical stage order is:

1. `discovery`
2. `domain`
3. `state`
4. `api`
5. `design`
6. `slice`
7. `gates`
8. `implementation`

Each stage is expected to be worked in the same rhythm:

- `plan` to freeze the stage intent
- `status` to inspect current progress
- `review packet` to freeze the review input
- `review run` to execute the isolated review
- `review record` to write back the verdict
- `approve` or `reject` to finalize the stage result
- `next` to advance when the stage is ready

## Project Boundaries

This skill keeps three spaces separate:

- `skill space`: the installed Codex capability bundle
- `project space`: the user project that receives the blueprint and generated assets
- runtime execution artifacts: state, audits, projections, and temporary review material

The repository also distinguishes:

- permanent blueprint artifacts
- generated project artifacts
- persistent runtime artifacts
- disposable runtime artifacts

Only the first three should be preserved as durable project history when they help the next reader continue the work.

## Skill Entry

- `SKILL.md`
- `agents/openai.yaml`

## Repository Contents

- `README.md` for the public overview
- `docs/` for installation, user manual, and share preparation
- `command-reference.md` for the canonical command contract
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
