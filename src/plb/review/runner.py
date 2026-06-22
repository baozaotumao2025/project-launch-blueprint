from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from plb.core.models import ReviewState, WorkflowStage


@dataclass(slots=True)
class ReviewPacket:
    stage: WorkflowStage
    target: str
    review_state: ReviewState = ReviewState.PACKET_CREATED
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ReviewRunResult:
    packet: ReviewPacket
    result_path: Path | None = None
    summary: str = ""
    review_state: ReviewState = ReviewState.REVIEW_RUNNING


class ReviewRunner(Protocol):
    def run(self, packet: ReviewPacket) -> ReviewRunResult: ...


@dataclass(slots=True)
class FreshSubagentReviewRunner:
    output_dir: Path

    def run(self, packet: ReviewPacket) -> ReviewRunResult:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        packet_path = self.output_dir / f"{packet.stage.value}-packet.json"
        result_path = self.output_dir / f"{packet.stage.value}-review.json"
        packet_path.write_text(
            json.dumps(
                {
                    "stage": packet.stage.value,
                    "target": packet.target,
                    "review_state": packet.review_state.value,
                    "payload": packet.payload,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "plb.review.worker",
                "--packet",
                str(packet_path),
                "--result",
                str(result_path),
            ],
            check=True,
        )
        result_payload = json.loads(result_path.read_text(encoding="utf-8"))
        return ReviewRunResult(
            packet=packet,
            result_path=result_path,
            summary=str(result_payload.get("summary", "")),
            review_state=ReviewState(str(result_payload.get("review_state", ReviewState.REVIEW_RUNNING.value))),
        )


FilesystemReviewRunner = FreshSubagentReviewRunner


def build_review_packet(stage: WorkflowStage, target: str, payload: dict[str, Any] | None = None) -> ReviewPacket:
    return ReviewPacket(stage=stage, target=target, payload=payload or {})
