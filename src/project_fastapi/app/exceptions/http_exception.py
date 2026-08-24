from fastapi  import FastAPI, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from ..responses import StandardResponse
from typing import cast
def http_error(app: FastAPI):
    @app.exception_handler(HTTPException)
    def http_excep(request: Request, exc: HTTPException):
        if isinstance(exc.detail, dict):
            detail = cast(dict[str, str],exc.detail)
            error = detail["error"]
            message = detail["message"]
        else:
            message = exc.detail
            error = "Something Wrong !"
        return JSONResponse(
            status_code=exc.status_code,
            content= StandardResponse(
                StatusCode=exc.status_code,
                Data=None,
                Path=request.url.path,
                Error = error,
                Message=message
            ).model_dump(mode="json")
        )