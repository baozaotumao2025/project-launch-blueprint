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

`implementation` is the last bridge. It turns approved stage outputs into real prototype code, tests, and configuration inside the target project. In the current project, that bridge is code-driven and verification-driven: it produces implementation plans, scaffolds, regression checks, and handoff artifacts. A rendered interactive UI still depends on the target project's own frontend runtime and code generation path.

Every stage must first freeze a stage-document inventory and matching coverage template before review can pass. `discovery` additionally builds a file-level `analysis_inventory`, and `domain` additionally builds an input inventory from approved discovery artifacts and auxiliary evidence. In both cases, the inventory is code-generated, frozen into the review packet, and rejected if the coverage rows do not align.

The same internal workflow should be reachable through two surfaces:

- `CLI` for deterministic execution and testing
- natural language for guided operation and intent routing

You can route the natural-language surface with `uv run plb route "<text>"`, and it will call the same underlying workflow functions as the typed commands.

## Practical E2E Path

For a strict end-to-end run, keep the project root in a temporary directory, seed a small mock `analysis/`, and drive the same command surface the user would use:

1. `uv run plb init`
2. `uv run plb status`
3. Create the minimal `analysis/` inputs required by `discovery`, plus a few extra files so inventory coverage can prove nothing was skipped
4. Run `discovery` through `plan -> status -> review packet -> review run -> review record -> approve -> next`
5. Repeat the same cycle for `domain`, `state`, `api`, `design`, `slice`, and `gates`
6. Enter `implementation` with a concrete `--goal`
7. Run `stage implementation next` until all implementation goals are completed
8. Finish with `stage implementation verify --strict`

For negative coverage, the current project expects tests to also verify these cases:

- `discovery` blocks when `analysis/` is incomplete
- a tampered coverage matrix is rejected by the isolated review worker
- natural-language routing returns `blocked` when the request is too vague
- `implementation` blocks when `--goal` is missing

The bootstrap entry is dependency-light and should fail hard when the target root is invalid. Use `--root` or `PLB_ROOT_DIR` when you want to point at a project explicitly.

The test suite is wired to `pytest-cov`, so `uv run pytest` now prints a `src/plb` coverage baseline by default.

## Codex Quick Start

1. Read [`SKILL.md`](./SKILL.md).
2. Install the skill from the GitHub link in Codex.
3. In the target project, run:

```bash
uv run plb init
```

If you want to point at a specific project root, run:

```bash
uv run plb --root /path/to/project init
```

4. Inspect the project state:

```bash
uv run plb status
```

Or:

```bash
uv run plb --root /path/to/project status
```

5. Then follow the stage flow and review loop described in [docs/step-04-user-manual.md](./docs/step-04-user-manual.md).

## Install

Install this skill from the GitHub link in Codex. After installation, the target project should use `uv run plb ...` as the canonical operating surface. The bootstrap entry should work without making the user guess the root directory or recover from a silent fallback. A direct `plb ...` shell alias may exist when the environment installs it, but it is only a convenience shortcut.

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
- `adr/` for architecture decision records
- `command-reference.md` for the canonical command contract
- `workflow-state.md` for state and revision rules
- `implementation/` for the final bridge into prototype code

## More

- [User manual](./docs/step-04-user-manual.md)
- [Install from GitHub link](./docs/step-05-install-from-github-link.md)
- [Share readiness checklist](./docs/step-06-share-readiness-checklist.md)
- [Tutorials index](./docs/tutorial/index.md)
- [Architecture decision records](./adr/README.md)

## Core Rules

- 先验证，再抽象
- 主输入优先，辅助证据只用于核验、补漏和反例攻击
- Each stage must enumerate its stage documents, freeze an inventory, and require a matching coverage matrix before review can pass
- `discovery` and `domain` additionally freeze their own external input inventories
- `state`, `api`, `design`, `slice`, and `gates` additionally freeze approved upstream input bundles before review can pass
- `implementation` consumes approved upstream artifacts and emits implementation plans, scaffolds, regression checks, and handoff records; it does not magically produce a finished interactive UI without the target project's own runtime/code path
- Use coverage-driven development plus explicit invariants: cover positive, negative, and boundary cases, and move critical assumptions into code-level assertions or precondition checks instead of prompt-only rules
- 每层只做一件事
- 每层都必须有正向测试和负向测试
- 每层都必须有可执行回退点

## Release Checklist

Before sharing this repository, confirm the following:

- `.venv/`, `__pycache__/`, and `.pytest_cache/` are not committed
- secrets are not stored in the repository
- `SKILL.md`, `agents/openai.yaml`, `README.md`, `docs/`, and `adr/` are present
- the repository is stable enough for another reader or Codex session to follow without extra explanation
