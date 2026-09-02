from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    DATABASE_USER: str
    DATABASE_PASSWORD: SecretStr = SecretStr("") 
    DATABASE_HOST: str 
    DATABASE_PORT: int 
    DATABASE_NAME: str 
    
    MAX_FILE_SIZE_STRING: str
    ALLOWED_EXTENSIONS_STRING: str
    ALLOWED_MIME_TYPES_STRING: str
    UPLOAD_DIR: str
    
    SECRET_KEY: SecretStr = SecretStr("")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAY: int = 7
    
    CORS_ORIGINS_STR: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    @computed_field
    @property
    def DATABASE_URL(self)->str:
        return f"mysql+pymysql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD.get_secret_value()}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    @computed_field
    @property
    def ALLOWED_EXTENSIONS(self) -> list[str]:
        return [exten.strip() for exten  in self.ALLOWED_EXTENSIONS_STRING.split(",")]
    @computed_field
    @property
    def ALLOWED_MIME_TYPES(self) -> list[str]:
        return [mine.strip() for mine  in self.ALLOWED_MIME_TYPES_STRING.split(",")]
    @computed_field
    @property
    def MAX_FILE_SIZE(self) -> int:
        return int(self.MAX_FILE_SIZE_STRING) * 1024 * 1024
    @computed_field
    @property 
    def CORS_ORIGINS(self) -> list[str]:
        return [cors.strip() for cors in self.CORS_ORIGINS_STR.split(",")]
setting = Setting()