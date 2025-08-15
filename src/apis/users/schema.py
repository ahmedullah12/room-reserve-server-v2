from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional

class UserRole(str, Enum):
    user = "user"
    admin = "admin"

class UserBase(BaseModel):
    name: str 
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole = UserRole.user
    address: Optional[str] = None
    
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    address: Optional[str] = None
    
    class Config:
        extra = "forbid"