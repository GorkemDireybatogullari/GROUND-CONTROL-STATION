"""JSON-file backed color code persistence."""

from __future__ import annotations

import json
from pathlib import Path

from app.core.exceptions import StorageError
from app.domain.color_code import ColorCodeRecord


class ColorCodeRepository:
    def __init__(self, path: Path) -> None:
        self._path = path

    def save(self, record: ColorCodeRecord) -> ColorCodeRecord:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            payload = record.model_dump(mode="json")
            self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"Could not write color code: {exc}") from exc
        return record

    def load(self) -> ColorCodeRecord | None:
        if not self._path.exists():
            return None
        try:
            raw = self._path.read_text(encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"Could not read color code: {exc}") from exc

        try:
            return ColorCodeRecord.model_validate_json(raw)
        except ValueError:
            return None
