# ADR 0007: API Stage Synthesizes Contracts From Approved Upstream State

## Status

Accepted

## Context

The API stage must produce a contract that is consistent with approved domain and state decisions. It should not create a standalone interface that conflicts with the state machine or the business boundary.

## Decision

The API stage uses the same prompt bundle and isolated review pipeline, but its contract source is the approved upstream state and domain context together with `api-contract/` documents. Validation is centered on schema shape, endpoint intent, and compatibility with earlier stages.

## Consequences

- API outputs are derived, not invented in isolation.
- Contract validation can detect mismatches before design or slice work starts.
- The API stage acts as a synthesis layer between state semantics and user-facing implementation.
