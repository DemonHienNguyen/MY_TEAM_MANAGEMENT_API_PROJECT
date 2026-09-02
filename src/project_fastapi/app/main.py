from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# from .db.seed import seed_data
from .core import limit, logger, setting
from .db import create_all  # type: ignore
from .exceptions import global_error, http_error, rare_limit, validate_error
from .routers import AuRouter, ProMeRouter, ProRouter, TasRouter, UsRouter
from .utils import CustomLogging


@asynccontextmanager
async def lifespan(app: FastAPI):
    # seed_data()
    yield


create_all()


app = FastAPI(version="3.6.7", lifespan=lifespan)

app.add_middleware(CustomLogging)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=setting.CORS_ORIGINS,
)

app.state.limiter = limit
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

global_error(app)
http_error(app)
validate_error(app)
rare_limit(app)

app.include_router(AuRouter)
app.include_router(UsRouter)
app.include_router(ProRouter)
app.include_router(ProMeRouter)
app.include_router(TasRouter)


@app.get(
    "/",
    summary="TestAPI",
    description="Này để check api chạy được không đồng thời có link use case",
)
def check_health_api():
    logger.info("API chạy tốt !")
    return {
        "message": "API run still good !",
        "file_check_sheet": "https://docs.google.com/spreadsheets/d/1hRoiXyYpnDJS35HoyMBsYho6rlGYrr5w_jxzofdsTEY/edit?usp=sharing",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="localhost", port=3636, reload=True)
