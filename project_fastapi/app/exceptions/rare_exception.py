from fastapi  import FastAPI, HTTPException, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from app.responses import StandardResponse
from slowapi.errors import RateLimitExceeded
def rare_limit(app: FastAPI):
    @app.exception_handler(RateLimitExceeded)
    def rare_limit(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=StandardResponse(
                StatusCode=status.HTTP_429_TOO_MANY_REQUESTS,
                Message="Quá Nhiều request !!",
                Error="It To Many Request",
                Data=None,
                Path=request.url.path
            ).model_dump(mode="json")
        )