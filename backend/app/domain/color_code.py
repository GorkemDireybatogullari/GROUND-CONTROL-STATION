"""Color code domain models."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

_HEX_PATTERN = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


class ColorCode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    color_code: str

    @field_validator("color_code")
    @classmethod
    def _validate_hex(cls, value: str) -> str:
        if not _HEX_PATTERN.match(value):
            raise ValueError("color_code must be a valid hex string (e.g. #FF0000)")
        return value if value.startswith("#") else f"#{value}"


class ColorCodeRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    color_code: str
    status: str = "active"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
