# Workflow State

> 这份文档定义 `project-launch-blueprint` 的权威状态模型。  
> 它借鉴 revision-aware workflow 的思路：状态必须可追踪、可回退、可使下游失效。

## 1. State Layers

### 1.1 Project State

项目级状态：

- `uninitialized`
- `initialized`
- `in_progress`
- `blocked`
- `ready_for_implementation`
- `implemented`
- `published`

### 1.2 Stage Artifact State

每个阶段产物的 revision 状态：

- `draft`
- `structurally_valid`
- `semantic_review`
- `approved`
- `rejected`
- `stale`
- `superseded`
- `archived`

### 1.3 Review State

每次审查的记录状态：

- `packet_created`
- `review_running`
- `passed`
- `failed`
- `needs_revision`
- `recorded`

## 2. Stage Registry

固定阶段顺序：

1. `discovery`
2. `domain`
3. `state`
4. `api`
5. `design`
6. `slice`
7. `gates`
8. `implementation`

每个 stage 都有：

- `stage_id`
- `order`
- `inputs`
- `outputs`
- `status`
- `revision`
- `review_state`
- `rollback_point`
- `regression_scope`
- `evidence`

## 3. Transition Rules

### 3.1 Project Transitions

```txt
uninitialized -> initialized -> in_progress
in_progress -> blocked
blocked -> in_progress
in_progress -> ready_for_implementation
ready_for_implementation -> implemented
implemented -> published
```

### 3.2 Stage Transitions

```txt
draft -> structurally_valid -> semantic_review -> approved
draft -> rejected
structurally_valid -> draft
semantic_review -> draft
approved -> stale
approved -> superseded
stale -> draft
rejected -> draft
superseded -> archived
```

### 3.3 Downstream Invalidations

When an upstream stage revision changes:

- the new upstream revision starts in `draft`
- downstream approved revisions become `stale`
- downstream stages cannot advance until upstream is re-approved
- stale downstream stages may remain editable, but they cannot pass the next gate

## 4. Validation Flow

Every stage must pass the same three-step validation chain:

1. deterministic validation
2. isolated LLM review
3. explicit approval or rejection

### 4.1 Deterministic Validation

Checks include:

- required fields present
- output schema satisfied
- dependencies complete
- stage boundaries respected
- no upstream leapfrogging

### 4.2 Isolated LLM Review

The review packet must:

- include only approved upstream inputs
- exclude generation context
- include counterexample prompts
- include rollback points

### 4.3 Approval Rule

A stage may become `approved` only when:

- deterministic validation passes
- isolated LLM review passes
- counterexamples fail to break the artifact
- rollback point is known
- review result has been recorded from the worker verdict
- the final approval step does not override the worker verdict

## 5. Regression Rule

Every successful stage completion must trigger regression against all previously approved downstream-relevant outputs.

Examples:

- after `domain`, rerun `discovery` regression checks
- after `state`, rerun `discovery + domain` regression checks
- after `api`, rerun `discovery + domain + state` regression checks
- after `design`, rerun `api` alignment checks
- after `slice`, rerun `design + api + state` integration checks
- after `gates`, rerun the full non-implementation pipeline
- after `implementation`, rerun the full release matrix

## 6. Storage Contract

Canonical state storage should live under the target project root:

```text
.project-launch-blueprint/state.db
.project-launch-blueprint/audits/
.project-launch-blueprint/exports/
.project-launch-blueprint/logs/
.project-launch-blueprint/backups/
```

Suggested database entities:

- project
- stage
- revision
- transition
- review_packet
- review_result
- dependency
- audit_event

## 7. Read Model

The CLI should be able to answer these questions directly from state:

- 当前项目是否已初始化
- 当前卡在哪个 stage
- 一共有多少 stage
- 每个 stage 当前 revision 是什么
- 哪些 stage 已批准
- 哪些 stage 因上游变化变 stale
- 当前 should run 哪个 regression
- 最近一次 LLM 审查结果是什么
- 回退点在哪里

## 8. Non-Negotiable Rules

- 不允许文档状态替代真实状态
- 不允许跳过 isolated review
- 不允许在上游未批准时推进下游
- 不允许静默覆盖 revision
- 不允许不记录回退点
- 不允许没有证据就进入 approved
