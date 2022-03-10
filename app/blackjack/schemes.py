from marshmallow import Schema, fields


class UserGetSchema(Schema):
    vk_id = fields.Int(required=True)

class UserCashSchema(Schema):
    vk_id = fields.Int(required=True)
    cash = fields.Int(required=True)

class UserSchema(Schema):
    vk_id = fields.Int(required=True)
    username = fields.Str(required=True)
    info = fields.Str(required=True)
    cash = fields.Int(required=True)
    num_of_wins = fields.Int(required=True)

class PlayerGetSchema(Schema):
    table_id = fields.Int(required=True)

class CardSchema(Schema):
    suit = fields.Str(required=True)
    card_name = fields.Str(required=True)
    value = fields.Int(required=True)

class PlayerSchema(Schema):
    vk_id = fields.Int(required=True)
    table_id = fields.Int(required=True)
    cards =  fields.Nested(CardSchema, many=True, required=True)
    state = fields.Str(required=True)
    bet = fields.Float(required=True)

class PlayersSchema(Schema):
    players = fields.Nested(PlayerSchema, many=True)

class TableGetSchema(Schema):
    table_id = fields.Int(required=True)

class TableSchema(Schema):
    id =  fields.Int(required=True) 
    peer_id = fields.Int(required=True)
    created_at = fields.DateTime(required=True)
    deck = fields.Nested(CardSchema, many=True, required=True)
    state = fields.Str(required=True)
