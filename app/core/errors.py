from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class DomainError(Exception):
    """Dasar semua error aturan bisnis."""

    status_code = 400
    error_code = "BAD_REQUEST"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    status_code = 404
    error_code = "NOT_FOUND"


class ConflictError(DomainError):
    status_code = 409
    error_code = "CONFLICT"


class InvalidStatusTransitionError(ConflictError):
    error_code = "INVALID_STATUS_TRANSITION"


class MechanicAtCapacityError(ConflictError):
    error_code = "MECHANIC_AT_CAPACITY"


class InsufficientStockError(ConflictError):
    error_code = "INSUFFICIENT_STOCK"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "error_code": exc.error_code},
        )
