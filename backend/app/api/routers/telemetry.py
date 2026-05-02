"""Read-only telemetry endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_telemetry_service
from app.domain.telemetry import (
    GpsReading,
    ImuReading,
    Nav2Plan,
    OdometryReading,
    StatusReading,
    TelemetrySnapshot,
)
from app.services.telemetry_service import TelemetryService

router = APIRouter(prefix="/api", tags=["telemetry"])

ServiceDep = Annotated[TelemetryService, Depends(get_telemetry_service)]


@router.get("/gps_message", response_model=GpsReading)
def gps_message(service: ServiceDep) -> GpsReading:
    return service.get_gps()


@router.get("/imu_message", response_model=ImuReading)
def imu_message(service: ServiceDep) -> ImuReading:
    return service.get_imu()


@router.get("/odometry", response_model=OdometryReading)
def odometry(service: ServiceDep) -> OdometryReading:
    return service.get_odometry()


@router.get("/linear_x")
def linear_x(service: ServiceDep) -> dict[str, float]:
    return {"linear_x": service.get_linear_x()}


@router.get("/angular_z")
def angular_z(service: ServiceDep) -> dict[str, float]:
    return {"angular_z": service.get_angular_z()}


@router.get("/armed_status")
def armed_status(service: ServiceDep) -> dict[str, bool]:
    return {"armed": service.get_status().armed}


@router.get("/mode_status")
def mode_status(service: ServiceDep) -> dict[str, str]:
    return {"mode": service.get_status().mode}


@router.get("/nav2_plan", response_model=Nav2Plan)
def nav2_plan(service: ServiceDep) -> Nav2Plan:
    return service.get_nav2_plan()


@router.get("/all_telemetry", response_model=TelemetrySnapshot)
def all_telemetry(service: ServiceDep) -> TelemetrySnapshot:
    return service.snapshot()


@router.get("/status", response_model=StatusReading)
def status(service: ServiceDep) -> StatusReading:
    return service.get_status()
