"""MissionService — subprocess launching + error paths."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.config import Settings
from app.core.exceptions import MissionError
from app.services.mission_service import MissionService


@pytest.mark.asyncio
async def test_missing_script_raises_mission_error(mission_service: MissionService) -> None:
    with pytest.raises(MissionError):
        await mission_service.run_waypoint_mission()


@pytest.mark.asyncio
async def test_launches_real_subprocess(tmp_settings: Settings) -> None:
    """Use a tiny throwaway script so we can verify the launch path end-to-end."""
    script = tmp_settings.ros_nodes_dir / "noop.py"
    script.write_text("import sys; sys.exit(0)\n")

    service = MissionService(
        waypoint_script=script,
        color_code_script=script,
        timeout_seconds=5.0,
    )

    result = await service.run_waypoint_mission()
    assert result.status == "success"
    assert "started" in result.message

    # Wait for the observer task to reap the child so test teardown is clean.
    for task in list(service._tasks):  # noqa: SLF001
        await task


@pytest.mark.asyncio
async def test_rejects_non_file_path(tmp_path: Path) -> None:
    """A directory path is not a script — should fail the is_file() check."""
    service = MissionService(
        waypoint_script=tmp_path,
        color_code_script=tmp_path,
        timeout_seconds=1.0,
    )
    with pytest.raises(MissionError):
        await service.run_color_code_mission()
