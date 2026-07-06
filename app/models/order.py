from beanie import Document, PydanticObjectId, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime

class Order(Document):
    user_id: Indexed(PydanticObjectId)
    product_id: Indexed(PydanticObjectId)
    
    amount_paid: float
    currency: str = "usd"
    status: str = "completed" # completed, refunded, failed
    
    stripe_session_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    
    referred_by_id: Optional[PydanticObjectId] = None
    commission_earned: float = 0.0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "orders"
        indexes = [
            [("user_id", 1), ("product_id", 1)],
            [("stripe_session_id", 1)]
        ]
