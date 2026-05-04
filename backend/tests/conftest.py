"""Shared pytest fixtures.

The ROS bridge is intentionally bypassed in tests — we drive the telemetry
repository directly so tests are deterministic and don't require a running
ROS2 stack.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_app
from app.repositories.color_code_repository import ColorCodeRepository
from app.repositories.telemetry_repository import TelemetryRepository
from app.repositories.waypoint_repository import WaypointRepository
from app.services.color_code_service import ColorCodeService
from app.services.mission_service import MissionService
from app.services.telemetry_service import TelemetryService
from app.services.waypoint_service import WaypointService


@pytest.fixture
def tmp_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Settings:
    """Settings rooted at a tmp dir so disk writes don't pollute the repo."""
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    settings = Settings(
        data_dir=tmp_path / "data",
        ros_nodes_dir=tmp_path / "ros_nodes",
        cors_allowed_origins=["http://localhost:5173"],
    )
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.ros_nodes_dir.mkdir(parents=True, exist_ok=True)
    get_settings.cache_clear()
    monkeypatch.setattr("app.core.config.get_settings", lambda: settings)
    # `app.main` re-exports get_settings; the lifespan reads through that
    # binding, so patch it there too.
    monkeypatch.setattr("app.main.get_settings", lambda: settings)
    return settings


@pytest.fixture
def telemetry_repository() -> TelemetryRepository:
    return TelemetryRepository()


@pytest.fixture
def waypoint_repository(tmp_settings: Settings) -> WaypointRepository:
    return WaypointRepository(tmp_settings.waypoints_path)


@pytest.fixture
def color_code_repository(tmp_settings: Settings) -> ColorCodeRepository:
    return ColorCodeRepository(tmp_settings.color_code_path)


@pytest.fixture
def telemetry_service(telemetry_repository: TelemetryRepository) -> TelemetryService:
    return TelemetryService(telemetry_repository)


@pytest.fixture
def waypoint_service(waypoint_repository: WaypointRepository) -> WaypointService:
    return WaypointService(waypoint_repository)


@pytest.fixture
def color_code_service(color_code_repository: ColorCodeRepository) -> ColorCodeService:
    return ColorCodeService(color_code_repository)


@pytest.fixture
def mission_service(tmp_settings: Settings) -> MissionService:
    return MissionService(
        waypoint_script=tmp_settings.waypoint_script_path,
        color_code_script=tmp_settings.color_code_script_path,
        timeout_seconds=tmp_settings.mission_timeout_seconds,
    )


@pytest.fixture
def app(
    tmp_settings: Settings,  # noqa: ARG001 — patches get_settings via fixture side-effect
    telemetry_repository: TelemetryRepository,
    waypoint_repository: WaypointRepository,
    color_code_repository: ColorCodeRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> FastAPI:
    """FastAPI app wired through the real lifespan, but with the ROS bridge stubbed.

    Letting the real lifespan run is important: FastAPI/Starlette finalise the
    middleware (including the user exception handlers) on first request, and
    the lifespan run gives a deterministic startup. We just stop the bridge
    from trying to import rclpy.
    """
    monkeypatch.setattr("app.ros.bridge.RosBridge.start", lambda _self: False)
    monkeypatch.setattr("app.ros.bridge.RosBridge.stop", lambda _self: None)

    # Pre-create the repositories the lifespan would otherwise build, so tests
    # can interact with the same instances the API sees.
    monkeypatch.setattr(
        "app.main.TelemetryRepository", lambda: telemetry_repository
    )
    monkeypatch.setattr(
        "app.main.WaypointRepository", lambda _path: waypoint_repository
    )
    monkeypatch.setattr(
        "app.main.ColorCodeRepository", lambda _path: color_code_repository
    )

    return create_app()


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
