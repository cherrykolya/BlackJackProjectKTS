from dataclasses import dataclass


@dataclass
class UpdateObject:
    id: int
    user_id: int
    peer_id: int
    body: dict
    

    @classmethod
    def from_message(cls, update_obj: dict) -> "UpdateObject":
        return cls(id=update_obj['message']['id'],
                   user_id=update_obj['message']['from_id'],
                   peer_id=update_obj['message']['peer_id'],
                   body=update_obj['message'])

    @classmethod
    def from_message_event(cls, update_obj: dict) -> "UpdateObject":
        return cls(id=None,
                   user_id=update_obj['user_id'],
                   peer_id=update_obj['peer_id'],
                   body=update_obj)

@dataclass
class Update:
    type: str
    object: UpdateObject

    @classmethod
    def from_dict(cls, update: dict) -> "Update":
        if update['type'] == 'message_new':
            return cls(type=update['type'],
                       object=UpdateObject.from_message(update['object']))
        elif update['type'] == 'message_event':
            return cls(type=update['type'],
                       object=UpdateObject.from_message_event(update['object']))

@dataclass
class Message:
    user_id: int
    peer_id: int
    text: str
