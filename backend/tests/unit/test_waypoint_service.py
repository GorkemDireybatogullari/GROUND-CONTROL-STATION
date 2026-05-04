"""WaypointService + WaypointRepository persistence."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.core.exceptions import StorageError
from app.domain.waypoint import Waypoint
from app.repositories.waypoint_repository import WaypointRepository
from app.services.waypoint_service import WaypointService


def test_save_persists_to_disk(
    waypoint_service: WaypointService, waypoint_repository: WaypointRepository
) -> None:
    waypoints = [Waypoint(latitude=41.0, longitude=29.0)]
    mission = waypoint_service.save_mission(waypoints, "trial")

    assert mission.mission_name == "trial"
    assert mission.waypoints[0].latitude == 41.0

    loaded = waypoint_repository.load()
    assert loaded is not None
    assert loaded.mission_name == "trial"
    assert loaded.waypoints[0].longitude == 29.0


def test_save_writes_indented_json(
    waypoint_service: WaypointService, waypoint_repository: WaypointRepository
) -> None:
    waypoint_service.save_mission([Waypoint(latitude=0, longitude=0)], "m")
    raw = waypoint_repository._path.read_text()  # noqa: SLF001
    parsed = json.loads(raw)
    assert "waypoints" in parsed
    assert "\n" in raw  # indent=2 → multi-line


def test_load_returns_none_when_file_missing(waypoint_repository: WaypointRepository) -> None:
    assert waypoint_repository.load() is None


def test_load_returns_none_when_file_corrupt(
    waypoint_repository: WaypointRepository, tmp_path: Path
) -> None:
    waypoint_repository._path.parent.mkdir(parents=True, exist_ok=True)  # noqa: SLF001
    waypoint_repository._path.write_text("{not json")  # noqa: SLF001
    assert waypoint_repository.load() is None


def test_save_rejects_invalid_latitude() -> None:
    with pytest.raises(ValueError):
        Waypoint(latitude=999.0, longitude=0.0)


def test_save_rejects_invalid_longitude() -> None:
    with pytest.raises(ValueError):
        Waypoint(latitude=0.0, longitude=-200.0)


def test_save_rejects_blank_mission_name(waypoint_service: WaypointService) -> None:
    with pytest.raises(ValueError):
        waypoint_service.save_mission([Waypoint(latitude=0, longitude=0)], "   ")


def test_storage_error_when_path_unwritable(tmp_path: Path) -> None:
    # Point the repo at a file path whose parent cannot be created (a regular file).
    blocker = tmp_path / "blocker"
    blocker.write_text("x")
    repo = WaypointRepository(blocker / "child" / "waypoints.json")
    service = WaypointService(repo)
    with pytest.raises(StorageError):
        service.save_mission([Waypoint(latitude=0, longitude=0)], "x")
