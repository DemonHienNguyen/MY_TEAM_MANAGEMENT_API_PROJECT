from fastapi import APIRouter, status, Depends, Query
from app.db import DataBase
from fastapi.requests import Request
from app.models import  UserModel
from app.schemas import UserResponse
from app.responses import StandardResponse
from app.services import search_user_by_name_email_or_status
from app.dependencies import get_current_user, Require_Admin, Require_Admin_and_User
from app.core import limit
router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.get("/me", dependencies=[Depends(Require_Admin_and_User)], response_model=StandardResponse[UserResponse], status_code=status.HTTP_200_OK)
@limit.limit("5/minute") # type: ignore
def get_detail_me(request: Request, curent_user: UserModel = Depends(get_current_user)):
    return StandardResponse(
        StatusCode=status.HTTP_200_OK,
        Error=None,
        Message="Thông tin chi tiết người dùng",
        Path=request.url.path,
        Data=curent_user,
    )
    
@router.get("/users", dependencies=[Depends(Require_Admin)], response_model=StandardResponse[list[UserResponse]], status_code=status.HTTP_200_OK)
@limit.limit("5/minute") # type: ignore
def get_list_of_user(request: Request, db :DataBase, name: str | None =  Query(default=None), email: str | None = Query(default=None), statu: bool | None = Query(default=None)):
    return StandardResponse(
        StatusCode=status.HTTP_200_OK,
        Message="Danh sách các người dùng !",
        Error=None,
        Data=search_user_by_name_email_or_status(db, name, email, statu),
        Path=request.url.path
    )