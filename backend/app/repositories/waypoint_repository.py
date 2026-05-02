"""JSON-file backed waypoint persistence."""

from __future__ import annotations

import json
from pathlib import Path

from app.core.exceptions import StorageError
from app.domain.waypoint import WaypointMission


class WaypointRepository:
    def __init__(self, path: Path) -> None:
        self._path = path

    def save(self, mission: WaypointMission) -> WaypointMission:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            payload = mission.model_dump(mode="json")
            self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"Could not write waypoints: {exc}") from exc
        return mission

    def load(self) -> WaypointMission | None:
        if not self._path.exists():
            return None
        try:
            raw = self._path.read_text(encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"Could not read waypoints: {exc}") from exc

        try:
            return WaypointMission.model_validate_json(raw)
        except ValueError:
            return None
