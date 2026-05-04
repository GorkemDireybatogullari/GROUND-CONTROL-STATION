"""ColorCodeService + validation."""

from __future__ import annotations

import pytest

from app.domain.color_code import ColorCode
from app.repositories.color_code_repository import ColorCodeRepository
from app.services.color_code_service import ColorCodeService


def test_save_normalises_missing_hash(
    color_code_service: ColorCodeService, color_code_repository: ColorCodeRepository
) -> None:
    record = color_code_service.save(ColorCode(color_code="FF00AA"))
    assert record.color_code == "#FF00AA"

    loaded = color_code_repository.load()
    assert loaded is not None
    assert loaded.color_code == "#FF00AA"


def test_save_accepts_short_hex(color_code_service: ColorCodeService) -> None:
    record = color_code_service.save(ColorCode(color_code="#abc"))
    assert record.color_code == "#abc"


@pytest.mark.parametrize("bad", ["red", "#GGGGGG", "#1234", "12345", ""])
def test_rejects_invalid_color(bad: str) -> None:
    with pytest.raises(ValueError):
        ColorCode(color_code=bad)


def test_load_returns_none_when_missing(color_code_repository: ColorCodeRepository) -> None:
    assert color_code_repository.load() is None
