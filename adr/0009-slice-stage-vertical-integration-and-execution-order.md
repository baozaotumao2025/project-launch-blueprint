# ADR 0009: Slice Stage Builds Vertical Integration From Approved Layers

## Status

Accepted

## Context

The slice stage is where the project starts packaging domain, state, API, and design decisions into implementation-shaped vertical slices.

## Decision

The slice stage uses approved upstream outputs plus `vertical-slice/` documents to produce a cross-layer execution order. It keeps the same review loop and isolated worker rules so slice assembly is auditable and repeatable.

## Consequences

- Slice work can be checked before implementation starts.
- Cross-layer dependencies become explicit.
- The execution order is controlled rather than inferred from scattered implementation tasks.
