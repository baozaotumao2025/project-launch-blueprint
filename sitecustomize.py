from __future__ import annotations

import os


def _enable_subprocess_coverage() -> None:
    if not os.environ.get("COVERAGE_PROCESS_START"):
        return
    try:
        import coverage
    except Exception:
        return
    coverage.process_startup()


_enable_subprocess_coverage()
