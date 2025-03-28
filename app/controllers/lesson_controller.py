from typing import List
from sqlalchemy.orm import Session
from app.models.models import Lesson
from app.schemas.lesson import LessonCreate, LessonUpdate
from fastapi import APIRouter, Depends, HTTPException, status, Query


class LessonController:
    def __init__(self, db: Session):
        self.db = db

    def check_id_is_not_null(self, lesson_id: int):
        # Kiểm tra xem ID đã tồn tại trong cơ sở dữ liệu chưa
        existing_lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
        return existing_lesson

    def create_lesson(self, data: LessonCreate):
        if data.id is not None:
            if self.check_id_is_not_null(data.id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Lesson with this ID already exists."
                )
            lesson = Lesson(id=data.id, title=data.title, content=data.content)

        else:
            lesson = Lesson(title=data.title, content=data.content)

        self.db.add(lesson)
        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    def get_lesson(self, lesson_id: int):
        return self.db.query(Lesson).filter(Lesson.id == lesson_id).first()

    def get_all_lessons(self) -> List[Lesson]:
        return self.db.query(Lesson).order_by(Lesson.id).all()

    def update_lesson(self, lesson_id: int, data: LessonUpdate):
        lesson = self.get_lesson(lesson_id)
        if not lesson:
            return None

        if data.title is not None:
            lesson.title = data.title
        if data.content is not None:
            lesson.content = data.content

        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    def delete_lesson(self, lesson_id: int):
        lesson = self.get_lesson(lesson_id)
        if not lesson:
            return False

        self.db.delete(lesson)
        self.db.commit()
        return True



    # def search_lessons(self, search_term: str) -> List[Lesson]:
    #     return self.db.query(Lesson).filter(
    #         Lesson.title.ilike(f'%{search_term}%') | Lesson.content.ilike(f'%{search_term}%')
    #     ).all()