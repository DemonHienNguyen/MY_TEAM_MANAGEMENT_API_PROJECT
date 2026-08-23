from sqlalchemy.orm import Session
from app.schemas import RefreshTokenRequest, UserResponseLogin
from fastapi import HTTPException, status
from app.core import decode_token, create_access_token
from app.models import UserModel
import jwt

def create_access(db: Session,body:  RefreshTokenRequest):
    credit_htttpexception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "message":"Lỗi Token không hợp lệ hoặc hết hạn",
            "error": "INVALID_REFRESH_TOKEN"
        },
        headers={
            "WWW-Authenticate":"Bearer"
        }
    )
    try:
        pay_load = decode_token(body.refresh_token)
        user_id = pay_load.get("sub", None)
        type_token = pay_load.get("type")
        if user_id is None or type_token != "refresh":
            raise credit_htttpexception
        
        user_to_find= db.query(UserModel).filter(UserModel.id == int(user_id)).first()
        if user_to_find is None:
            raise credit_htttpexception
        
    except jwt.PyJWKError:
        raise credit_htttpexception    
    
    new_access_token = create_access_token(pay_load=pay_load)
    return UserResponseLogin(
        access_token=new_access_token,
        refresh_token=body.refresh_token
    )
        