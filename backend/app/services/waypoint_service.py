"""Waypoint persistence orchestration."""

from __future__ import annotations

from app.domain.waypoint import Waypoint, WaypointMission
from app.repositories.waypoint_repository import WaypointRepository


class WaypointService:
    def __init__(self, repository: WaypointRepository) -> None:
        self._repository = repository

    def save_mission(
        self,
        waypoints: list[Waypoint],
        mission_name: str,
    ) -> WaypointMission:
        mission = WaypointMission(waypoints=waypoints, mission_name=mission_name)
        return self._repository.save(mission)
