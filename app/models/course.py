from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Lesson(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    title: str
    description: Optional[str] = None
    video_url: Optional[str] = None
    pdf_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    order: int

class Module(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    title: str
    description: Optional[str] = None
    lessons: List[Lesson] = []
    order: int

class Course(Document):
    title: str
    description: str
    thumbnail_url: Optional[str] = None
    modules: List[Module] = []
    is_published: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "courses"

class UserProgress(Document):
    user_id: PydanticObjectId
    course_id: PydanticObjectId
    completed_lessons: List[PydanticObjectId] = [] # List of Lesson IDs
    last_accessed: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "user_progress"
        indexes = [
            [("user_id", 1), ("course_id", 1)],
        ]
