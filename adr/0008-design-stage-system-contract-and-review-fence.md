# ADR 0008: Design Stage Enforces System Contract Before Slice Work

## Status

Accepted

## Context

The design stage should turn the approved API contract into design-system rules that the implementation can follow without reinterpretation.

## Decision

The design stage consumes approved API and upstream context, then binds its work to `design-system/` documents. Its review boundary focuses on visual and component-system constraints, not on business logic discovery.

## Consequences

- Design decisions are kept consistent with the API contract.
- Visual/system rules are frozen before vertical slicing begins.
- The stage acts as a review fence so slice work does not re-litigate design basics.
