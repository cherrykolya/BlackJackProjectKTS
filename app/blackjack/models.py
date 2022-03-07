import json

from dataclasses import dataclass
from distutils.log import info
from typing import Optional
from datetime import datetime
from app.store.database.gino import db
from app.store.bot.deck import Card
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import ARRAY


# TODO: Написать модели user, player, gaming_table
class UserModel(db.Model):
    __tablename__ = "user"

    vk_id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.Unicode)
    info = db.Column(db.Unicode)
    num_of_wins = db.Column(db.Integer, nullable=False)
    cash = db.Column(db.Integer, nullable=False)

@dataclass
class User:
    vk_id: int
    username: str
    info: dict
    cash: int
    num_of_wins: int

    @classmethod
    def from_database(cls, user: UserModel) -> "User":
        return cls(vk_id=user.vk_id,
                   username=user.username,
                   info=user.info,
                   cash=user.cash,
                   num_of_wins=user.num_of_wins)


class TableModel(db.Model):
    __tablename__ = "table"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    peer_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(), server_default="now()")
    deck = db.Column(ARRAY(JSONB), nullable=False)
    state = db.Column(db.Unicode, nullable=False)

@dataclass
class Table:
    id: int  # == peer_id, один стол в беседе
    peer_id: int
    created_at: datetime
    deck: list[Card]
    state: int

    @classmethod
    def from_database(cls, table: TableModel) -> "Table":
        return cls(id=table.id,
                   peer_id=table.peer_id,
                   created_at=table.created_at,
                   deck=[Card.from_dict(card) for card in table.deck],
                   state=table.state)


class PlayerModel(db.Model):
    __tablename__ = "player"

    vk_id = db.Column(db.Integer, nullable=False)
    table_id = db.Column(
        db.Integer, db.ForeignKey("table.id", ondelete="CASCADE"), nullable=False
    )
    cards = db.Column(ARRAY(JSONB), nullable=False)
    bet = db.Column(db.Float)
    state = db.Column(db.Unicode, nullable=False)


@dataclass
class Player:
    vk_id: int
    table_id: int
    cards: list[Card]
    state: int
    bet: float


    @classmethod
    def from_database(cls, player: PlayerModel) -> "Player":
        return cls(vk_id=player.vk_id,
                   table_id=player.table_id,
                   cards=[Card.from_dict(card) for card in player.cards],
                   state=player.state,
                   bet=player.bet)

