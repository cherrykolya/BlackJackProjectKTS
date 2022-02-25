from dataclasses import dataclass
from typing import Optional

from app.store.database.gino import db
from sqlalchemy.dialects.postgresql import JSONB

@dataclass
class User:
    vk_id: int
    username: str
    info: dict

@dataclass
class Table:
    id: int
    created_at: str
    state: int

@dataclass
class Player:
    vk_id: int
    table_id: int
    cash: int
    num_of_wins: int
    

# TODO: Написать модели user, player, gaming_table
class UserModel(db.Model):
    __tablename__ ="user"

    vk_id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.Unicode)
    info = db.Column(db.Unicode)

class TableModel(db.Model):
    __tablename__ ="table"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    state = db.Column(db.Integer, nullable=False)

class PlayerModel(db.Model):
    __tablename__ ="player"

    vk_id = db.Column(db.Integer, db.ForeignKey("user.vk_id", ondelete = 'CASCADE'), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey("table.id", ondelete = 'CASCADE'), nullable=False)
    cash = db.Column(db.Integer, nullable=False)
    num_of_wins = db.Column(db.Integer, nullable=False)



