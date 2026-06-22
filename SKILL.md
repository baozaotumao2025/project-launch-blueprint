---
name: project-launch-blueprint
description: Install, initialize, and operate the Project Launch Blueprint skill to turn analysis into validated project artifacts, implementation plans, and prototype code.
---

# Project Launch Blueprint Skill

## Quick Start

1. Read [`README.md`](./README.md).
2. Read [`docs/step-04-user-manual.md`](./docs/step-04-user-manual.md).
3. Install or import the skill from the GitHub link in Codex.
4. In the target project, run `uv run plb init`.
5. Then run `uv run plb status`.

## What This Skill Does

- Turn raw `analysis/` into validated blueprint artifacts.
- Move approved artifacts into `implementation`.
- Generate prototype code, directories, tests, and configuration in the target project.
- Keep project assets, process artifacts, and runtime state organized.

## Reading Order

1. `README.md`
2. `docs/step-04-user-manual.md`
3. `docs/step-05-install-from-github-link.md`
4. `docs/step-03-project-space-and-artifact-classes.md`
5. `cli-architecture.md`
6. `command-reference.md`
7. `implementation/index.md`

## Operating Rules

- Keep `analysis/` as raw input.
- Use the staged blueprint layers to validate and refine outputs.
- Treat `implementation` as the last bridge from verified artifacts to real prototype code.
- Use stage commands only after upstream gates are ready.

## Constraints

- Do not skip validation before moving to the next stage.
- Do not treat temporary execution files as final assets unless they are meant to be preserved with the project history.
- Do not start implementation before `quality-gates` are approved.
