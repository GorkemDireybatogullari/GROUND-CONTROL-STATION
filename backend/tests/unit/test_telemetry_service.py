"""TelemetryService — thin orchestration on top of the repository."""

from __future__ import annotations

import pytest

from app.core.exceptions import NotFoundError
from app.domain.telemetry import GpsReading, ImuReading, Nav2Plan, Nav2Pose, Quaternion, Vector3
from app.repositories.telemetry_repository import TelemetryRepository
from app.services.telemetry_service import TelemetryService


def test_imu_falls_back_to_zero_default(telemetry_service: TelemetryService) -> None:
    reading = telemetry_service.get_imu()
    assert reading.yaw == 0.0
    assert reading.pitch == 0.0
    assert reading.roll == 0.0


def test_imu_reflects_repository(
    telemetry_repository: TelemetryRepository, telemetry_service: TelemetryService
) -> None:
    telemetry_repository.set_imu(ImuReading(yaw=1.0))
    assert telemetry_service.get_imu().yaw == 1.0


def test_gps_default(telemetry_service: TelemetryService) -> None:
    reading = telemetry_service.get_gps()
    assert reading == GpsReading()


def test_nav2_plan_raises_when_empty(telemetry_service: TelemetryService) -> None:
    with pytest.raises(NotFoundError):
        telemetry_service.get_nav2_plan()


def test_nav2_plan_returns_populated(
    telemetry_repository: TelemetryRepository, telemetry_service: TelemetryService
) -> None:
    plan = Nav2Plan(
        poses=[
            Nav2Pose(
                position=Vector3(x=1, y=2, z=3),
                orientation=Quaternion(),
                header=__import__("app.domain.telemetry", fromlist=["Nav2Header"]).Nav2Header(),
            )
        ],
        pose_count=1,
    )
    telemetry_repository.set_nav2_plan(plan)
    assert telemetry_service.get_nav2_plan().pose_count == 1


def test_snapshot_includes_status_fields(
    telemetry_repository: TelemetryRepository, telemetry_service: TelemetryService
) -> None:
    telemetry_repository.set_armed(True)
    telemetry_repository.set_mode("MANUAL")
    snap = telemetry_service.snapshot()
    assert snap.armed is True
    assert snap.mode == "MANUAL"
