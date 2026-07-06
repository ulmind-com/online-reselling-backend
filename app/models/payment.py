from beanie import Document, Link
from pydantic import Field
from datetime import datetime
from typing import Optional
from app.models.user import User

class Payment(Document):
    user: Link[User]
    stripe_charge_id: str
    stripe_invoice_id: Optional[str] = None
    amount: float
    currency: str = "usd"
    status: str
    receipt_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "payments"
