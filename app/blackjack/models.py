from dataclasses import dataclass
from typing import Optional

from app.store.database.gino import db
from app.store.bot.deck import Deck
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import ARRAY

@dataclass
class User:
    vk_id: int
    username: str
    info: dict
    cash: int
    num_of_wins: int

@dataclass
class Table:
    id: int # == peer_id, один стол в беседе
    peer_id: int
    created_at: str
    deck: Deck
    state: int

@dataclass
class Player:
    vk_id: int
    table_id: int
    cards: Deck
    state: int
    bet: float
    

# TODO: Написать модели user, player, gaming_table
class UserModel(db.Model):
    __tablename__ ="user"

    vk_id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.Unicode)
    info = db.Column(db.Unicode)
    num_of_wins = db.Column(db.Integer, nullable=False)
    cash = db.Column(db.Integer, nullable=False)

class TableModel(db.Model):
    __tablename__ ="table"
    
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    peer_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(), server_default='now()')
    deck = db.Column(db.PickleType, nullable=False)
    #deck = db.Column(ARRAY(db.Unicode), nullable=False)
    state = db.Column(db.Unicode, nullable=False)

class PlayerModel(db.Model):
    __tablename__ ="player"

    vk_id = db.Column(db.Integer, nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey("table.id", ondelete = 'CASCADE'), nullable=False)
    cards = db.Column(db.PickleType, nullable=False)
    bet = db.Column(db.Float)
    state = db.Column(db.Unicode, nullable=False)



