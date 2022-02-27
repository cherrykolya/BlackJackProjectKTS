from dataclasses import dataclass


@dataclass
class UpdateObject:
    id: int
    user_id: int
    body: dict
    peer_id: int


@dataclass
class Update:
    type: str
    object: UpdateObject


@dataclass
class Message:
    user_id: int
    peer_id: int
    text: str
