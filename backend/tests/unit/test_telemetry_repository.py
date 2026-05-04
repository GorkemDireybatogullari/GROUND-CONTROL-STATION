"""TelemetryRepository: in-memory store correctness + thread safety."""

from __future__ import annotations

import threading

from app.domain.telemetry import GpsReading, ImuReading, Nav2Plan, OdometryReading, Vector3
from app.repositories.telemetry_repository import TelemetryRepository


def test_returns_none_until_written(telemetry_repository: TelemetryRepository) -> None:
    assert telemetry_repository.get_imu() is None
    assert telemetry_repository.get_gps() is None
    assert telemetry_repository.get_odometry() is None
    assert telemetry_repository.get_nav2_plan() is None


def test_zero_defaults_for_scalars(telemetry_repository: TelemetryRepository) -> None:
    assert telemetry_repository.get_linear_x() == 0.0
    assert telemetry_repository.get_angular_z() == 0.0
    status = telemetry_repository.get_status()
    assert status.armed is False
    assert status.mode == "UNKNOWN"


def test_round_trip_imu_gps_odom(telemetry_repository: TelemetryRepository) -> None:
    telemetry_repository.set_imu(ImuReading(yaw=1.0, pitch=2.0, roll=3.0))
    telemetry_repository.set_gps(GpsReading(latitude=41.0, longitude=29.0, altitude=10.0))
    telemetry_repository.set_odometry(
        OdometryReading(
            linear_velocity=Vector3(x=1.0),
            angular_velocity=Vector3(z=0.5),
            position=Vector3(x=10.0, y=20.0),
        )
    )
    assert telemetry_repository.get_imu() == ImuReading(yaw=1.0, pitch=2.0, roll=3.0)
    assert telemetry_repository.get_gps().latitude == 41.0
    assert telemetry_repository.get_odometry().position.x == 10.0


def test_status_partial_updates_preserve_other_field(
    telemetry_repository: TelemetryRepository,
) -> None:
    telemetry_repository.set_armed(True)
    telemetry_repository.set_mode("AUTO")
    status = telemetry_repository.get_status()
    assert status.armed is True
    assert status.mode == "AUTO"

    telemetry_repository.set_armed(False)
    status = telemetry_repository.get_status()
    assert status.armed is False
    assert status.mode == "AUTO"


def test_snapshot_combines_all_subsystems(telemetry_repository: TelemetryRepository) -> None:
    telemetry_repository.set_imu(ImuReading(yaw=0.5))
    telemetry_repository.set_cmd_vel(linear_x=1.5, angular_z=-0.2)
    telemetry_repository.set_armed(True)
    snap = telemetry_repository.snapshot()
    assert snap.imu is not None and snap.imu.yaw == 0.5
    assert snap.linear_x == 1.5
    assert snap.angular_z == -0.2
    assert snap.armed is True


def test_concurrent_writes_remain_consistent(
    telemetry_repository: TelemetryRepository,
) -> None:
    """Stress: many threads writing — final state must reflect *some* legal write."""
    iterations = 500

    def writer(value: float) -> None:
        for _ in range(iterations):
            telemetry_repository.set_cmd_vel(linear_x=value, angular_z=value * -1)

    threads = [threading.Thread(target=writer, args=(v,)) for v in (1.0, 2.0, 3.0)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    lin = telemetry_repository.get_linear_x()
    ang = telemetry_repository.get_angular_z()
    # Both fields are written together under the lock — they must match a legal pair.
    assert lin in {1.0, 2.0, 3.0}
    assert ang == -lin


def test_nav2_plan_round_trip(telemetry_repository: TelemetryRepository) -> None:
    plan = Nav2Plan(poses=[], pose_count=0)
    telemetry_repository.set_nav2_plan(plan)
    assert telemetry_repository.get_nav2_plan() is plan
