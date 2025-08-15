from uuid import UUID
from src.apis.users.schema import UserBase
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserCreate(UserBase):
    password: str
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class LoginData(BaseModel):
    accessToken: str
    email: EmailStr

class LoginResponse(BaseModel):
    statusCode: int
    success: bool
    message: str
    data: LoginData
    
    
class UserResponse(UserBase):
    id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        
class SignUpResponse(LoginResponse):
    pass
