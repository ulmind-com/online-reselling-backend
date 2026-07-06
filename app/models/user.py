from beanie import Document, Indexed, PydanticObjectId
from pydantic import EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid

class Role(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"

class User(Document):
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    full_name: str
    role: Role = Role.MEMBER
    is_active: bool = True
    is_verified: bool = False
    profile_image: Optional[str] = None
    referred_by_id: Optional[PydanticObjectId] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    stripe_customer_id: Optional[str] = None
    
    # Stripe Connect (for affiliates receiving payouts)
    stripe_connect_id: Optional[str] = None
    charges_enabled: bool = False
    
    # Referral System
    referral_code: str = Field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    
    class Settings:
        name = "users"
