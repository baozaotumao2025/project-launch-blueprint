# ADR 0004: Route CLI and Natural Language Through the Same Workflow

## Status

Accepted

## Context

The project needs both deterministic command usage and flexible natural-language usage, but they must not diverge in behavior.

## Decision

The CLI and natural-language surfaces are thin entry points that route into the same workflow functions. Intent parsing only selects the stage or action; it does not create a separate business path.

## Consequences

- The command contract stays consistent across entry surfaces.
- Tests can cover one workflow path instead of two competing implementations.
- Future stages can be added once and exposed through both surfaces together.
