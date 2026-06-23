# ADR 0013: Freeze-First, Inventory-First, Verify-Second Methodology

## Status

Accepted

## Context

Across the workflow, the recurring failure mode is the same: a stage sees upstream material, but the review path does not freeze that material into a reproducible inventory before abstraction begins. That makes omissions, accidental duplication, and hallucinated “coverage” too easy.

Prompt-only guidance is not enough to protect against this class of error because prompts can drift, context can leak, and the reviewer can silently infer missing items.

## Decision

Adopt a single cross-stage methodology:

- freeze the relevant input set before review or implementation
- enumerate the frozen inputs into a stable inventory
- create a one-to-one coverage matrix for that inventory
- include both structures in the packet, report, or implementation plan
- make the worker or implementation path enforce the inventory/coverage alignment
- treat prompt instructions as guidance only, not as the enforcement boundary

This methodology applies as follows:

- `discovery` freezes file-level `analysis_inventory`
- `domain` freezes `domain_input_inventory`
- `state`, `api`, `design`, `slice`, and `gates` freeze approved upstream input inventories
- `implementation` freezes the approved upstream input inventory for the goal-driven plan

The same pattern also applies to the stage document set for each stage.

## Consequences

- The workflow can prove that inputs were seen, not merely assumed.
- Inventory and coverage become explicit contracts instead of reviewer memory.
- The same anti-hallucination mechanism works across all stages, not just discovery.
- Enforcement lives in code paths and validation workers, while prompts remain explainers rather than guarantees.
- Future stage work can inherit the same pattern without reinventing its own accounting rules.
