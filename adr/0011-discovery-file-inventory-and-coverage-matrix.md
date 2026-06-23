# ADR 0011: Discovery File Inventory and Coverage Matrix

## Status

Accepted

## Context

The discovery stage consumes user-prepared `analysis/` assets. The stage must not only reject missing required inputs; it also needs a reproducible way to prove that every file under `analysis/` was accounted for during review and that no file was silently ignored or invented by the model.

Prompt instructions alone are not sufficient for this guarantee because they can be bypassed by implementation drift, prompt edits, or accidental reviewer context leakage.

## Decision

Discovery now generates a file-level inventory for `analysis/` and a matching coverage template before review is executed.

The workflow must:

- recursively enumerate every file under `analysis/`
- store the result as `analysis_inventory`
- create a one-to-one `analysis_coverage_template` entry for each inventory item
- include both structures in the discovery review packet
- fail review when the inventory and coverage template diverge
- require the validation report to surface any unmapped or explicitly excluded file

The review worker must enforce the packet shape, inventory completeness, coverage-row alignment, and summary counts as hard checks.

## Consequences

- Discovery can prove file-level accounting instead of only asserting that `analysis/` existed.
- Unmapped files become an explicit review concern instead of a hidden omission.
- The model still performs abstraction, but it operates on a frozen, code-generated file list rather than a loose folder reference.
- Prompt templates remain useful as guidance, but the enforcement boundary is the code path that builds the packet and the worker that validates it.
- This ADR is the discovery-stage expression of the broader freeze-first / inventory-first / verify-second methodology.
