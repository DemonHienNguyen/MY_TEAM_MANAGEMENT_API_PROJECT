from fastapi  import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from ..responses import StandardResponse
from ..core import logger

def global_error(app: FastAPI):
    @app.exception_handler(Exception)
    def global_excep(request: Request, exc: Exception):
        logger.error("LỖI HỆ THỐNG HOẶC DATABASE")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=StandardResponse(
                StatusCode=status.HTTP_500_INTERNAL_SERVER_ERROR,
                Error="INTERNAL_SERVER_ERROR",
                Data=None,
                Path = request.url.path,
                Message= "Lỗi hệ thống !" 
            ).model_dump(mode="json")
        )