from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str 
    full_name: str 
    @field_validator("email")
    @classmethod
    def validate_email(cls, value:str):
        if not value.strip():
            raise ValueError("Email không được trống !")
        return value
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        if len(value) < 8:
            raise ValueError("Mật khẩu phải 8 ký tự !")
        if not any(c.isupper() for c in value):
            raise ValueError("Mật khẩu phải có ít nhất 1 ký tự viết Hoa")
        if not any(c.islower() for c in value):
            raise ValueError("Mật khẩu phải có ít nhất 1 ký tự thường !")
        if not any(c.isdigit() for c in value):
            raise ValueError("Mật khẩu phải có ít nhất 1 số !")
        if value.isalnum():
            raise ValueError("Mật khẩu phải có ít nhất 1 ký tự đặc biệt")
        return value
    @field_validator("full_name")
    @classmethod
    def validate_name(cls, value:  str):
        if not value.strip():
            raise ValueError("Tên không được để trống !")
        if len(value.strip()) != 2:
            raise ValueError("Tên phải có ít nhất 2 ký tự không có ký tự khoảng trắng")
        return value
    
class UserResponse(BaseModel):
    id: int
    email: str 
    full_name: str 
    role: str 
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid"
    )

class UserResponseButForGetProjectMember(BaseModel):
    id: int
    # email: str
    full_name: str 
class UserResponseButForGetDetailProject(BaseModel):
    id: int
    email: str
    full_name: str
    model_config = ConfigDict(
        from_attributes=True
    ) 
class UserResponseButForGetDetailTask(BaseModel):
    id: int
    full_name: str 

class UserLogin(BaseModel):
    email: EmailStr
    password: str 
    @field_validator("email")
    @classmethod
    def validate_email(cls, value:str):
        if not value.strip():
            raise ValueError("Email không được trống !")
        return value

    
    
class UserResponseLogin(BaseModel):
    access_token: str 
    refresh_token: str 
    token_type: str = "Bearer"
    model_config = ConfigDict(
        from_attributes=True
    )
    

    