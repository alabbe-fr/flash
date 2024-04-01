from sqlalchemy.dialects.postgresql import ENUM
import datetime

from db import db
from utils import ExtendedEnum


class Word(db.Model):
    __tablename__ = "words"

    id = db.Column(db.Integer, primary_key=True)
    recto = db.Column(db.String(256), nullable=False)
    verso = db.Column(db.String(256), nullable=False)
    picture = db.Column(db.String(2048))
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)

    decks = db.relationship("Deck", secondary="word_deck", back_populates="words")
    answers = db.relationship("Answer", backref="words")

    def __repr__(self):
        return f"{self.recto} -> {self.verso}"

    def to_dict(self):
        return {
            "recto": self.recto,
            "verso": self.verso,
            "picture": self.picture,
        }


class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.Integer, db.ForeignKey("words.id"), nullable=False)
    correct = db.Column(db.Boolean, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)


class DeckLevel(ExtendedEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Deck(db.Model):
    __tablename__ = "decks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    level = db.Column(ENUM(DeckLevel, create_type=False), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)

    words = db.relationship("Word", secondary="word_deck", back_populates="decks")

    def to_dict(self):
        return {
            "name": self.name,
            "level": self.level.value,
            "id": self.id,
        }


word_deck = db.Table(
    "word_deck",
    db.Column("word_id", db.Integer, db.ForeignKey("words.id")),
    db.Column("deck_id", db.Integer, db.ForeignKey("decks.id")),
)
