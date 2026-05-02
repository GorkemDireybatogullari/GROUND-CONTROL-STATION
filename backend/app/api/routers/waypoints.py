"""Waypoint persistence endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field

from app.api.deps import get_waypoint_service
from app.core.config import Settings, get_settings
from app.domain.waypoint import Waypoint, WaypointMission
from app.services.waypoint_service import WaypointService

router = APIRouter(prefix="/api", tags=["waypoints"])

ServiceDep = Annotated[WaypointService, Depends(get_waypoint_service)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


class WaypointsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    waypoints: list[Waypoint] = Field(min_length=1)
    mission_name: str = ""


@router.post("/save_waypoints", response_model=WaypointMission)
def save_waypoints(
    payload: WaypointsRequest,
    service: ServiceDep,
    settings: SettingsDep,
) -> WaypointMission:
    name = payload.mission_name or settings.default_mission_name
    return service.save_mission(payload.waypoints, name)
