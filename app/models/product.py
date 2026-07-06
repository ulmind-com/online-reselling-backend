from beanie import Document, Link, PydanticObjectId, Indexed
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ProductFile(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    title: str
    file_type: str # 'pdf', 'video', 'zip', etc.
    file_url: str
    size_bytes: Optional[int] = None
    is_downloadable: bool = True
    order: int = 0

class Product(Document):
    # Core
    title: str
    slug: Indexed(str, unique=True)
    short_description: str
    full_description: str
    sku: Optional[str] = None
    
    # Pricing
    price: float
    sale_price: Optional[float] = None
    stripe_price_id: Optional[str] = None
    
    # Categorization
    category_id: Optional[PydanticObjectId] = None
    tags: List[str] = []
    
    # Media
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    gallery_urls: List[str] = []
    
    # Content
    included_files: List[ProductFile] = []
    features: List[str] = []
    learning_outcomes: List[str] = []
    requirements: List[str] = []
    
    # Display Settings
    status: str = "draft" # draft, published, archived
    is_featured: bool = False
    is_bestseller: bool = False
    is_new: bool = False
    
    # Affiliate Settings
    affiliate_enabled: bool = True
    commission_percentage: float = 20.0
    
    # Analytics / Stats
    version: str = "1.0.0"
    download_limit: Optional[int] = None
    views: int = 0
    sales_count: int = 0
    average_rating: float = 0.0
    reviews_count: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "products"
        indexes = [
            [("status", 1)],
            [("is_featured", 1)],
            [("category_id", 1)]
        ]
