"""Color code persistence orchestration."""

from __future__ import annotations

from app.domain.color_code import ColorCode, ColorCodeRecord
from app.repositories.color_code_repository import ColorCodeRepository


class ColorCodeService:
    def __init__(self, repository: ColorCodeRepository) -> None:
        self._repository = repository

    def save(self, color: ColorCode) -> ColorCodeRecord:
        record = ColorCodeRecord(color_code=color.color_code)
        return self._repository.save(record)
