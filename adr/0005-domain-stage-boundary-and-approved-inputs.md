# ADR 0005: Domain Stage Uses Approved Upstream Inputs and Freezes Boundary

## Status

Accepted

## Context

`domain` is the first stage that turns discovery into a stable business boundary. It must not invent a new scope and must only operate on already approved upstream material.

## Decision

The domain stage consumes approved discovery output, frozen project definition, and the persisted stage documents for `domain-model/`. It uses the same review loop and isolated worker pattern as discovery, but the decision target is the domain boundary, not the raw analysis input.

## Consequences

- Domain output is derived from approved upstream context instead of fresh ad hoc interpretation.
- The domain boundary becomes the reference point for later state, API, and design work.
- Missing upstream approval blocks progress instead of allowing scope drift.
