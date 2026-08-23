from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import create_all
from app.models import UserModel, ProjectMemberModel, ProjectModel, TaskModel, CommnentModel  # type: ignore
from app.exceptions import global_error, http_error, validate_error, rare_limit
from contextlib import asynccontextmanager
from app.db.seed import seed_data  # type: ignore
from app.core import limit
from app.routers import AuRouter, UsRouter, ProRouter, ProMeRouter, TasRouter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core import logger, setting
from app.utils import CustomLogging


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
    allow_origins=setting.CORS_ORIGINS
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


@app.get("/")
def check_health_api():
    logger.info("API chạy tốt !")
    return {"message": "API run still good !"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="localhost", port=3636, reload=True)
