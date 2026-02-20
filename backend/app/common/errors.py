from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.common.observability import get_request_id


class ApiException(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, object] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


def build_error_response(
    code: str,
    message: str,
    trace_id: str,
    details: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "trace_id": trace_id,
        }
    }


def _http_exception_to_payload(exc: HTTPException) -> tuple[str, str, dict[str, object]]:
    if isinstance(exc.detail, dict):
        code = str(exc.detail.get("code", "http_error"))
        message = str(exc.detail.get("message", "Request failed"))
        details = exc.detail.get("details", {})
        if isinstance(details, dict):
            return code, message, details
        return code, message, {"raw_details": details}
    if isinstance(exc.detail, str):
        return "http_error", exc.detail, {}
    return "http_error", "Request failed", {"raw_details": exc.detail}


def _serialize_validation_errors(exc: RequestValidationError) -> list[dict[str, object]]:
    return jsonable_encoder(exc.errors())


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiException)
    async def api_exception_handler(request: Request, exc: ApiException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_response(
                code=exc.code,
                message=exc.message,
                details=exc.details,
                trace_id=get_request_id(request),
            ),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        code, message, details = _http_exception_to_payload(exc)
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_response(
                code=code,
                message=message,
                details=details,
                trace_id=get_request_id(request),
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=build_error_response(
                code="validation_error",
                message="Request validation failed",
                details={"errors": _serialize_validation_errors(exc)},
                trace_id=get_request_id(request),
            ),
        )

    @app.exception_handler(Exception)
    async def fallback_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=build_error_response(
                code="internal_server_error",
                message="Unexpected server error",
                details={"exception_type": exc.__class__.__name__},
                trace_id=get_request_id(request),
            ),
        )
