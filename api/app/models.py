from sqlalchemy.dialects.postgresql import ENUM

from db import db
from utils import ExtendedEnum


class Word(db.Model):
    __tablename__ = "words"

    id = db.Column(db.Integer, primary_key=True)
    word_type = db.Column(db.String(32), nullable=False)
    translation = db.Column(db.String(256), nullable=False)

    __mapper_args__ = {"polymorphic_on": word_type}

    decks = db.relationship("Deck", secondary="word_deck", back_populates="words")
    answers = db.relationship("Answer", backref="words")

    def to_dict(self):
        return {"translation": self.translation}


class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.Integer, db.ForeignKey("words.id"), nullable=False)
    correct = db.Column(db.Boolean, nullable=False)


class Noun(Word):
    __mapper_args__ = {"polymorphic_identity": "noun"}

    value = db.Column(db.String(256), nullable=False)
    gender = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return f"{self.gender} {self.value} -> {self.translation}"

    def to_dict(self):
        return dict(
            {
                "type": "noun",
                "gender": self.gender,
                "value": self.value,
            },
            **super().to_dict(),
        )


class DeckLevel(ExtendedEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Deck(db.Model):
    __tablename__ = "decks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    level = db.Column(ENUM(DeckLevel, create_type=False), nullable=False)

    words = db.relationship("Word", secondary="word_deck", back_populates="decks")

    def to_dict(self):
        return {"name": self.name, "level": self.level.value}


word_deck = db.Table(
    "word_deck",
    db.Column("word_id", db.Integer, db.ForeignKey("words.id")),
    db.Column("deck_id", db.Integer, db.ForeignKey("decks.id")),
)
