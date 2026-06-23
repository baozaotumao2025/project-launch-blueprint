# ADR 0002: Use a Unified Stage Prompt Bundle and Isolated Worker

## Status

Accepted

## Context

The stage flow needs a single way to assemble method, template, schema, example, and checklist inputs so generation and review behave consistently across CLI and natural language entry points.

## Decision

Every stage request is compiled into a `StagePromptBundle`. Review execution is routed through an isolated worker or subagent that receives the bundle instead of inheriting the caller's live context.

## Consequences

- Prompt assembly is centralized and testable.
- Review work is isolated from the caller's conversational state.
- CLI and natural language surfaces can share the same execution contract.
