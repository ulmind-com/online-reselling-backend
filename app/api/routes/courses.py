from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from beanie import PydanticObjectId
from app.models.user import User
from app.models.course import Course, UserProgress, Module, Lesson
from app.schemas.course import CourseCreate, CourseUpdate, CourseOut, ModuleCreate, LessonCreate, ProgressUpdate
from app.api.dependencies.auth import get_current_active_user, get_current_admin
from datetime import datetime

router = APIRouter()

# --- Public/Subscriber Routes ---

@router.get("/", response_model=List[CourseOut])
async def get_courses(current_user: User = Depends(get_current_active_user)):
    # Subscribers can only see published courses, admins can see all
    if current_user.role == "admin":
        courses = await Course.find_all().to_list()
    else:
        # Here you could also check if the user has an active subscription
        courses = await Course.find(Course.is_published == True).to_list()
    return courses

@router.get("/{course_id}", response_model=CourseOut)
async def get_course(course_id: PydanticObjectId, current_user: User = Depends(get_current_active_user)):
    course = await Course.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if not course.is_published and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this course")
        
    return course

@router.get("/{course_id}/progress")
async def get_user_progress(course_id: PydanticObjectId, current_user: User = Depends(get_current_active_user)):
    progress = await UserProgress.find_one(
        UserProgress.user_id == current_user.id,
        UserProgress.course_id == course_id
    )
    if not progress:
        return {"completed_lessons": []}
    return {"completed_lessons": progress.completed_lessons}

@router.post("/{course_id}/progress")
async def update_user_progress(
    course_id: PydanticObjectId, 
    progress_data: ProgressUpdate, 
    current_user: User = Depends(get_current_active_user)
):
    progress = await UserProgress.find_one(
        UserProgress.user_id == current_user.id,
        UserProgress.course_id == course_id
    )
    
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            course_id=course_id,
            completed_lessons=[progress_data.lesson_id]
        )
        await progress.insert()
    else:
        if progress_data.lesson_id not in progress.completed_lessons:
            progress.completed_lessons.append(progress_data.lesson_id)
            progress.last_accessed = datetime.utcnow()
            await progress.save()
            
    return {"status": "success", "completed_lessons": progress.completed_lessons}

# --- Admin Routes ---

@router.post("/", response_model=CourseOut)
async def create_course(course_in: CourseCreate, admin: User = Depends(get_current_admin)):
    course = Course(**course_in.dict())
    await course.insert()
    return course

@router.put("/{course_id}", response_model=CourseOut)
async def update_course(course_id: PydanticObjectId, course_in: CourseUpdate, admin: User = Depends(get_current_admin)):
    course = await Course.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    update_data = course_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(course, key, value)
        
    course.updated_at = datetime.utcnow()
    await course.save()
    return course

@router.post("/{course_id}/modules", response_model=CourseOut)
async def add_module(course_id: PydanticObjectId, module_in: ModuleCreate, admin: User = Depends(get_current_admin)):
    course = await Course.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    new_module = Module(**module_in.dict())
    course.modules.append(new_module)
    course.updated_at = datetime.utcnow()
    await course.save()
    return course

@router.post("/{course_id}/modules/{module_id}/lessons", response_model=CourseOut)
async def add_lesson(
    course_id: PydanticObjectId, 
    module_id: PydanticObjectId, 
    lesson_in: LessonCreate, 
    admin: User = Depends(get_current_admin)
):
    course = await Course.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Find module
    target_module = None
    for module in course.modules:
        if module.id == module_id:
            target_module = module
            break
            
    if not target_module:
        raise HTTPException(status_code=404, detail="Module not found")
        
    new_lesson = Lesson(**lesson_in.dict())
    target_module.lessons.append(new_lesson)
    course.updated_at = datetime.utcnow()
    await course.save()
    return course
