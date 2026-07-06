from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from beanie import PydanticObjectId
from datetime import datetime

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut
from app.api.dependencies.auth import get_current_active_user, get_current_admin_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[ProductOut])
async def get_products(
    category_id: Optional[PydanticObjectId] = None,
    status: Optional[str] = None,
    is_featured: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    query = {}
    if category_id:
        query["category_id"] = category_id
    if status:
        query["status"] = status
    if is_featured is not None:
        query["is_featured"] = is_featured
        
    products = await Product.find(query).skip(skip).limit(limit).sort("-created_at").to_list()
    return products

@router.get("/{id}", response_model=ProductOut)
async def get_product(id: PydanticObjectId):
    product = await Product.get(id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Increment view count
    product.views += 1
    await product.save()
    
    return product

@router.get("/slug/{slug}", response_model=ProductOut)
async def get_product_by_slug(slug: str):
    product = await Product.find_one(Product.slug == slug)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductOut, dependencies=[Depends(get_current_admin_user)])
async def create_product(product_in: ProductCreate):
    existing = await Product.find_one(Product.slug == product_in.slug)
    if existing:
        raise HTTPException(status_code=400, detail="Product with this slug already exists")
    
    product = Product(**product_in.model_dump())
    await product.insert()
    return product

@router.put("/{id}", response_model=ProductOut, dependencies=[Depends(get_current_admin_user)])
async def update_product(id: PydanticObjectId, product_in: ProductUpdate):
    product = await Product.get(id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    update_data = product_in.model_dump(exclude_unset=True)
    if "slug" in update_data and update_data["slug"] != product.slug:
        existing = await Product.find_one(Product.slug == update_data["slug"])
        if existing:
            raise HTTPException(status_code=400, detail="Product with this slug already exists")
            
    for field, value in update_data.items():
        setattr(product, field, value)
        
    product.updated_at = datetime.utcnow()
    await product.save()
    return product

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin_user)])
async def delete_product(id: PydanticObjectId):
    product = await Product.get(id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await product.delete()
