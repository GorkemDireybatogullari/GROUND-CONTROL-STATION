"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT: Path = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Strongly typed application settings."""

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ROOT.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ─── Server ─────────────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 5002
    log_level: str = "INFO"

    # Comma-separated. "*" allowed only outside production.
    cors_allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )

    # ─── ROS2 ───────────────────────────────────────────────────────────────
    ros_domain_id: int = 0

    # ─── Filesystem layout ──────────────────────────────────────────────────
    backend_root: Path = BACKEND_ROOT
    data_dir: Path = BACKEND_ROOT / "data"
    ros_nodes_dir: Path = BACKEND_ROOT / "ros_nodes"

    waypoints_filename: str = "waypoints.json"
    color_code_filename: str = "color_code.json"

    waypoint_script: str = "waypoint_publisher.py"
    color_code_script: str = "color_code_publisher.py"

    # ─── Mission ────────────────────────────────────────────────────────────
    mission_timeout_seconds: float = 300.0
    default_mission_name: str = "yildizusv_mission"

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def _split_cors(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("log_level")
    @classmethod
    def _normalise_log_level(cls, value: str) -> str:
        normalised = value.upper()
        if normalised not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError(f"Invalid log level: {value}")
        return normalised

    # Convenience helpers ─────────────────────────────────────────────────────
    @property
    def waypoints_path(self) -> Path:
        return self.data_dir / self.waypoints_filename

    @property
    def color_code_path(self) -> Path:
        return self.data_dir / self.color_code_filename

    @property
    def waypoint_script_path(self) -> Path:
        return self.ros_nodes_dir / self.waypoint_script

    @property
    def color_code_script_path(self) -> Path:
        return self.ros_nodes_dir / self.color_code_script


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings accessor for use as a FastAPI dependency."""
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings
