from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.models import get_db, User
from app.controllers.lesson_controller import LessonController
from app.schemas.lesson import LessonCreate, LessonResponse, LessonUpdate
from app.utils.auth import get_current_active_user

router = APIRouter(
    prefix="/api/lessons",
    tags=["lessons"],
    responses={401: {"description": "Unauthorized"}},
)


@router.get("", response_model=List[LessonResponse])
async def get_lessons(
        search: Optional[str] = Query(None, description="Search term in title or content"),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    lesson_controller = LessonController(db)

    if search:
        lessons = lesson_controller.search_lessons(search)
    else:
        lessons = lesson_controller.get_all_lessons()

    return lessons


@router.post("", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
        lesson: LessonCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    lesson_controller = LessonController(db)
    new_lesson = lesson_controller.create_lesson(lesson)
    return new_lesson


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
        lesson_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    lesson_controller = LessonController(db)
    lesson = lesson_controller.get_lesson(lesson_id)
    print(lesson)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )

    return lesson


@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
        lesson_id: int,
        lesson_data: LessonUpdate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    lesson_controller = LessonController(db)

    # Kiểm tra bài học tồn tại
    existing_lesson = lesson_controller.get_lesson(lesson_id)
    if not existing_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )

    # Cập nhật bài học
    updated_lesson = lesson_controller.update_lesson(lesson_id, lesson_data)
    return updated_lesson


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
        lesson_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    lesson_controller = LessonController(db)

    # Kiểm tra bài học tồn tại
    existing_lesson = lesson_controller.get_lesson(lesson_id)
    if not existing_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )

    # Xóa bài học
    success = lesson_controller.delete_lesson(lesson_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete lesson"
        )

    return None