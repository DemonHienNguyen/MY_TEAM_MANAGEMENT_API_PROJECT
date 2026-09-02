from typing import Any, cast

from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from ..core import logger
from ..responses import StandardResponse


def validate_error(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    def validate_error(request: Request, exc: RequestValidationError):
        logger.warning("DỮ LIỆU SAI HOẶC KHÔNG HỢP LỆ")
        error = cast(list[dict[str, Any]], exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=StandardResponse(
                StatusCode=status.HTTP_422_UNPROCESSABLE_CONTENT,
                Message="UNPROCESSABLE_CONTENT",
                Data=None,
                Error= jsonable_encoder(error),
                Path = request.url.path
            ).model_dump(mode="json")
        )