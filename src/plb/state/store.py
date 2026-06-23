from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from contextlib import closing
from pathlib import Path

from plb.core.models import (
    ProjectState,
    ReviewRecord,
    ReviewState,
    StageHealth,
    StageLifecycleEvent,
    StageLifecyclePhase,
    StageLifecycleRecord,
    StageRecord,
    StageStatus,
    WorkflowStage,
)
from plb.core.paths import ProjectPaths


@dataclass(slots=True)
class StateSnapshot:
    project_state: ProjectState = ProjectState.UNINITIALIZED
    data: dict[str, object] = field(default_factory=dict)


class StateStore:
    """Thin storage facade for the workflow state."""

    def __init__(self, paths: ProjectPaths):
        self.paths = paths

    def ensure_layout(self) -> None:
        self.paths.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.paths.logs_dir.mkdir(parents=True, exist_ok=True)
        self.paths.audits_dir.mkdir(parents=True, exist_ok=True)
        self.paths.exports_dir.mkdir(parents=True, exist_ok=True)
        self.paths.backups_dir.mkdir(parents=True, exist_ok=True)
        self.paths.projections_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_database()

    def load(self) -> StateSnapshot:
        if not self.paths.state_db.exists():
            return StateSnapshot(data={})

        with closing(sqlite3.connect(self.paths.state_db)) as conn:
            row = conn.execute(
                "select project_state, payload from project_state_snapshot order by id desc limit 1"
            ).fetchone()
            if row is None:
                return StateSnapshot(data={})
            project_state, payload = row
            data = json.loads(payload) if payload else {}
            return StateSnapshot(project_state=ProjectState(project_state), data=data)

    def load_stage(self, stage: WorkflowStage) -> StageRecord:
        if not self.paths.state_db.exists():
            return StageRecord(stage=stage)

        with closing(sqlite3.connect(self.paths.state_db)) as conn:
            row = conn.execute(
                "select status, payload from stage_progress where stage = ?",
                (stage.value,),
            ).fetchone()
            if row is None:
                return StageRecord(stage=stage)
            status, payload = row
            return StageRecord(stage=stage, status=StageStatus(status), payload=json.loads(payload) if payload else {})

    def load_stage_lifecycle(self, stage: WorkflowStage) -> StageLifecycleRecord:
        if not self.paths.state_db.exists():
            return StageLifecycleRecord(stage=stage)

        with closing(sqlite3.connect(self.paths.state_db)) as conn:
            row = conn.execute(
                """
                select phase, health, status, last_event, details, updated_at
                from stage_lifecycle
                where stage = ?
                """,
                (stage.value,),
            ).fetchone()
            if row is None:
                return StageLifecycleRecord(stage=stage)
            phase, health, status, last_event, details, updated_at = row
            return StageLifecycleRecord(
                stage=stage,
                phase=StageLifecyclePhase(phase),
                health=StageHealth(health),
                status=StageStatus(status),
                last_event=str(last_event),
                details=json.loads(details) if details else {},
                updated_at=str(updated_at),
            )

    def stage_lifecycle_events(self, stage: WorkflowStage) -> list[StageLifecycleEvent]:
        if not self.paths.state_db.exists():
            return []
        with closing(sqlite3.connect(self.paths.state_db)) as conn:
            rows = conn.execute(
                """
                select event, phase, health, status, details, created_at
                from stage_lifecycle_events
                where stage = ?
                order by id asc
                """,
                (stage.value,),
            ).fetchall()
        events: list[StageLifecycleEvent] = []
        for event, phase, health, status, details, created_at in rows:
            events.append(
                StageLifecycleEvent(
                    stage=stage,
                    event=str(event),
                    phase=StageLifecyclePhase(phase),
                    health=StageHealth(health),
                    status=StageStatus(status),
                    details=json.loads(details) if details else {},
                    created_at=str(created_at),
                )
            )
        return events

    def set_stage(
        self,
        stage: WorkflowStage,
        status: StageStatus,
        payload: dict[str, object] | None = None,
    ) -> StageRecord:
        self.ensure_layout()
        payload_text = json.dumps(payload or {}, ensure_ascii=False, sort_keys=True)
        now = datetime.now(timezone.utc).isoformat()
        with closing(sqlite3.connect(self.paths.state_db)) as conn:
            conn.execute(
                """
                insert into stage_progress(stage, status, payload, updated_at)
                values (?, ?, ?, ?)
                on conflict(stage) do update set
                    status = excluded.status,
                    payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (stage.value, status.value, payload_text, now),
            )
            conn.commit()
        return StageRecord(stage=stage, status=status, payload=payload or {})

    def record_stage_lifecycle(
        self,
        stage: WorkflowStage,
        event: str,
        *,
        phase: StageLifecyclePhase | None = None,
        health: StageHealth | None = None,
        status: StageStatus | None = None,
        details: dict[str, object] | None = None,
    ) -> StageLifecycleRecord:
        self.ensure_layout()
        current = self.load_stage_lifecycle(stage)
        next_phase = phase or current.phase
        next_health = health or current.health
        next_status = status or current.status
        next_details = dict(current.details)
        if details:
            next_details.update(details)
        now = datetime.now(timezone.utc).isoformat()
        details_text = json.dumps(next_details or {}, ensure_ascii=False, sort_keys=True)
        with closing(sqlite3.connect(self.paths.state_db)) as conn:
            conn.execute(
                """
                insert into stage_lifecycle(stage, phase, health, status, last_event, details, updated_at)
                values (?, ?, ?, ?, ?, ?, ?)
                on conflict(stage) do update set
                    phase = excluded.phase,
                    health = excluded.health,
                    status = excluded.status,
                    last_event = excluded.last_event,
                    details = excluded.details,
                    updated_at = excluded.updated_at
                """,
                (
                    stage.value,
                    next_phase.value,
                    next_health.value,
                    next_status.value,
                    event,
                    details_text,
                    now,
                ),
            )
            conn.execute(
                """
                insert into stage_lifecycle_events(stage, event, phase, health, status, details, created_at)
                values (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    stage.value,
                    event,
                    next_phase.value,
                    next_health.value,
                    next_status.value,
                    details_text,
                    now,
                ),
            )
            conn.commit()
        return StageLifecycleRecord(
            stage=stage,
            phase=next_phase,
            health=next_health,
            status=next_status,
            last_event=event,
            details=next_details,
            updated_at=now,
        )

    def load_review(self, stage: WorkflowStage) -> ReviewRecord:
        if not self.paths.state_db.exists():
            return ReviewRecord(stage=stage)

        with closing(sqlite3.connect(self.paths.state_db)) as conn:
            row = conn.execute(
                "select state, payload from review_progress where stage = ?",
                (stage.value,),
            ).fetchone()
            if row is None:
                return ReviewRecord(stage=stage)
            state, payload = row
            return ReviewRecord(stage=stage, state=ReviewState(state), payload=json.loads(payload) if payload else {})

    def load_implementation_run(self) -> dict[str, object] | None:
        if not self.paths.state_db.exists():
            return None
        with closing(sqlite3.connect(self.paths.state_db)) as conn:
            row = conn.execute(
                "select goal, scope, fresh_reviewer, status, payload from implementation_run where stage = ?",
                (WorkflowStage.IMPLEMENTATION.value,),
            ).fetchone()
            if row is None:
                return None
            goal, scope, fresh_reviewer, status, payload = row
            data = json.loads(payload) if payload else {}
            data.update(
                {
                    "goal": goal,
                    "scope": scope,
                    "fresh_reviewer": bool(fresh_reviewer),
                    "status": status,
                }
            )
            return data

    def save_implementation_run(
        self,
        goal: str,
        scope: str,
        fresh_reviewer: bool,
        payload: dict[str, object],
        status: str = "active",
    ) -> dict[str, object]:
        self.ensure_layout()
        now = datetime.now(timezone.utc).isoformat()
        payload_text = json.dumps(payload or {}, ensure_ascii=False, sort_keys=True)
        with closing(sqlite3.connect(self.paths.state_db)) as conn:
            conn.execute(
                """
                insert into implementation_run(stage, goal, scope, fresh_reviewer, status, payload, created_at, updated_at)
                values (?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(stage) do update set
                    goal = excluded.goal,
                    scope = excluded.scope,
                    fresh_reviewer = excluded.fresh_reviewer,
                    status = excluded.status,
                    payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (
                    WorkflowStage.IMPLEMENTATION.value,
                    goal,
                    scope,
                    1 if fresh_reviewer else 0,
                    status,
                    payload_text,
                    now,
                    now,
                ),
            )
            conn.commit()
        result = dict(payload or {})
        result.update(
            {
                "goal": goal,
                "scope": scope,
                "fresh_reviewer": fresh_reviewer,
                "status": status,
            }
        )
        return result

    def update_implementation_run(
        self,
        patch: dict[str, object],
        status: str | None = None,
    ) -> dict[str, object] | None:
        current = self.load_implementation_run()
        if current is None:
            return None
        current.update(patch)
        next_status = status or str(current.get("status", "active"))
        self.save_implementation_run(
            goal=str(current.get("goal", "")),
            scope=str(current.get("scope", "")),
            fresh_reviewer=bool(current.get("fresh_reviewer", False)),
            payload={k: v for k, v in current.items() if k not in {"goal", "scope", "fresh_reviewer", "status"}},
            status=next_status,
        )
        current["status"] = next_status
        return current

    def set_review(
        self,
        stage: WorkflowStage,
        state: ReviewState,
        payload: dict[str, object] | None = None,
    ) -> ReviewRecord:
        self.ensure_layout()
        payload_text = json.dumps(payload or {}, ensure_ascii=False, sort_keys=True)
        now = datetime.now(timezone.utc).isoformat()
        with closing(sqlite3.connect(self.paths.state_db)) as conn:
            conn.execute(
                """
                insert into review_progress(stage, state, payload, updated_at)
                values (?, ?, ?, ?)
                on conflict(stage) do update set
                    state = excluded.state,
                    payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (stage.value, state.value, payload_text, now),
            )
            conn.commit()
        return ReviewRecord(stage=stage, state=state, payload=payload or {})

    def review_packet_path(self, stage: WorkflowStage) -> Path:
        return self.paths.audits_dir / f"{stage.value}-packet.json"

    def review_result_path(self, stage: WorkflowStage) -> Path:
        return self.paths.audits_dir / f"{stage.value}-review.json"

    def write_review_artifact(self, stage: WorkflowStage, kind: str, payload: dict[str, object]) -> Path:
        self.ensure_layout()
        artifact_path = self.paths.audits_dir / f"{stage.value}-{kind}.json"
        artifact_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        return artifact_path

    def read_review_artifact(self, stage: WorkflowStage, kind: str) -> dict[str, object]:
        artifact_path = self.paths.audits_dir / f"{stage.value}-{kind}.json"
        if not artifact_path.exists():
            return {}
        return json.loads(artifact_path.read_text(encoding="utf-8"))

    def completed_stage_count(self) -> int:
        if not self.paths.state_db.exists():
            return 0
        with closing(sqlite3.connect(self.paths.state_db)) as conn:
            row = conn.execute(
                "select count(*) from stage_progress where status = ?",
                (StageStatus.COMPLETED.value,),
            ).fetchone()
            return int(row[0] if row else 0)

    def ensure_stage_seed(self, stage: WorkflowStage) -> StageRecord:
        record = self.load_stage(stage)
        if record.status == StageStatus.PENDING and record.payload == {} and not self.paths.state_db.exists():
            self.set_stage(stage, StageStatus.PENDING)
            self.record_stage_lifecycle(
                stage,
                "seeded",
                phase=StageLifecyclePhase.SEEDED,
                health=StageHealth.STABLE,
                status=StageStatus.PENDING,
                details={"seeded": True},
            )
        elif record.status == StageStatus.PENDING and not self._stage_exists(stage):
            self.set_stage(stage, StageStatus.PENDING)
            self.record_stage_lifecycle(
                stage,
                "seeded",
                phase=StageLifecyclePhase.SEEDED,
                health=StageHealth.STABLE,
                status=StageStatus.PENDING,
                details={"seeded": True},
            )
        return self.load_stage(stage)

    def save(self, snapshot: StateSnapshot) -> None:
        self.ensure_layout()
        payload = json.dumps(snapshot.data or {}, ensure_ascii=False, sort_keys=True)
        now = datetime.now(timezone.utc).isoformat()
        with closing(sqlite3.connect(self.paths.state_db)) as conn:
            conn.execute(
                """
                insert into project_state_snapshot(project_state, payload, created_at)
                values (?, ?, ?)
                """,
                (snapshot.project_state.value, payload, now),
            )
            conn.commit()

    def set_project_state(self, state: ProjectState, data: dict[str, object] | None = None) -> StateSnapshot:
        snapshot = StateSnapshot(project_state=state, data=data or {})
        self.save(snapshot)
        return snapshot

    def _ensure_database(self) -> None:
        with closing(sqlite3.connect(self.paths.state_db)) as conn:
            conn.execute(
                """
                create table if not exists project_state_snapshot (
                    id integer primary key autoincrement,
                    project_state text not null,
                    payload text not null,
                    created_at text not null
                )
                """
            )
            conn.execute(
                """
                create table if not exists stage_progress (
                    stage text primary key,
                    status text not null,
                    payload text not null,
                    updated_at text not null
                )
                """
            )
            conn.execute(
                """
                create table if not exists stage_lifecycle (
                    stage text primary key,
                    phase text not null,
                    health text not null,
                    status text not null,
                    last_event text not null,
                    details text not null,
                    updated_at text not null
                )
                """
            )
            conn.execute(
                """
                create table if not exists stage_lifecycle_events (
                    id integer primary key autoincrement,
                    stage text not null,
                    event text not null,
                    phase text not null,
                    health text not null,
                    status text not null,
                    details text not null,
                    created_at text not null
                )
                """
            )
            conn.execute(
                """
                create table if not exists review_progress (
                    stage text primary key,
                    state text not null,
                    payload text not null,
                    updated_at text not null
                )
                """
            )
            conn.execute(
                """
                create table if not exists implementation_run (
                    stage text primary key,
                    goal text not null,
                    scope text not null,
                    fresh_reviewer integer not null,
                    status text not null,
                    payload text not null,
                    created_at text not null,
                    updated_at text not null
                )
                """
            )
            conn.commit()

    def _stage_exists(self, stage: WorkflowStage) -> bool:
        if not self.paths.state_db.exists():
            return False
        with closing(sqlite3.connect(self.paths.state_db)) as conn:
            row = conn.execute(
                "select 1 from stage_progress where stage = ?",
                (stage.value,),
            ).fetchone()
            return row is not None
