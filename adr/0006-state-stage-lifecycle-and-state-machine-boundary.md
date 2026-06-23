# ADR 0006: State Stage Owns the State Machine Boundary and Lifecycle Rules

## Status

Accepted

## Context

The state stage must translate the approved domain boundary into stable lifecycle rules and state transitions that can be persisted and audited.

## Decision

The state stage reads approved discovery and domain outputs, then constrains its prompt bundle and review packet to `state-machine/` documents. Its result is expected to define lifecycle boundaries, persistence rules, and rollback points without crossing into API or design concerns.

## Consequences

- State transitions become auditable instead of implicit.
- Lifecycle records in the database are aligned with the state machine contract.
- The stage stays focused on state semantics and does not leak downstream implementation details.
