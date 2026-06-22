---
name: project-launch-blueprint
description: Install, initialize, and operate the Project Launch Blueprint skill to turn analysis into validated project artifacts, implementation plans, and prototype code.
---

# Project Launch Blueprint Skill

Use this skill to:

- install or share the Project Launch Blueprint as a Codex skill
- initialize a target project with `plb init`
- inspect and progress blueprint stages with `plb status` and `plb stage ...`
- move from validated artifacts into `implementation`
- keep project assets, process artifacts, and runtime state organized

## Agent Start Order

1. Read [`README.md`](./README.md).
2. Read [`docs/step-04-user-manual.md`](./docs/step-04-user-manual.md).
3. Read [`docs/step-05-install-from-github-link.md`](./docs/step-05-install-from-github-link.md).
4. Read [`docs/step-03-project-space-and-artifact-classes.md`](./docs/step-03-project-space-and-artifact-classes.md).
5. Read [`cli-architecture.md`](./cli-architecture.md) and [`command-reference.md`](./command-reference.md).
6. Read [`implementation/index.md`](./implementation/index.md) before translating approved artifacts into code.

## Default Workflow

- Keep `analysis/` as raw input.
- Use the staged blueprint layers to validate and refine outputs.
- Keep `implementation` as the last bridge from verified artifacts to real prototype code.
- Keep project-space assets and process artifacts together so future readers can continue without reconstruction.

## Minimal Commands

- Initialize a project with `uv run plb init` from the target repository root.
- Check progress with `uv run plb status`.
- Use stage commands to generate, verify, and advance each layer.
- Use `implementation` only after upstream gates are approved.

## Hard Constraints

- Do not skip validation before moving to the next stage.
- Do not treat temporary execution files as final assets unless they are meant to be preserved with the project history.
- Do not start implementation before `quality-gates` are approved.
