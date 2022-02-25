from dataclasses import dataclass
from typing import Optional


# from app.store.database.gino import db
# from sqlalchemy.dialects.postgresql import JSONB


@dataclass
class Theme:
    id: Optional[int]
    title: str

# # TODO
# # Дописать все необходимые поля модели
# class ThemeModel(db.Model):
#     __tablename__ = "themes"

#     title = db.Column(db.Unicode, nullable=False, primary_key=True)
#     id = db.Column(db.Integer, nullable=False, )
    

# # TODO
# # Дописать все необходимые поля модели
# class AnswerModel(db.Model):
#     __tablename__ = "answers"

#     question_title = db.Column(db.Unicode, db.ForeignKey("questions.title", ondelete = 'CASCADE'), nullable=False)
#     question_id = db.Column(db.Integer, nullable=False)
#     title = db.Column(db.Unicode)
#     is_correct = db.Column(db.Integer)


@dataclass
class Question:
    id: Optional[int]
    title: str
    theme_id: int
    answers: list["Answer"]

# # TODO
# # Дописать все необходимые поля модели
# class QuestionModel(db.Model):
#     __tablename__ = "questions"

#     theme_title = db.Column(db.Unicode, db.ForeignKey("themes.title", ondelete = 'CASCADE'), nullable=False)
#     theme_id = db.Column(db.Integer, nullable=False)
#     title = db.Column(db.Unicode, primary_key=True, nullable=False)
#     id = db.Column(db.Integer, nullable=False)


@dataclass
class Answer:
    title: str
    is_correct: bool

