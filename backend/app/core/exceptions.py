import logging
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.common import ErrorResponse

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(
        self,
        *,
        detail: str,
        status_code: int = HTTPStatus.BAD_REQUEST,
        code: str = "application_error",
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code
        self.code = code


class ConflictException(AppException):
    def __init__(self, detail: str) -> None:
        super().__init__(detail=detail, status_code=HTTPStatus.CONFLICT, code="conflict")


class NotFoundException(AppException):
    def __init__(self, detail: str) -> None:
        super().__init__(detail=detail, status_code=HTTPStatus.NOT_FOUND, code="not_found")


class ServiceUnavailableException(AppException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            detail=detail,
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            code="service_unavailable",
        )


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Could not validate credentials.") -> None:
        super().__init__(detail=detail, status_code=HTTPStatus.UNAUTHORIZED, code="unauthorized")


def _error_response(request: Request, *, status_code: int, code: str, detail: str) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    payload = ErrorResponse(code=code, detail=detail, request_id=request_id)
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning("application_exception", extra={"code": exc.code, "detail": exc.detail})
    return _error_response(
        request,
        status_code=exc.status_code,
        code=exc.code,
        detail=exc.detail,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return _error_response(
        request,
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        code="validation_error",
        detail="Request validation failed.",
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "HTTP error."
    return _error_response(
        request,
        status_code=exc.status_code,
        code="http_error",
        detail=detail,
    )


async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    logger.exception("database_exception", exc_info=exc)
    return _error_response(
        request,
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        code="database_error",
        detail="A database error occurred while processing the request.",
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception", exc_info=exc)
    return _error_response(
        request,
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        code="internal_server_error",
        detail="An unexpected error occurred.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
