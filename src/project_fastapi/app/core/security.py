from copy import deepcopy
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError, decode, encode
from pwdlib import PasswordHash

from .config import setting

password_hash = PasswordHash.recommended()

def get_password_hash(password: str):
    return password_hash.hash(password)

def verify_password(password_plain_text: str, password_aready_hash: str):
    return password_hash.verify(password_plain_text, password_aready_hash)


def create_access_token(pay_load: dict[str, Any], expire_time: timedelta | None = None):
    encode_pay_load = deepcopy(pay_load)
    encode_pay_load.update(
        {
            "exp": datetime.now(UTC) + (expire_time or timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)),
            "type": "access"
        }
    )
    token = encode(payload=encode_pay_load, key=setting.SECRET_KEY.get_secret_value(), algorithm=setting.ALGORITHM)
    return token

def create_refresh_token(pay_load: dict[str, Any], expire_time: timedelta | None = None):
    encode_pay_load = deepcopy(pay_load)
    encode_pay_load.update(
        {
            "exp": datetime.now(UTC) + (expire_time or timedelta(days=setting.ACCESS_TOKEN_EXPIRE_MINUTES)),
            "type": "refresh"
        }
    )
    token = encode(payload=encode_pay_load, key=setting.SECRET_KEY.get_secret_value(), algorithm=setting.ALGORITHM)
    return token

def decode_token(token: str):
    try:
        pay_load = decode(jwt=token, key=setting.SECRET_KEY.get_secret_value(), algorithms=[setting.ALGORITHM])
        return pay_load
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Token hết hạn !",
                "error": "token has expire time !"
            }
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Token không hợp lệ !",
                "error": "Invalidate Token"
            }
        )