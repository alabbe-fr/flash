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
    description = db.Column(db.String(2048))
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)
    deck_id = db.Column(
        db.Integer,
        db.ForeignKey("decks.id", ondelete="CASCADE"),
        nullable=False,
    )
    deck = db.relationship("Deck", back_populates="words")

    answers = db.relationship(
        "Answer",
        backref="words",
        passive_deletes=True,
    )

    def __repr__(self):
        return self.verso

    def to_dict(self):
        return {
            "recto": self.recto,
            "verso": self.verso,
            "picture": self.picture,
            "description": self.description,
        }


class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(
        db.Integer,
        db.ForeignKey("words.id", ondelete="CASCADE"),
        nullable=False,
    )
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
    profile_id = db.Column(
        db.Integer,
        db.ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    profile = db.relationship("Profile", back_populates="decks")

    words = db.relationship(
        "Word",
        back_populates="deck",
        passive_deletes=True,
    )

    def __repr__(self):
        return self.name

    def to_dict(self):
        return {
            "name": self.name,
            "level": self.level.value,
            "id": self.id,
        }


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    parent_id = db.Column(
        db.Integer,
        db.ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=True,
    )
    parent = db.relationship("Profile", remote_side=[id], backref="children")

    decks = db.relationship(
        "Deck",
        back_populates="profile",
        passive_deletes=True,
    )

    def __repr__(self):
        return self.name

    def to_dict(self):
        return {
            "name": self.name,
            "id": self.id,
            "parent_id": self.id,
        }
