"""Domain-specific exception types and FastAPI handlers."""

from __future__ import annotations

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = structlog.get_logger(__name__)


class DomainError(Exception):
    """Base class for backend domain errors that map to HTTP responses."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    status_code = status.HTTP_404_NOT_FOUND


class StorageError(DomainError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class MissionError(DomainError):
    status_code = status.HTTP_502_BAD_GATEWAY


def register_exception_handlers(app: FastAPI) -> None:
    """Wire domain exceptions to JSON responses."""

    @app.exception_handler(DomainError)
    async def _handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        logger.warning("domain_error", type=type(exc).__name__, message=exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "error": type(exc).__name__},
        )

    @app.exception_handler(ValidationError)
    async def _handle_validation_error(_: Request, exc: ValidationError) -> JSONResponse:
        # Catches Pydantic errors raised when constructing models inside handlers
        # (FastAPI auto-handles the request-body case; this covers manual usage).
        logger.info("validation_error", errors=exc.error_count())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": exc.errors(
                    include_url=False, include_context=False, include_input=False
                )
            },
        )
