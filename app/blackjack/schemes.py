from marshmallow import Schema, fields


class UserCashSchema(Schema):
    vk_id = fields.Int(required=True)
    cash = fields.Int(required=True)