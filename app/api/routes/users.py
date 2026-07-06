from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.user import User
from app.schemas.user import UserOut
from app.api.dependencies.auth import get_current_admin

router = APIRouter()

@router.get("/", response_model=List[UserOut])
async def get_users(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_admin)):
    users = await User.find_all().skip(skip).limit(limit).to_list()
    return users
