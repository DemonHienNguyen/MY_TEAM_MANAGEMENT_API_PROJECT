from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models import UserModel
from ..schemas import UserRegister, UserLogin
from ..core import get_password_hash, verify_password, create_access_token, create_refresh_token
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

find_user_by_email: Callable[[Session, str], UserModel | None] = lambda the_data, user_email: the_data.query(UserModel).filter(UserModel.email == user_email).first()

def post_a_user(db:Session, data_in: UserRegister):
    check = find_user_by_email(db, data_in.email)
    if check: 
        return "DUPLICATE USER EMAIL"
    new_data = UserModel(
        email = data_in.email,
        password_hash = get_password_hash(data_in.password),
        full_name = data_in.full_name,
        created_at = data_in.created_at
    )
    
    try:
        db.add(new_data)
        db.commit()
        db.refresh(new_data)
    except IntegrityError:
        print("Dữ liệu bị trùng lặp dữ liệu !")
        db.rollback()
    return new_data

def login(db :Session, data_login: UserLogin):
    user_check = find_user_by_email(db, data_login.email)
    if user_check is None or not  verify_password(data_login.password, user_check.password_hash):
        return "PASSWORD OR ACCOUNT WRONG !"
    if not user_check.is_active:
        return "USER HAVE BEEN LOCK !"
    data_user:dict[str, Any] = {
        "sub": str(user_check.id),
        "iat": datetime.now(timezone.utc),
        "role": user_check.role,
        "user_name": user_check.full_name
    }
    token = create_access_token(pay_load=data_user)
    token_refresh = create_refresh_token(pay_load=data_user)
    return {
        "access_token": token,
        "refresh_token": token_refresh,
        "token_type": "Bearer"
    }
        