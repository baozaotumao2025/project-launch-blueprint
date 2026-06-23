# ADR 0003: Require User-Prepared Discovery Inputs

## Status

Accepted

## Context

The discovery stage depends on analysis assets that come from the user's project work. Those files must not be fabricated by the skill or by the IDE assistant.

## Decision

Discovery planning, packet creation, and review must verify the presence of `analysis/brief.md`, `analysis/story-maps/*.md`, `analysis/pages/*.md`, `analysis/features/index.md`, `analysis/gwt/*.feature`, and `analysis/relations/*.md`. If they are missing, the workflow stops and tells the user to prepare them.

## Consequences

- The workflow respects the user's source material and avoids hallucinating discovery inputs.
- Missing prerequisites surface early, before review or state transitions.
- Discovery remains a user-owned analysis step instead of an auto-generated shortcut.
