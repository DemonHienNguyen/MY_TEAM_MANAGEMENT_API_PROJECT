#  V1
import os
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()


def get_enviroment():
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)


get_enviroment()


class Setting:
    def __init__(self):
        self.SECRET_KEY = self.get_require("SECRET_KEY")
        self.DATABASE_USER = self.get_require("DATABASE_USER")
        self.DATABASE_PASSWORD = self.get_require("DATABASE_PASSWORD")
        self.DATABASE_HOST = self.get_require("DATABASE_HOST")
        self.DATABASE_PORT = self.get_int("DATABASE_PORT", default=3306, min_value=1, max_value=65535)
        self.DATABASE_NAME = self.get_require("DATABASE_NAME")
        
        self.DATABASE_URL = self.build_database_url()
        
        self.ALGORITHM = self.get("ALGORITHM",default="HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = self.get_int("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, min_value=1)
        self.CORS_ORIGINS = self.get_list("CORS_ORIGINS")

    @staticmethod
    def get(name: str, default: str | None = None):
        return os.getenv(name, default=default)

    @staticmethod
    def get_require(name: str):
        value = os.getenv(name)
        if value is None:
            raise RuntimeError(f"Thiếu biến môi trường: {name}")
        return value
    @staticmethod
    def get_int(name: str, default: int | None = None, max_value: int | None = None, min_value: int|None = None):
        value = os.getenv(name)
        if value is None:
            if default is None:
                raise RuntimeError(f"Thiếu biến môi trường: {name}")
            return default
        try:
            value = int(value)
        except ValueError:
            raise RuntimeError(f"Biến môi trường {name} phải là số !")
        if min_value is not None and value < min_value:
            raise RuntimeError(f"Biến môi trường {name} phải >= {min_value} !")
        if max_value is not None and value > max_value:
            raise RuntimeError(f"Biến môi trường {name} phải <= {max_value} !")
        return value
    
    @staticmethod
    def get_bool(name: str, default: bool | None = None):
        value = os.getenv(name)
        if value is None:
            if default is None:
                raise RuntimeError(f"Thiếu biến môi trường: {name}")
            return default
        if value in ["1",  "true",  "yes", "on"]:
            return True
        if value in ["0", "false", "no", "off"]:
            return False
        raise RuntimeError(f"Biến môi trường này {name} phải là giá trị bool !")
    @staticmethod
    def get_list(name: str) -> list[str]:
        value = os.getenv(name)
        if value is None:
            return []
        return [item.strip()
                for item in value.split(",")]
        
    def build_database_url(self):
        return f"mysql+pymysql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    def validate_database_url(self):
        parsed = urlparse(self.DATABASE_URL)
        if not parsed.scheme:
            raise RuntimeError(f"Database không phù hợp !")
    def validate(self):
        if len(self.SECRET_KEY) < 32:
            raise RuntimeError(f"secret key phải dài hơn 32 ký tự trở lên")
        if self.ALGORITHM not in ["HS256", "HS384", "HS512"]:
            raise RuntimeError(f"Thuật toán trong env không được hỗ trợ !")

@lru_cache
def get_setting() -> Setting:
    return Setting()
        
setting = get_setting()