from fastapi import APIRouter, status, Depends, Query
from ..db import DataBase
from fastapi.requests import Request
from ..models import UserModel
from ..schemas import UserResponse
from ..responses import StandardResponse
from ..services import search_user_by_name_email_or_status
from ..dependencies import get_current_user, Require_Admin, Require_Admin_and_User
from ..core import limit

router = APIRouter(prefix="/user", tags=["User"])


@router.get(
    "/me",
    dependencies=[Depends(Require_Admin_and_User)],
    response_model=StandardResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin cá nhân của mình",
    description="Trả về thông tin chi tiết của người dùng (Không bao gồm password_hash)"
)
@limit.limit("5/minute")  # type: ignore
def get_detail_me(request: Request, curent_user: UserModel = Depends(get_current_user)):
    return StandardResponse(
        StatusCode=status.HTTP_200_OK,
        Error=None,
        Message="Thông tin chi tiết người dùng",
        Path=request.url.path,
        Data=curent_user,
    )


@router.get(
    "/users",
    dependencies=[Depends(Require_Admin)],
    response_model=StandardResponse[list[UserResponse]],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách người dùng",
    description="Người dùng có thể lấy danh sách của người dùng, có thể lọc theo họ tên, email và trạng thái (Chỉ dành riêng cho ADMIN)"
)
@limit.limit("5/minute")  # type: ignore
def get_list_of_user(
    request: Request,
    db: DataBase,
    name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    statu: bool | None = Query(default=None),
):
    return StandardResponse(
        StatusCode=status.HTTP_200_OK,
        Message="Danh sách các người dùng !",
        Error=None,
        Data=search_user_by_name_email_or_status(db, name, email, statu),
        Path=request.url.path,
    )
