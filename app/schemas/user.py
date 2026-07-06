from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import Role

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    referred_by_code: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_image: Optional[str] = None

from beanie import PydanticObjectId

class UserOut(UserBase):
    id: PydanticObjectId
    role: str
    is_active: bool
    is_verified: bool
    profile_image: Optional[str]
    referral_code: Optional[str] = None
    created_at: datetime
    
    class Config:
        populate_by_name = True
