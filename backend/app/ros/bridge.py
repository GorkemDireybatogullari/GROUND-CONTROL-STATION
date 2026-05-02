"""Manages rclpy lifecycle alongside the FastAPI app.

ROS2 spinning is synchronous; FastAPI is async. We isolate spinning on a
daemon thread and expose ``start``/``stop`` hooks the lifespan can call.
``rclpy`` may be unavailable at import time (e.g. in CI without ROS) — the
bridge degrades gracefully and logs the situation rather than crashing.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from app.repositories.telemetry_repository import TelemetryRepository

logger = structlog.get_logger(__name__)


class RosBridge:
    def __init__(self, repository: TelemetryRepository) -> None:
        self._repository = repository
        self._thread: threading.Thread | None = None
        self._executor: object | None = None
        self._node: object | None = None
        self._started = False

    def start(self) -> bool:
        """Initialise rclpy, create node, spin in background. Returns True on success."""
        try:
            import rclpy
            from rclpy.executors import MultiThreadedExecutor

            from app.ros.subscribers import TelemetrySubscriber
        except ImportError as exc:
            logger.warning("ros_unavailable", error=str(exc))
            return False

        try:
            rclpy.init()
            self._node = TelemetrySubscriber(self._repository)
            executor = MultiThreadedExecutor()
            executor.add_node(self._node)
            self._executor = executor

            self._thread = threading.Thread(
                target=executor.spin,
                name="ros-spinner",
                daemon=True,
            )
            self._thread.start()
            self._started = True
            logger.info("ros_bridge_started")
            return True
        except Exception as exc:
            logger.error("ros_bridge_start_failed", error=str(exc))
            self._safe_shutdown()
            return False

    def stop(self) -> None:
        if not self._started:
            return
        self._safe_shutdown()
        logger.info("ros_bridge_stopped")

    def _safe_shutdown(self) -> None:
        try:
            import rclpy
        except ImportError:
            return

        try:
            if self._executor is not None:
                self._executor.shutdown()  # type: ignore[attr-defined]
            if self._node is not None:
                self._node.destroy_node()  # type: ignore[attr-defined]
            if rclpy.ok():
                rclpy.shutdown()
            if self._thread is not None and self._thread.is_alive():
                self._thread.join(timeout=2.0)
        except Exception as exc:
            logger.warning("ros_bridge_shutdown_warning", error=str(exc))
        finally:
            self._executor = None
            self._node = None
            self._thread = None
            self._started = False
