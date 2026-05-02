"""Mission execution result model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class MissionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    message: str
