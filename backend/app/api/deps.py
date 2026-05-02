"""FastAPI dependency providers.

Services are constructed once during the lifespan and stashed on
``app.state``; these helpers pull them out for use with ``Depends``.
"""

from __future__ import annotations

from fastapi import Request

from app.services.color_code_service import ColorCodeService
from app.services.mission_service import MissionService
from app.services.telemetry_service import TelemetryService
from app.services.waypoint_service import WaypointService


def get_telemetry_service(request: Request) -> TelemetryService:
    return request.app.state.telemetry_service  # type: ignore[no-any-return]


def get_waypoint_service(request: Request) -> WaypointService:
    return request.app.state.waypoint_service  # type: ignore[no-any-return]


def get_color_code_service(request: Request) -> ColorCodeService:
    return request.app.state.color_code_service  # type: ignore[no-any-return]


def get_mission_service(request: Request) -> MissionService:
    return request.app.state.mission_service  # type: ignore[no-any-return]
