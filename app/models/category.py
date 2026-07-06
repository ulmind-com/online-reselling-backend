from beanie import Document, PydanticObjectId, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime

class Category(Document):
    name: str
    slug: Indexed(str, unique=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "categories"
