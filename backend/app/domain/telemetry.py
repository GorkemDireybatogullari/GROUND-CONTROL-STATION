"""Telemetry domain models (IMU, GPS, odometry, status, Nav2 plan)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ImuReading(_Frozen):
    yaw: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0


class GpsReading(_Frozen):
    latitude: float = 0.0
    longitude: float = 0.0
    altitude: float = 0.0


class Vector3(_Frozen):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class OdometryReading(_Frozen):
    linear_velocity: Vector3 = Field(default_factory=Vector3)
    angular_velocity: Vector3 = Field(default_factory=Vector3)
    position: Vector3 = Field(default_factory=Vector3)


class StatusReading(_Frozen):
    armed: bool = False
    mode: str = "UNKNOWN"


class Quaternion(_Frozen):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0


class Nav2Header(_Frozen):
    frame_id: str = ""
    stamp: float = 0.0


class Nav2Pose(_Frozen):
    position: Vector3
    orientation: Quaternion
    header: Nav2Header


class Nav2Plan(_Frozen):
    header: Nav2Header = Field(default_factory=Nav2Header)
    poses: list[Nav2Pose] = Field(default_factory=list)
    pose_count: int = 0


class TelemetrySnapshot(_Frozen):
    """Combined snapshot returned by the /all_telemetry endpoint."""

    imu: ImuReading | None = None
    gps: GpsReading | None = None
    odom: OdometryReading | None = None
    linear_x: float | None = None
    angular_z: float | None = None
    armed: bool | None = None
    mode: str | None = None
    nav2_plan: Nav2Plan | None = None
