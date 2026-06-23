# Stage Map

> 这张表把每个 stage 的学习材料、决策记录和阅读目标放在一起，方便按阶段快速定位。

| Stage | Learn | Input | Output | ADR | Methodology Dir | Key Code |
| --- | --- | --- | --- | --- | --- | --- |
| discovery | [Tutorial](./discovery-implementation-tutorial.md) | `analysis/` user-prepared inputs + file inventory + stage docs inventory | discovery boundary + review packet | [ADR 0003](../../adr/0003-discovery-input-precheck-and-closed-world-init.md), [ADR 0011](../../adr/0011-discovery-file-inventory-and-coverage-matrix.md) | `discovery/` | [`workflow/prompting.py`](../../src/plb/workflow/prompting.py), [`commands/review.py`](../../src/plb/commands/review.py), [`review/worker.py`](../../src/plb/review/worker.py) |
| domain | [Tutorial](./domain-implementation-tutorial.md) | approved discovery output + input inventory + stage docs inventory | domain boundary | [ADR 0005](../../adr/0005-domain-stage-boundary-and-approved-inputs.md), [ADR 0012](../../adr/0012-domain-input-inventory-and-coverage-matrix.md) | `domain-model/` | [`commands/stage.py`](../../src/plb/commands/stage.py), [`commands/review.py`](../../src/plb/commands/review.py), [`workflow/prompting.py`](../../src/plb/workflow/prompting.py) |
| state | [Tutorial](./state-implementation-tutorial.md) | approved discovery + domain output + stage docs inventory + upstream input inventory | state machine + lifecycle rules | [ADR 0006](../../adr/0006-state-stage-lifecycle-and-state-machine-boundary.md) | `state-machine/` | [`state/store.py`](../../src/plb/state/store.py), [`commands/stage.py`](../../src/plb/commands/stage.py) |
| api | [Tutorial](./api-implementation-tutorial.md) | approved discovery + domain + state output + stage docs inventory + upstream input inventory | API contract | [ADR 0007](../../adr/0007-api-stage-contract-synthesis-and-validation.md) | `api-contract/` | [`workflow/prompting.py`](../../src/plb/workflow/prompting.py), [`commands/review.py`](../../src/plb/commands/review.py) |
| design | [Tutorial](./design-implementation-tutorial.md) | approved API + upstream context + stage docs inventory + upstream input inventory | design-system rules | [ADR 0008](../../adr/0008-design-stage-system-contract-and-review-fence.md) | `design-system/` | [`workflow/prompting.py`](../../src/plb/workflow/prompting.py), [`commands/review.py`](../../src/plb/commands/review.py) |
| slice | [Tutorial](./slice-implementation-tutorial.md) | approved domain + state + api + design + stage docs inventory + upstream input inventory | vertical slice execution order | [ADR 0009](../../adr/0009-slice-stage-vertical-integration-and-execution-order.md) | `vertical-slice/` | [`commands/stage.py`](../../src/plb/commands/stage.py), [`commands/review.py`](../../src/plb/commands/review.py) |
| gates | [Tutorial](./gates-implementation-tutorial.md) | approved upstream stages + stage docs inventory + upstream input inventory | implementation release fence | [ADR 0010](../../adr/0010-gates-stage-release-fence-before-implementation.md) | `quality-gates/` | [`commands/stage.py`](../../src/plb/commands/stage.py), [`commands/review.py`](../../src/plb/commands/review.py) |

## How To Use This Map

1. Pick the stage you want to learn.
2. Open the tutorial first.
3. Read the ADR second to understand the rationale.
4. Read the key code files to see how the stage is wired.
5. Open the stage directory files if you need the detailed method, rules, schema, or checklist.

The map is intentionally ordered to match the workflow progression.
