from marshmallow import Schema, fields


class WordSchema(Schema):
    translation = fields.Str(required=True)


class NounSchema(WordSchema):
    value = fields.Str(required=True)
    gender = fields.Str(required=True)


class DeckSchema(Schema):
    name = fields.Str(required=True)
    words = fields.List(fields.Str())


noun_schema = NounSchema()
deck_schema = DeckSchema()
