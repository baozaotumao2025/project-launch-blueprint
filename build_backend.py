from __future__ import annotations

import base64
import hashlib
import os
import tempfile
import zipfile
from pathlib import Path

NAME = "plb"
VERSION = "0.1.0"
PY_TAG = "py3"
ABI_TAG = "none"
PLATFORM_TAG = "any"
DIST_INFO = f"{NAME}-{VERSION}.dist-info"
WHEEL_FILENAME = f"{NAME}-{VERSION}-{PY_TAG}-{ABI_TAG}-{PLATFORM_TAG}.whl"

ROOT = Path(__file__).resolve().parent
SRC_ROOT = ROOT / "src"


def _metadata_text() -> str:
    return "\n".join(
        [
            "Metadata-Version: 2.3",
            f"Name: {NAME}",
            f"Version: {VERSION}",
            "Summary: Project Launch Blueprint CLI scaffold",
            "Requires-Python: >=3.11",
            "",
        ]
    )


def _wheel_text() -> str:
    return "\n".join(
        [
            "Wheel-Version: 1.0",
            "Generator: plb-build-backend",
            "Root-Is-Purelib: true",
            f"Tag: {PY_TAG}-{ABI_TAG}-{PLATFORM_TAG}",
            "",
        ]
    )


def _entry_points_text() -> str:
    return "\n".join(["[console_scripts]", "plb = plb.cli:main", ""])


def _editable_pth_text() -> str:
    return str(SRC_ROOT) + os.linesep


def _hash_bytes(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    return "sha256=" + base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def _write_metadata_tree(target: Path) -> None:
    dist_info = target / DIST_INFO
    dist_info.mkdir(parents=True, exist_ok=True)
    (dist_info / "METADATA").write_text(_metadata_text(), encoding="utf-8")
    (dist_info / "WHEEL").write_text(_wheel_text(), encoding="utf-8")
    (dist_info / "entry_points.txt").write_text(_entry_points_text(), encoding="utf-8")


def _record_entries(files: list[tuple[str, bytes]]) -> str:
    rows: list[str] = []
    for path, data in files:
        rows.append(f"{path},{_hash_bytes(data)},{len(data)}")
    rows.append(f"{DIST_INFO}/RECORD,,")
    return "\n".join(rows) + "\n"


def _build_wheel_archive(wheel_dir: str, editable: bool) -> str:
    wheel_dir_path = Path(wheel_dir)
    wheel_dir_path.mkdir(parents=True, exist_ok=True)
    archive_path = wheel_dir_path / WHEEL_FILENAME

    payloads: list[tuple[str, bytes]] = []
    payloads.append((f"{DIST_INFO}/METADATA", _metadata_text().encode("utf-8")))
    payloads.append((f"{DIST_INFO}/WHEEL", _wheel_text().encode("utf-8")))
    payloads.append((f"{DIST_INFO}/entry_points.txt", _entry_points_text().encode("utf-8")))
    if editable:
        payloads.append((f"{NAME}.pth", _editable_pth_text().encode("utf-8")))

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_root = Path(tmpdir)
        record_text = _record_entries(payloads)
        (temp_root / DIST_INFO).mkdir(parents=True, exist_ok=True)
        (temp_root / DIST_INFO / "RECORD").write_text(record_text, encoding="utf-8")

        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for rel_path, data in payloads:
                zf.writestr(rel_path, data)
            zf.writestr(f"{DIST_INFO}/RECORD", record_text)

    return archive_path.name


def get_requires_for_build_wheel(config_settings=None):
    return []


def get_requires_for_build_editable(config_settings=None):
    return []


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    target = Path(metadata_directory)
    _write_metadata_tree(target)
    return DIST_INFO


def prepare_metadata_for_build_editable(metadata_directory, config_settings=None):
    target = Path(metadata_directory)
    _write_metadata_tree(target)
    return DIST_INFO


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    return _build_wheel_archive(wheel_directory, editable=False)


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    return _build_wheel_archive(wheel_directory, editable=True)

