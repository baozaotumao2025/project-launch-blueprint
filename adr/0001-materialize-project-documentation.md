# ADR 0001: Materialize Project Documentation During Initialization

## Status

Accepted

## Context

The skill needs a predictable project-local documentation tree so later stage execution can read the same method, template, schema, and checklist files without depending on the installed skill location.

## Decision

`uv run plb init` materializes the blueprint documents into `records/project-launch-blueprint/` inside the target project. The operation is idempotent and preserves any existing project-local copies.

## Consequences

- Stage execution can prefer project-local docs while still falling back to repository defaults when needed.
- The target project gains a durable, inspectable record of the operating contract.
- Initialization does not generate business source code.
