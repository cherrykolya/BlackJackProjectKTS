from dataclasses import dataclass
from typing import Optional

from app.store.bot.state import EventTypes


@dataclass
class Message:
    user_id: int
    peer_id: int
    text: str
    payload: Optional[dict]
    event_id: Optional[str]

    @classmethod
    def from_message_new(cls, message: dict) -> "Message":
        return cls(
            user_id=message["from_id"],
            peer_id=message["peer_id"],
            text=message["text"],
            payload=message["payload"] if "payload" in message.keys() else None,
            event_id=None,
        )

    @classmethod
    def from_message_event(cls, message: dict) -> "Message":
        if "payload" in message.keys():
            return cls(
                user_id=message["user_id"],
                peer_id=message["peer_id"],
                text=None,
                payload=message["payload"],
                event_id=message["event_id"],
            )


@dataclass
class UpdateObject:
    id: int
    body: Message

    @classmethod
    def from_message_new(cls, update_obj: dict) -> "UpdateObject":
        return cls(
            id=update_obj["message"]["id"],
            body=Message.from_message_new(update_obj["message"]),
        )

    @classmethod
    def from_message_event(cls, update_obj: dict) -> "UpdateObject":
        return cls(id=None, body=Message.from_message_event(update_obj))


@dataclass
class Update:
    type: str
    object: UpdateObject

    @classmethod
    def from_dict(cls, update: dict) -> "Update":
        if update["type"] == EventTypes.MESSAGE_NEW:
            return cls(
                type=update["type"],
                object=UpdateObject.from_message_new(update["object"]),
            )
        elif update["type"] == EventTypes.MESSAGE_EVENT:
            return cls(
                type=update["type"],
                object=UpdateObject.from_message_event(update["object"]),
            )

    @property
    def user_id(self):
        return self.object.body.user_id

    @property
    def peer_id(self):
        return self.object.body.peer_id

    @property
    def text(self):
        return self.object.body.text

    @property
    def payload(self):
        return self.object.body.payload
