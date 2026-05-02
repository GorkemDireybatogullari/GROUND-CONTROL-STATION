"""Mission execution: launches ROS publisher scripts as detached subprocesses.

Uses ``asyncio.create_subprocess_exec`` so the FastAPI event loop is never
blocked by ``subprocess.run``. Each launch is fire-and-forget: the request
returns as soon as the process is spawned; output is logged when it exits.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import structlog

from app.core.exceptions import MissionError
from app.domain.mission import MissionResult

logger = structlog.get_logger(__name__)


class MissionService:
    def __init__(
        self,
        waypoint_script: Path,
        color_code_script: Path,
        timeout_seconds: float,
    ) -> None:
        self._waypoint_script = waypoint_script
        self._color_code_script = color_code_script
        self._timeout = timeout_seconds
        self._tasks: set[asyncio.Task[None]] = set()

    async def run_waypoint_mission(self) -> MissionResult:
        return await self._launch(self._waypoint_script, "Waypoint mission")

    async def run_color_code_mission(self) -> MissionResult:
        return await self._launch(self._color_code_script, "Color code mission")

    async def _launch(self, script: Path, label: str) -> MissionResult:
        # Stat is a single, sub-millisecond syscall; not worth offloading.
        if not await asyncio.to_thread(script.is_file):
            raise MissionError(f"{label} script not found: {script}")

        try:
            process = await asyncio.create_subprocess_exec(
                "python3",
                str(script),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except OSError as exc:
            raise MissionError(f"{label} failed to launch: {exc}") from exc

        task = asyncio.create_task(self._observe(process, label))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

        return MissionResult(
            status="success",
            message=f"{label} started (pid={process.pid})",
        )

    async def _observe(self, process: asyncio.subprocess.Process, label: str) -> None:
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self._timeout,
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            logger.warning("mission_timeout", label=label, timeout=self._timeout)
            return

        if process.returncode == 0:
            logger.info("mission_completed", label=label, pid=process.pid)
        else:
            logger.error(
                "mission_failed",
                label=label,
                pid=process.pid,
                returncode=process.returncode,
                stderr=stderr.decode(errors="replace").strip(),
                stdout=stdout.decode(errors="replace").strip(),
            )
