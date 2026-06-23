# ADR 0012: Domain Input Inventory and Coverage Matrix

## Status

Accepted

## Context

The domain stage consumes already-verified discovery outputs plus auxiliary evidence. That input set is larger and more heterogeneous than a single source document, so the stage needs a structured way to account for every item it sees and to make exclusions explicit.

Prompt instructions alone are not enough to guarantee that every upstream input is considered exactly once and either mapped, excluded, or marked for human review.

The same accounting problem repeats in later stages: each stage has its own frozen stage-document set, and state/api/design/slice/gates also consume approved upstream artifacts that need to be enumerated and frozen before review.

## Decision

Domain should perform file-level or item-level accounting over its inputs before finalizing the model.

The broader workflow should treat input accounting as a stage-level contract, not a one-off domain trick:

- every stage freezes a stage-document inventory and matching coverage template
- domain additionally freezes a domain input inventory and coverage matrix
- later stages additionally freeze an upstream input inventory and coverage matrix built from approved upstream artifacts

The workflow must:

- enumerate all domain inputs into a stable `domain_input_inventory`
- create a one-to-one `domain_coverage_matrix` entry for each inventory item
- include both structures in the domain validation report
- surface intentionally excluded or unclear inputs in `unmapped_inputs`
- fail validation when inventory and coverage diverge
- apply the same hard accounting pattern to stage documents and approved upstream inputs in later stages

## Consequences

- Domain can prove that every upstream input was explicitly considered.
- Unclear evidence no longer disappears into a vague “auxiliary only” bucket.
- The stage stays aligned with discovery: enumerate first, abstract second, verify third.
- Prompt templates remain guidance, but accounting is a contract in the output schema and validation rules.
- The same freeze-first / validate-second pattern now extends to state, api, design, slice, and gates without relying on prompt-only discipline.
- This ADR is one instance of the broader freeze-first / inventory-first / verify-second methodology recorded in ADR 0013.
