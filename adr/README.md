# Architecture Decision Records

This directory captures the architectural decisions behind the current implementation.

## Reading Order

1. `0001-materialize-project-documentation.md`
2. `0002-stage-prompt-bundle-and-isolated-worker.md`
3. `0003-discovery-input-precheck-and-closed-world-init.md`
4. `0004-unified-cli-and-natural-language-routing.md`
5. `0005-domain-stage-boundary-and-approved-inputs.md`
6. `0006-state-stage-lifecycle-and-state-machine-boundary.md`
7. `0007-api-stage-contract-synthesis-and-validation.md`
8. `0008-design-stage-system-contract-and-review-fence.md`
9. `0009-slice-stage-vertical-integration-and-execution-order.md`
10. `0010-gates-stage-release-fence-before-implementation.md`
11. `0011-discovery-file-inventory-and-coverage-matrix.md`
12. `0012-domain-input-inventory-and-coverage-matrix.md`
13. `0013-freeze-first-inventory-first-verify-second-methodology.md`
14. `0014-coverage-driven-development-and-explicit-invariants.md`

## Purpose

The ADRs explain why the initialization flow materializes project documentation, why stage execution uses a unified prompt bundle, why discovery is blocked until user-prepared inputs exist, why discovery also needs file-level inventory and coverage accounting, why domain also needs input inventory and coverage accounting, why the remaining stages inherit the same review contract, why the workflow adopts a freeze-first / inventory-first / verify-second methodology, why the project uses coverage-driven development with explicit invariants, and why both CLI and natural language route through the same workflow.
