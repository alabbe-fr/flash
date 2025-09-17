import os
from flask import Flask, request, abort, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from marshmallow import ValidationError
from sqlalchemy import func
from random import shuffle
import redis

from models import Word, Answer, Deck, DeckLevel, Profile
from validators import word_schema, deck_schema, answer_schema, profile_schema
from db import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis.from_url(os.environ["REDIS_URL"])
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
CORS(app, origins=[os.environ["APP_URL"]])

db.init_app(app)
migrate = Migrate(app, db)


@app.route("/healthcheck")
def healthcheck():
    return "", 200


@app.route("/words")
def get_words():
    return [word.to_dict() for word in Word.query.all()]


@app.route("/words/<deck_id>")
def get_deck_words(deck_id):
    deck = Deck.query.filter_by(id=deck_id).first()
    if not deck:
        abort(404)

    words = [word.to_dict() for word in deck.words]
    shuffle(words)

    return words


@app.route("/words/mistakes/<profile_id>")
def get_mistakes(profile_id):
    words = [
        word.to_dict()
        for word in (
            Word.query.join(Answer, Answer.word == Word.id)
            .join(Deck, Deck.id == Word.deck_id)
            .filter(Deck.profile_id == profile_id)
            .filter(Answer.correct == False)
            .all()
        )
    ]
    shuffle(words)

    return words


@app.route("/word/<deck_id>", methods=["POST"])
def add_word(deck_id):
    try:
        deck = Deck.query.filter_by(id=deck_id).first()
        if not deck:
            abort(404)

        data = word_schema.load(request.json)

        new_noun = Word(
            recto=data["recto"],
            verso=data["verso"],
            picture=data.get("picture"),
            description=data.get("description"),
            deck=deck,
        )

        db.session.add(new_noun)
        db.session.commit()
    except ValidationError as err:
        return jsonify({"message": "Validation error", "errors": err.messages}), 400

    return {"id": new_noun.id}, 201


@app.route("/answers", methods=["DELETE"])
def answers():
    Answer.query.delete()
    db.session.commit()

    return "", 204


@app.route("/answer/<word_id>", methods=["POST"])
def answer(word_id):
    try:
        data = answer_schema.load(request.json)

        answer = Answer.query.filter_by(word=word_id).first()
        if answer:
            answer.correct = data["correct"]
        else:
            new_answer = Answer(
                word=word_id,
                correct=data["correct"],
            )
            db.session.add(new_answer)

        db.session.commit()
    except ValidationError as err:
        return jsonify({"message": "Validation error", "errors": err.messages}), 400

    return "", 200


@app.route("/decks/<profile_id>")
def get_decks(profile_id):
    decks = []

    mistakes_deck_size = len(
        db.session.query(func.count(Answer.id))
        .join(Word, Answer.word == Word.id)
        .join(Deck, Word.deck_id == Deck.id)
        .filter(Deck.profile_id == profile_id)
        .filter(Answer.correct == False)
        .group_by(Word.id)
        .all()
    )
    if mistakes_deck_size > 0:
        decks.append(
            {
                "score": 0,
                "size": mistakes_deck_size,
                "name": "Previous Mistakes",
                "level": "easy",
                "id": f"mistakes/{profile_id}",
            }
        )

    profile = Profile.query.filter_by(id=profile_id).first()
    if not profile:
        abort(404)

    for deck in profile.decks:
        score = len(
            db.session.query(func.count(Answer.word))
            .join(Word, Answer.word == Word.id)
            .filter(Word.deck_id == deck.id)
            .filter(Answer.correct)
            .group_by(Word.id)
            .all()
        )

        decks.append(
            {
                "score": score,
                "size": len(deck.words),
                **deck.to_dict(),
            }
        )

    return decks


@app.route("/profiles", defaults={"parent_id": None})
@app.route("/profiles/<parent_id>")
def get_profiles(parent_id):
    profiles = Profile.query.filter_by(parent_id=parent_id).all()
    return [profile.to_dict() for profile in profiles]


@app.route("/deck/<profile_id>", methods=["POST"])
def add_deck(profile_id):
    try:
        profile = Profile.query.filter_by(id=profile_id).first()
        if not profile:
            abort(404)

        data = deck_schema.load(request.json)
        level = DeckLevel[data["level"].upper()]

        deck = Deck(
            name=data["name"],
            level=level,
            profile=profile,
        )
        db.session.add(deck)

        db.session.commit()
    except ValidationError as err:
        return jsonify({"message": "Validation error", "errors": err.messages}), 400

    return {"id": deck.id}, 201


@app.route("/profile", defaults={"profile_id": None}, methods=["POST"])
@app.route("/profile/<profile_id>", methods=["POST"])
def add_profile(profile_id):
    try:
        data = profile_schema.load(request.json)

        if profile_id:
            parent = Profile.query.filter_by(id=profile_id).first()
            if not parent:
                abort(404)

            profile = Profile(
                name=data["name"],
                parent=parent,
            )
        else:
            profile = Profile(
                name=data["name"],
            )

        db.session.add(profile)
        db.session.commit()
    except ValidationError as err:
        return jsonify({"message": "Validation error", "errors": err.messages}), 400

    return {"id": profile.id}, 201


class WordAdmin(ModelView):
    column_searchable_list = ["recto", "verso"]
    column_list = ("recto", "verso", "picture", "description", "deck")
    column_filters = ("deck",)


class DeckAdmin(ModelView):
    column_searchable_list = ["name"]
    column_list = ("name", "level", "profile")
    column_filters = ("profile",)


class ProfileAdmin(ModelView):
    column_searchable_list = ["name"]
    column_list = ("name", "parent")


admin = Admin(app)
admin.add_view(WordAdmin(Word, db.session))
admin.add_view(DeckAdmin(Deck, db.session))
admin.add_view(ProfileAdmin(Profile, db.session))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
