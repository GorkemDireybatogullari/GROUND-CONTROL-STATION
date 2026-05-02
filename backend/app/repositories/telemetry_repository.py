"""In-memory thread-safe store for telemetry readings.

Written to from the ROS subscriber thread; read from FastAPI request handlers.
A single ``threading.RLock`` guards all attributes — the data is small and
read/write contention is negligible for a GCS workload.
"""

from __future__ import annotations

import threading

from app.domain.telemetry import (
    GpsReading,
    ImuReading,
    Nav2Plan,
    OdometryReading,
    StatusReading,
    TelemetrySnapshot,
)


class TelemetryRepository:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._imu: ImuReading | None = None
        self._gps: GpsReading | None = None
        self._odom: OdometryReading | None = None
        self._linear_x: float | None = None
        self._angular_z: float | None = None
        self._status = StatusReading()
        self._nav2: Nav2Plan | None = None

    # ─── writers (called from ROS thread) ───────────────────────────────────
    def set_imu(self, imu: ImuReading) -> None:
        with self._lock:
            self._imu = imu

    def set_gps(self, gps: GpsReading) -> None:
        with self._lock:
            self._gps = gps

    def set_odometry(self, odom: OdometryReading) -> None:
        with self._lock:
            self._odom = odom

    def set_cmd_vel(self, linear_x: float, angular_z: float) -> None:
        with self._lock:
            self._linear_x = linear_x
            self._angular_z = angular_z

    def set_armed(self, armed: bool) -> None:
        with self._lock:
            self._status = self._status.model_copy(update={"armed": armed})

    def set_mode(self, mode: str) -> None:
        with self._lock:
            self._status = self._status.model_copy(update={"mode": mode})

    def set_nav2_plan(self, plan: Nav2Plan) -> None:
        with self._lock:
            self._nav2 = plan

    # ─── readers (called from FastAPI handlers) ─────────────────────────────
    def get_imu(self) -> ImuReading | None:
        with self._lock:
            return self._imu

    def get_gps(self) -> GpsReading | None:
        with self._lock:
            return self._gps

    def get_odometry(self) -> OdometryReading | None:
        with self._lock:
            return self._odom

    def get_linear_x(self) -> float:
        with self._lock:
            return self._linear_x or 0.0

    def get_angular_z(self) -> float:
        with self._lock:
            return self._angular_z or 0.0

    def get_status(self) -> StatusReading:
        with self._lock:
            return self._status

    def get_nav2_plan(self) -> Nav2Plan | None:
        with self._lock:
            return self._nav2

    def snapshot(self) -> TelemetrySnapshot:
        with self._lock:
            return TelemetrySnapshot(
                imu=self._imu,
                gps=self._gps,
                odom=self._odom,
                linear_x=self._linear_x,
                angular_z=self._angular_z,
                armed=self._status.armed,
                mode=self._status.mode,
                nav2_plan=self._nav2,
            )
