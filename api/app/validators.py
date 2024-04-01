from marshmallow import Schema, fields, validate

from models import DeckLevel


class WordSchema(Schema):
    recto = fields.Str(required=True)
    verso = fields.Str(required=True)
    picture = fields.Str()


class AnswerSchema(Schema):
    word = fields.Str(required=True)
    correct = fields.Boolean(required=True)


class DeckSchema(Schema):
    name = fields.Str(required=True)
    level = fields.Str(validate=validate.OneOf(DeckLevel.values()))
    words = fields.List(fields.Str())


word_schema = WordSchema()
answer_schema = AnswerSchema()
deck_schema = DeckSchema()
