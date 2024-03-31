from marshmallow import Schema, fields, validate

from models import DeckLevel


class WordSchema(Schema):
    translation = fields.Str(required=True)


class AnswerSchema(Schema):
    word = fields.Str(required=True)
    correct = fields.Boolean(required=True)


class NounSchema(WordSchema):
    value = fields.Str(required=True)
    gender = fields.Str(required=True)


class DeckSchema(Schema):
    name = fields.Str(required=True)
    level = fields.Str(validate=validate.OneOf(DeckLevel.values()))
    words = fields.List(fields.Str())


noun_schema = NounSchema()
answer_schema = AnswerSchema()
deck_schema = DeckSchema()
