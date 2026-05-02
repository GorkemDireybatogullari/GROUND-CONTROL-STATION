"""FastAPI application entry point."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import color_code, mission, telemetry, waypoints
from app.core.config import Settings, get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.repositories.color_code_repository import ColorCodeRepository
from app.repositories.telemetry_repository import TelemetryRepository
from app.repositories.waypoint_repository import WaypointRepository
from app.ros.bridge import RosBridge
from app.services.color_code_service import ColorCodeService
from app.services.mission_service import MissionService
from app.services.telemetry_service import TelemetryService
from app.services.waypoint_service import WaypointService

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = get_settings()

    telemetry_repo = TelemetryRepository()
    waypoint_repo = WaypointRepository(settings.waypoints_path)
    color_code_repo = ColorCodeRepository(settings.color_code_path)

    app.state.telemetry_service = TelemetryService(telemetry_repo)
    app.state.waypoint_service = WaypointService(waypoint_repo)
    app.state.color_code_service = ColorCodeService(color_code_repo)
    app.state.mission_service = MissionService(
        waypoint_script=settings.waypoint_script_path,
        color_code_script=settings.color_code_script_path,
        timeout_seconds=settings.mission_timeout_seconds,
    )

    bridge = RosBridge(telemetry_repo)
    started = bridge.start()
    if started:
        logger.info("ros_bridge_online")
    else:
        logger.warning("ros_bridge_offline_continuing_without_telemetry_writes")
    app.state.ros_bridge = bridge

    try:
        yield
    finally:
        bridge.stop()


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="YildizUSV Ground Control Station API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(telemetry.router)
    app.include_router(waypoints.router)
    app.include_router(color_code.router)
    app.include_router(mission.router)

    @app.get("/", tags=["health"])
    def root() -> dict[str, str]:
        return {"status": "ok", "service": "yildizusv-gcs-backend"}

    @app.get("/healthz", tags=["health"])
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()


def run() -> None:
    """Console-script entry point used by ``gcs-backend``."""
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run()
