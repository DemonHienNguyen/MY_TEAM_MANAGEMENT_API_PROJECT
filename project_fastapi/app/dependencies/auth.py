from app.core import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from app.models import (
    UserModel,
    UserRole,
    ProjectMemberRole,
    TaskModel,
    ProjectModel,
    ProjectMemberModel,
)
import jwt
from app.db import DataBase

o_schema = HTTPBearer()


def get_current_user(
    db: DataBase, token: HTTPAuthorizationCredentials = Depends(o_schema)
):
    credital_http_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"message": "Token không hợp lệ !", "error": "Token not correct !"},
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_riel = token.credentials
        pay_load = decode_token(token=token_riel)
        user_id = pay_load["sub"]
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "Lỗi token không hợp lệ !",
                    "error": "Token is not allowed !",
                },
            )
    except jwt.ExpiredSignatureError:
        raise credital_http_exception
    except jwt.PyJWKError:
        raise credital_http_exception

    user_find = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
    if user_find is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Người dùng không tồn tại !",
                "error": "NOT FOUND A USER !",
            },
        )
    if not user_find.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Người dùng đã bị khóa !",
                "error": "USER HAVE BEEN LOCK !",
            },
        )
    return user_find


class RequireRole:
    def __init__(self, allowed_list: list[str]):
        self.allowed_list = allowed_list

    def __call__(self, current_user: UserModel = Depends(get_current_user)):
        if current_user.role not in self.allowed_list:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Người dùng không có quyền !",
                    "error": "USER HAVE NOT PREMISION !",
                },
            )
        return current_user


Require_Admin_and_User = RequireRole([UserRole.ADMIN, UserRole.USER])
Require_Admin = RequireRole([UserRole.ADMIN])
Require_User = RequireRole([UserRole.USER])
