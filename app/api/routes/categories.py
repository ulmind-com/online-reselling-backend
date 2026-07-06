from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from beanie import PydanticObjectId
from datetime import datetime

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.api.dependencies.auth import get_current_active_user, get_current_admin_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[CategoryOut])
async def get_categories():
    categories = await Category.find_all().to_list()
    return categories

@router.get("/{id}", response_model=CategoryOut)
async def get_category(id: PydanticObjectId):
    category = await Category.get(id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=CategoryOut, dependencies=[Depends(get_current_admin_user)])
async def create_category(category_in: CategoryCreate):
    existing = await Category.find_one(Category.slug == category_in.slug)
    if existing:
        raise HTTPException(status_code=400, detail="Category with this slug already exists")
    
    category = Category(**category_in.model_dump())
    await category.insert()
    return category

@router.put("/{id}", response_model=CategoryOut, dependencies=[Depends(get_current_admin_user)])
async def update_category(id: PydanticObjectId, category_in: CategoryUpdate):
    category = await Category.get(id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
        
    update_data = category_in.model_dump(exclude_unset=True)
    if "slug" in update_data and update_data["slug"] != category.slug:
        existing = await Category.find_one(Category.slug == update_data["slug"])
        if existing:
            raise HTTPException(status_code=400, detail="Category with this slug already exists")
            
    for field, value in update_data.items():
        setattr(category, field, value)
        
    category.updated_at = datetime.utcnow()
    await category.save()
    return category

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin_user)])
async def delete_category(id: PydanticObjectId):
    category = await Category.get(id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await category.delete()
