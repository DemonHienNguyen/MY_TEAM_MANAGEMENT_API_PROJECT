from fastapi import APIRouter, HTTPException, status
from fastapi.requests import Request

from ..core import limit
from ..db import DataBase
from ..responses import StandardResponse
from ..schemas import (
    RefreshTokenRequest,
    UserLogin,
    UserRegister,
    UserResponse,
    UserResponseLogin,
)
from ..services import create_access, login, post_a_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=StandardResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Thêm người dùng mới / Đăng ký",
    description="HÀM ĐỂ ĐĂNG KÝ SẼ NHẬP CÁC TRƯỜNG EMAIL, PASSWORD, VÀ FULLNAME SAU ĐÓ SẼ CHECK PASSWORD HỢP LỆ (PASSWORD CÓ 8 KÝ TỰ, ÍT NHẤT CHỨA 1 KÝ TỰ THƯỜNG VỚI 1 KÝ TỰ VIẾT HOA)",
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
    "/login",
    response_model=UserResponseLogin,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng nhập",
    description="SẼ NHẬP TRƯỜNG EMAIL VÀ PASSWORD SAU ĐÓ CHECK CÓ TÀI KHOẢN CHỨA EMAIL ĐÓ CÓ TỒN TẠI HAY KHÔNG RỒI SO SÁNH MẬT KHẨU CUỐI CÙNG TRẢ VỀ ACCESS_TOKEN VỚI REFRESH_TOKEN",
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
    "/refresh",
    response_model=UserResponseLogin,
    status_code=status.HTTP_201_CREATED,
    summary="Cấp lại access token",
    description="SỬ DỤNG REFRESH_TOKEN ĐỂ LẤY ACCESSTOKEN MỚI MÀ KHÔNG CẦN PHẢI ĐĂNG NHẬP LẠI",
)
@limit.limit("10/hour")  # type: ignore
def refresh_access_token(request: Request, db: DataBase, body: RefreshTokenRequest):
    check = create_access(db, body)
    return check
