from pydantic import BaseModel, Field
from typing import List, Optional
from beanie import PydanticObjectId
from datetime import datetime
from app.models.course import Module, Lesson

class CourseCreate(BaseModel):
    title: str
    description: str
    thumbnail_url: Optional[str] = None
    is_published: bool = False

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_published: Optional[bool] = None

class CourseOut(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    title: str
    description: str
    thumbnail_url: Optional[str] = None
    modules: List[Module] = []
    is_published: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

class ModuleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    order: int

class LessonCreate(BaseModel):
    title: str
    description: Optional[str] = None
    video_url: Optional[str] = None
    pdf_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    order: int

class ProgressUpdate(BaseModel):
    lesson_id: PydanticObjectId
