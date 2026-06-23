# ADR 0014: Coverage-Driven Development And Explicit Invariants

## Status

Accepted

## Context

This project contains multiple workflow stages, prompt assembly steps, review packet builders, isolated review workers, and stage transition rules. These paths are easy to regress in two ways:

- a branch is added or refactored without a corresponding test for its edge behavior
- a critical assumption remains only in a prompt or convention, so the runtime never actually enforces it

Prompt-only rules are not sufficient for long-lived workflow automation. They can drift, be interpreted loosely, or fail silently when the code changes around them.

## Decision

Adopt a coverage-driven development strategy with explicit invariants.

- Treat coverage as a quantitative baseline for workflow reliability.
- For every stage, command, prompt assembly function, and review gate, add positive, negative, and boundary tests.
- Use coverage gaps to identify weak branches and fill them deliberately instead of relying on happy-path tests alone.
- Promote critical assumptions from prompt text or developer convention into code-level invariants when they must always hold.
- Express those invariants with assertions, precondition checks, or structural guards rather than natural-language guidance alone.
- Prefer code-enforced contracts for input inventories, coverage matrices, stage ordering, and review prerequisites.

In this project, the pattern is:

- `discovery` freezes file inventory before review
- `domain` freezes approved input inventory before review
- `state`, `api`, `design`, `slice`, and `gates` freeze approved upstream inventories before review
- `implementation` uses explicit goal-driven planning and regression checks, with its own invariants for blocked items and roll-forward behavior

## Consequences

Positive consequences:

- Key paths become testable, auditable, and easier to reason about.
- Prompt assembly no longer depends only on documentation discipline; the runtime itself enforces the important contract points.
- Coverage reports become a practical signal for which branches still need attention.
- Refactors are safer because invariant violations and missing edges fail early.
- Negative and boundary cases become first-class citizens of the workflow, not an afterthought.

Tradeoffs:

- More effort is required up front to model and test edge behavior.
- Some assumptions that once lived only in documentation must be represented as code.
- Coverage metrics must be interpreted alongside semantic correctness; a high percentage alone does not guarantee correctness.

## Result

The project now treats workflow correctness as a combination of:

- code-enforced invariants for mandatory rules
- coverage-driven tests for behavioral completeness
- prompt text as explanatory context, not as the enforcement boundary

This approach is intended to keep the workflow consistent as the repository evolves and as new stages, commands, or prompt templates are added.
