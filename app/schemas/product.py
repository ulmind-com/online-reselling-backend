from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId

class ProductFileBase(BaseModel):
    title: str
    file_type: str
    file_url: str
    size_bytes: Optional[int] = None
    is_downloadable: bool = True
    order: int = 0

class ProductBase(BaseModel):
    title: str
    slug: str
    short_description: str
    full_description: str
    sku: Optional[str] = None
    
    price: float
    sale_price: Optional[float] = None
    stripe_price_id: Optional[str] = None
    
    category_id: Optional[PydanticObjectId] = None
    tags: List[str] = []
    
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    gallery_urls: List[str] = []
    
    features: List[str] = []
    learning_outcomes: List[str] = []
    requirements: List[str] = []
    
    status: str = "draft"
    is_featured: bool = False
    is_bestseller: bool = False
    is_new: bool = False
    
    affiliate_enabled: bool = True
    commission_percentage: float = 20.0
    
    version: str = "1.0.0"
    download_limit: Optional[int] = None

class ProductCreate(ProductBase):
    included_files: List[ProductFileBase] = []

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    sale_price: Optional[float] = None
    stripe_price_id: Optional[str] = None
    category_id: Optional[PydanticObjectId] = None
    tags: Optional[List[str]] = None
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    gallery_urls: Optional[List[str]] = None
    features: Optional[List[str]] = None
    learning_outcomes: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    is_bestseller: Optional[bool] = None
    is_new: Optional[bool] = None
    affiliate_enabled: Optional[bool] = None
    commission_percentage: Optional[float] = None
    version: Optional[str] = None
    download_limit: Optional[int] = None
    included_files: Optional[List[ProductFileBase]] = None

class ProductFileOut(ProductFileBase):
    id: PydanticObjectId

class ProductOut(ProductBase):
    id: PydanticObjectId
    included_files: List[ProductFileOut] = []
    views: int
    sales_count: int
    average_rating: float
    reviews_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
