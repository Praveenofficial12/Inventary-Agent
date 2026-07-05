from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"

class UserBase(BaseModel):
    full_name: str = ""
    email: EmailStr
    role: UserRole = UserRole.EMPLOYEE

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase):
    id: str = Field(alias="_id")
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserOut(UserBase):
    id: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict = {}

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
