"""Waypoint domain models."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Waypoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)


class WaypointMission(BaseModel):
    model_config = ConfigDict(extra="forbid")

    waypoints: list[Waypoint] = Field(min_length=1)
    mission_name: str = "yildizusv_mission"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("mission_name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("mission_name must not be empty")
        return cleaned
