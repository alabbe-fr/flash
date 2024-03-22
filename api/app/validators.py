from marshmallow import Schema, fields


class WordSchema(Schema):
    translation = fields.Str(required=True)


class NounSchema(WordSchema):
    value = fields.Str(required=True)
    gender = fields.Str(required=True)


noun_schema = NounSchema()
