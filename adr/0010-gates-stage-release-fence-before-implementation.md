# ADR 0010: Gates Stage Is the Final Release Fence Before Implementation

## Status

Accepted

## Context

The gates stage must confirm that every upstream decision is ready before implementation is allowed to proceed.

## Decision

The gates stage consumes all approved upstream artifacts and `quality-gates/` documents, then blocks implementation until the release fence is satisfied. It is the last non-implementation stage in the workflow order.

## Consequences

- Implementation cannot start early.
- Readiness checks stay separate from code generation.
- The project has one final gate that can surface missing approvals, stale inputs, or unresolved risks.
