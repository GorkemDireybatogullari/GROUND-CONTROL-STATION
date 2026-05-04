"""Settings parsing — env vars, list-from-CSV, log level normalisation."""

from __future__ import annotations

import pytest

from app.core.config import Settings


def test_cors_csv_string_is_split() -> None:
    settings = Settings(cors_allowed_origins="http://a.test, http://b.test ,")
    assert settings.cors_allowed_origins == ["http://a.test", "http://b.test"]


def test_cors_list_passes_through() -> None:
    settings = Settings(cors_allowed_origins=["http://a"])
    assert settings.cors_allowed_origins == ["http://a"]


def test_log_level_uppercased() -> None:
    settings = Settings(log_level="debug")
    assert settings.log_level == "DEBUG"


def test_invalid_log_level_rejected() -> None:
    with pytest.raises(ValueError):
        Settings(log_level="loud")


def test_path_helpers() -> None:
    settings = Settings()
    assert settings.waypoints_path.name == "waypoints.json"
    assert settings.color_code_path.name == "color_code.json"
    assert settings.waypoint_script_path.name == "waypoint_publisher.py"
