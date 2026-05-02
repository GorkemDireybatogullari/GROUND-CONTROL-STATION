"""Color code persistence endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Form

from app.api.deps import get_color_code_service
from app.domain.color_code import ColorCode, ColorCodeRecord
from app.services.color_code_service import ColorCodeService

router = APIRouter(prefix="/api", tags=["color-code"])

ServiceDep = Annotated[ColorCodeService, Depends(get_color_code_service)]


@router.post("/save_color_code", response_model=ColorCodeRecord)
def save_color_code(
    color_code: Annotated[str, Form(...)],
    service: ServiceDep,
) -> ColorCodeRecord:
    return service.save(ColorCode(color_code=color_code))
