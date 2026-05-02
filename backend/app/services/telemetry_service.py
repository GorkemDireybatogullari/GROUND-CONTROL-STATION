"""Telemetry read service — thin wrapper over the repository.

Kept as a separate layer so that, if telemetry ever needs derived metrics
(filtering, smoothing, unit conversion), there's a clear home for them.
"""

from __future__ import annotations

from app.core.exceptions import NotFoundError
from app.domain.telemetry import (
    GpsReading,
    ImuReading,
    Nav2Plan,
    OdometryReading,
    StatusReading,
    TelemetrySnapshot,
)
from app.repositories.telemetry_repository import TelemetryRepository


class TelemetryService:
    def __init__(self, repository: TelemetryRepository) -> None:
        self._repository = repository

    def get_imu(self) -> ImuReading:
        return self._repository.get_imu() or ImuReading()

    def get_gps(self) -> GpsReading:
        return self._repository.get_gps() or GpsReading()

    def get_odometry(self) -> OdometryReading:
        return self._repository.get_odometry() or OdometryReading()

    def get_linear_x(self) -> float:
        return self._repository.get_linear_x()

    def get_angular_z(self) -> float:
        return self._repository.get_angular_z()

    def get_status(self) -> StatusReading:
        return self._repository.get_status()

    def get_nav2_plan(self) -> Nav2Plan:
        plan = self._repository.get_nav2_plan()
        if plan is None or plan.pose_count == 0:
            raise NotFoundError("No Nav2 plan data available from ROS2")
        return plan

    def snapshot(self) -> TelemetrySnapshot:
        return self._repository.snapshot()
