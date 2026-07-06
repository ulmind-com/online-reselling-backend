from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum

class CommissionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    REJECTED = "rejected"

class Referral(Document):
    inviter_id: PydanticObjectId
    invitee_id: PydanticObjectId
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "referrals"
        indexes = [
            "inviter_id",
            "invitee_id"
        ]

class Commission(Document):
    user_id: PydanticObjectId
    referral_id: PydanticObjectId
    amount: float
    status: CommissionStatus = CommissionStatus.PENDING
    payment_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "commissions"
        indexes = [
            "user_id",
            "status"
        ]

class WithdrawalRequest(Document):
    user_id: PydanticObjectId
    amount: float
    status: CommissionStatus = CommissionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
    class Settings:
        name = "withdrawal_requests"
        indexes = [
            "user_id",
            "status"
        ]
