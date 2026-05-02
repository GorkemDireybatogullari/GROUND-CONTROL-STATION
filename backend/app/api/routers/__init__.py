"""API routers grouped by resource."""

from app.api.routers import color_code, mission, telemetry, waypoints

__all__ = ["color_code", "mission", "telemetry", "waypoints"]
