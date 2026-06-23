---
name: project-launch-blueprint
description: Install, initialize, and operate the Project Launch Blueprint skill to move a user project from project-space setup through staged contracts, review loops, and implementation-ready deliverables.
---

# Project Launch Blueprint Skill

## Quick Start

1. Read [`README.md`](./README.md).
2. Read [`docs/step-04-user-manual.md`](./docs/step-04-user-manual.md).
3. Install or import the skill from the GitHub link in Codex.
4. Run `uv run plb init`.
5. Run `uv run plb status`.
6. If needed, pass `--root /path/to/project` or set `PLB_ROOT_DIR`.

## Read Next

1. `docs/step-05-install-from-github-link.md`
2. `docs/step-01-skill-installation-and-artifact-contract.md`
3. `docs/step-02-project-definition-and-final-deliverables.md`
4. `docs/step-03-project-space-and-artifact-classes.md`
5. `command-reference.md`
6. `cli-architecture.md`
7. `docs/tutorial/index.md`
8. `adr/README.md`
9. `implementation/index.md`

## Do This

1. Initialize the target project.
2. Inspect `status`.
3. Follow the stage flow in order:
   `discovery` -> `domain` -> `state` -> `api` -> `design` -> `slice` -> `gates` -> `implementation`
4. Use the shared rhythm for each stage:
   `plan` -> `status` -> `review packet` -> `review run` -> `review record` -> `approve/reject` -> `next`
5. Use `uv run plb route "<text>"` when you want the natural-language entry point.
6. For every stage, require a frozen stage-document inventory and matching coverage template before review can pass.
7. For `discovery`, also require a file-level `analysis_inventory` and matching coverage template.
8. For `domain`, also require an approved-discovery-backed input inventory and matching coverage template.
9. For `state`, `api`, `design`, `slice`, and `gates`, also require approved upstream input bundles and matching coverage templates.
10. For strict E2E testing, create a temporary project root under `/tmp`, seed a minimal `analysis/`, run the full stage chain, then delete the temp root after the test.

## Rules

- Keep `skill space` and `project space` separate.
- Treat the stage flow as business progression.
- Do not skip validation before moving to the next stage.
- Treat `implementation` as the last bridge from verified artifacts to implementation code, scaffolds, and verification artifacts.
- Treat `implementation` as the last bridge from verified artifacts to implementation scaffolds, regression checks, and handoff records; do not promise a finished interactive UI unless the target project has a real frontend runtime path.
- Treat stage input inventory and coverage validation as code-enforced, not prompt-enforced.
- Treat stage document inventory and coverage validation as code-enforced, not prompt-enforced.
- Keep temporary execution files separate from durable project assets unless the docs explicitly say they should be preserved.
- Keep this file short and navigational; prefer links to companion files instead of duplicating long explanations.
- Treat 200 lines as a soft upper bound for `SKILL.md` so the skill stays efficient to read in-session.

## Decision Records

- Use `adr/` for implementation decisions and read it after the operating contract.
- Use `docs/tutorial/` for stage-by-stage teaching material and read it before implementation details.
- When a detail needs more than one short rule, move it into `README.md`, `docs/`, `command-reference.md`, or `adr/` and link to it here.

## Constraints

- Do not start `implementation` before `gates` are approved.
- Do not collapse review packet, review run, and review record into one step when the workflow needs auditable separation.
- Do not treat temporary execution files as final assets unless they are meant to be preserved with the project history.
- Do not require the user to recover from a silent fallback when the root or installation is wrong.
