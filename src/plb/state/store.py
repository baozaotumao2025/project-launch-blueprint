from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from plb.core.models import ProjectState, ReviewRecord, ReviewState, StageRecord, StageStatus, WorkflowStage
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

        with sqlite3.connect(self.paths.state_db) as conn:
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

        with sqlite3.connect(self.paths.state_db) as conn:
            row = conn.execute(
                "select status, payload from stage_progress where stage = ?",
                (stage.value,),
            ).fetchone()
            if row is None:
                return StageRecord(stage=stage)
            status, payload = row
            return StageRecord(stage=stage, status=StageStatus(status), payload=json.loads(payload) if payload else {})

    def set_stage(
        self,
        stage: WorkflowStage,
        status: StageStatus,
        payload: dict[str, object] | None = None,
    ) -> StageRecord:
        self.ensure_layout()
        payload_text = json.dumps(payload or {}, ensure_ascii=False, sort_keys=True)
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.paths.state_db) as conn:
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

    def load_review(self, stage: WorkflowStage) -> ReviewRecord:
        if not self.paths.state_db.exists():
            return ReviewRecord(stage=stage)

        with sqlite3.connect(self.paths.state_db) as conn:
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
        with sqlite3.connect(self.paths.state_db) as conn:
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
        with sqlite3.connect(self.paths.state_db) as conn:
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
        with sqlite3.connect(self.paths.state_db) as conn:
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
        with sqlite3.connect(self.paths.state_db) as conn:
            row = conn.execute(
                "select count(*) from stage_progress where status = ?",
                (StageStatus.COMPLETED.value,),
            ).fetchone()
            return int(row[0] if row else 0)

    def ensure_stage_seed(self, stage: WorkflowStage) -> StageRecord:
        record = self.load_stage(stage)
        if record.status == StageStatus.PENDING and record.payload == {} and not self.paths.state_db.exists():
            self.set_stage(stage, StageStatus.PENDING)
        elif record.status == StageStatus.PENDING and not self._stage_exists(stage):
            self.set_stage(stage, StageStatus.PENDING)
        return self.load_stage(stage)

    def save(self, snapshot: StateSnapshot) -> None:
        self.ensure_layout()
        payload = json.dumps(snapshot.data or {}, ensure_ascii=False, sort_keys=True)
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.paths.state_db) as conn:
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
        with sqlite3.connect(self.paths.state_db) as conn:
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
        with sqlite3.connect(self.paths.state_db) as conn:
            row = conn.execute(
                "select 1 from stage_progress where stage = ?",
                (stage.value,),
            ).fetchone()
            return row is not None
