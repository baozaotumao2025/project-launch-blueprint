---
name: project-launch-blueprint
description: Install, initialize, and operate the Project Launch Blueprint skill to move a user project from project-space setup through staged contracts, review loops, and implementation-ready deliverables.
---

# Project Launch Blueprint Skill

## Quick Start

1. Read [`README.md`](./README.md).
2. Read [`docs/step-04-user-manual.md`](./docs/step-04-user-manual.md).
3. Install or import the skill from the GitHub link in Codex.
4. In the target project, run `uv run plb init`.
5. Then run `uv run plb status`.

## What This Skill Does

- Install the skill into Codex and initialize the target project space.
- Define the post-install contract so the project knows what was created, what stayed out, and what must be preserved.
- Define the project boundary and final deliverables before implementation starts.
- Classify permanent blueprint artifacts, generated project artifacts, persistent runtime artifacts, and disposable runtime artifacts.
- Advance the project through `discovery`, `domain`, `state`, `api`, `design`, `slice`, `gates`, and `implementation`.
- Use the review loop `plan -> status -> review packet -> review run -> review record -> approve/reject -> next` to keep every stage auditable.
- Turn approved stage outputs into prototype code, directories, tests, and configuration in the target project.
- Keep user manual, GitHub installation guidance, and share readiness instructions aligned with the same operating contract.
- Expose the same internal workflow through both `CLI` and natural language entry surfaces.

## Reading Order

1. `README.md`
2. `docs/step-04-user-manual.md`
3. `docs/step-05-install-from-github-link.md`
4. `docs/step-01-skill-installation-and-artifact-contract.md`
5. `docs/step-02-project-definition-and-final-deliverables.md`
6. `docs/step-03-project-space-and-artifact-classes.md`
7. `command-reference.md`
8. `cli-architecture.md`
9. `implementation/index.md`

## Operating Rules

- Keep `skill space` and `project space` separate.
- Treat the stage flow as business progression, not as a generic command catalog.
- Use `plan`, `status`, `review packet`, `review run`, `review record`, `approve/reject`, and `next` as the shared rhythm for every stage.
- Treat `implementation` as the last bridge from verified artifacts to real prototype code.
- Do not skip validation before moving to the next stage.
- Keep temporary execution files separate from durable project assets unless the docs explicitly say they should be preserved.

## Constraints

- Do not start `implementation` before `gates` are approved.
- Do not collapse review packet, review run, and review record into one step when the workflow needs auditable separation.
- Do not treat temporary execution files as final assets unless they are meant to be preserved with the project history.
