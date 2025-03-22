from typing import List
from sqlalchemy.orm import Session
from app.models.models import Lesson
from app.schemas.lesson import LessonCreate, LessonUpdate


class LessonController:
    def __init__(self, db: Session):
        self.db = db

    def create_lesson(self, data: LessonCreate):
        lesson = Lesson(title=data.title, content=data.content)
        self.db.add(lesson)
        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    def get_lesson(self, lesson_id: int):
        return self.db.query(Lesson).filter(Lesson.id == lesson_id).first()

    def get_all_lessons(self) -> List[Lesson]:
        return self.db.query(Lesson).all()

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

    def search_lessons(self, search_term: str) -> List[Lesson]:
        return self.db.query(Lesson).filter(
            Lesson.title.ilike(f'%{search_term}%') | Lesson.content.ilike(f'%{search_term}%')
        ).all()