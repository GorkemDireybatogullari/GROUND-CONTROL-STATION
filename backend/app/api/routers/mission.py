"""Mission control endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_mission_service
from app.domain.mission import MissionResult
from app.services.mission_service import MissionService

router = APIRouter(prefix="/api", tags=["mission"])

ServiceDep = Annotated[MissionService, Depends(get_mission_service)]


@router.post("/run_mission", response_model=MissionResult)
async def run_mission(service: ServiceDep) -> MissionResult:
    return await service.run_waypoint_mission()


@router.post("/run_mission2", response_model=MissionResult)
async def run_mission2(service: ServiceDep) -> MissionResult:
    return await service.run_color_code_mission()
