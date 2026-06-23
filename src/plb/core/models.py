from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProjectState(str, Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    READY_FOR_IMPLEMENTATION = "ready_for_implementation"
    IMPLEMENTED = "implemented"
    PUBLISHED = "published"


class ArtifactState(str, Enum):
    DRAFT = "draft"
    STRUCTURALLY_VALID = "structurally_valid"
    SEMANTIC_REVIEW = "semantic_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    STALE = "stale"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class ReviewState(str, Enum):
    PACKET_CREATED = "packet_created"
    REVIEW_RUNNING = "review_running"
    PASSED = "passed"
    FAILED = "failed"
    NEEDS_REVISION = "needs_revision"
    RECORDED = "recorded"


class WorkflowStage(str, Enum):
    DISCOVERY = "discovery"
    DOMAIN = "domain"
    STATE = "state"
    API = "api"
    DESIGN = "design"
    SLICE = "slice"
    GATES = "gates"
    IMPLEMENTATION = "implementation"


class StageStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    NEEDS_REVISION = "needs_revision"


class StageLifecyclePhase(str, Enum):
    SEEDED = "seeded"
    PLANNED = "planned"
    PACKET_CREATED = "packet_created"
    REVIEW_RUNNING = "review_running"
    REVIEW_RECORDED = "review_recorded"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    STALE = "stale"
    FAILED = "failed"


class StageHealth(str, Enum):
    STABLE = "stable"
    DEGRADED = "degraded"
    BLOCKED = "blocked"
    STALE = "stale"
    FAILED = "failed"


@dataclass(slots=True)
class CommandResult:
    status: str
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StageRecord:
    stage: WorkflowStage
    status: StageStatus = StageStatus.PENDING
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ReviewRecord:
    stage: WorkflowStage
    state: ReviewState = ReviewState.PACKET_CREATED
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StageLifecycleRecord:
    stage: WorkflowStage
    phase: StageLifecyclePhase = StageLifecyclePhase.SEEDED
    health: StageHealth = StageHealth.STABLE
    status: StageStatus = StageStatus.PENDING
    last_event: str = "seeded"
    details: dict[str, Any] = field(default_factory=dict)
    updated_at: str = ""


@dataclass(slots=True)
class StageLifecycleEvent:
    stage: WorkflowStage
    event: str
    phase: StageLifecyclePhase
    health: StageHealth
    status: StageStatus
    details: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""


@dataclass(slots=True)
class GoalEntry:
    goal_id: str
    order: int
    goal: str
    depends_on: list[str] = field(default_factory=list)
    status: str = "pending"
    regression_scope: list[str] = field(default_factory=list)
    rollback_point: str = ""
    evidence: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RegressionCheck:
    after_goal: str
    what_to_rerun: list[str] = field(default_factory=list)
    why: str = ""
    pass_criteria: list[str] = field(default_factory=list)
    rollback_point: str = ""
    status: str = "pending"
    evidence: list[str] = field(default_factory=list)


@dataclass(slots=True)
class GoalProgress:
    total_goals: int = 0
    completed_goals: int = 0
    current_goal: str = ""
    next_goal: str = ""


@dataclass(slots=True)
class ImplementationRun:
    goal: str
    scope: str
    fresh_reviewer: bool = False
    goal_registry: list[GoalEntry] = field(default_factory=list)
    goal_progress: GoalProgress = field(default_factory=GoalProgress)
    regression_checks: list[RegressionCheck] = field(default_factory=list)
    blocked_items: list[str] = field(default_factory=list)
    rollback_point: str = ""
    status: str = "active"
