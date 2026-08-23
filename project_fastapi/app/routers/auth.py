from fastapi import APIRouter, status, HTTPException
from app.db import DataBase
from fastapi.requests import Request
from app.schemas import (
    UserRegister,
    UserResponse,
    UserLogin,
    UserResponseLogin,
    RefreshTokenRequest,
)
from app.services import post_a_user, login, create_access
from app.responses import StandardResponse
from app.core import limit

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=StandardResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
@limit.limit("5/minute")  # type: ignore
def create_a_new_user(request: Request, db: DataBase, user_regis: UserRegister):
    check = post_a_user(db, user_regis)
    if check == "DUPLICATE USER EMAIL":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Email này đã được đăng ký !",
                "error": "This Email has exists !",
            },
        )

    return StandardResponse(
        StatusCode=status.HTTP_201_CREATED,
        Message="Thêm thành công người dùng !",
        Error=None,
        Data=check,
        Path=request.url.path,
    )


@router.post(
    "/login", response_model=UserResponseLogin, status_code=status.HTTP_201_CREATED
)
@limit.limit("5/minute")  # type: ignore
def login_a_user(request: Request, db: DataBase, login_form: UserLogin):
    check = login(db, login_form)
    if check == "PASSWORD OR ACCOUNT WRONG !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Lỗi Tài khoản hoặc mật khẩu không đúng !",
                "error": "WRONG PASSWORD OR ACCOUNT !",
            },
        )
    if check == "USER HAVE BEEN LOCK !":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Lỗi Tài khoản đã bị khóa !",
                "error": "YOUR ACCOUNT HAVE BEEN LOCK !",
            },
        )
    return check


@router.post(
    "/refresh", response_model=UserResponseLogin, status_code=status.HTTP_201_CREATED
)
@limit.limit("10/hour")  # type: ignore
def refresh_access_token(request: Request, db: DataBase, body: RefreshTokenRequest):
    check = create_access(db, body)
    return check
