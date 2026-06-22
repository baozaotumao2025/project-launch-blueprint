---
name: project-launch-blueprint
description: Install, initialize, and operate the Project Launch Blueprint skill to turn analysis into validated project artifacts, implementation plans, and prototype code.
---

# Project Launch Blueprint Skill

Use this skill when you need to:

- install or share the Project Launch Blueprint as a Codex skill
- initialize a target project with `plb init`
- inspect and progress blueprint stages with `plb status` and `plb stage ...`
- move from validated artifacts into `implementation`
- keep project assets, process artifacts, and runtime state organized

## Reading order

1. Read [`README.md`](./README.md) for the quick overview.
2. Read [`docs/step-04-user-manual.md`](./docs/step-04-user-manual.md) for install and init usage.
3. Read [`docs/step-03-project-space-and-artifact-classes.md`](./docs/step-03-project-space-and-artifact-classes.md) for artifact boundaries.
4. Read [`cli-architecture.md`](./cli-architecture.md) and [`command-reference.md`](./command-reference.md) for commands and state flow.
5. Read [`implementation/index.md`](./implementation/index.md) before translating approved artifacts into code.

## Core workflow

- Keep `analysis/` as raw input.
- Use the staged blueprint layers to validate and refine outputs.
- Treat `implementation` as the last bridge from verified artifacts to real prototype code.
- Keep project-space assets and process artifacts together so a future teammate can pick up the repository without losing context.

## Minimal operator guidance

- Initialize a project with `uv run plb init` from the target repository root.
- Check progress with `uv run plb status`.
- Use stage commands to generate, verify, and advance each layer.
- Use `implementation` only after upstream gates are approved.

