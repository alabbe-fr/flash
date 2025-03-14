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
app.config["SESSION_REDIS"] = redis.from_url("redis://127.0.0.1:6379")
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
CORS(app, origins=["http://localhost:8000"])

db.init_app(app)
migrate = Migrate(app, db)


@app.route("/words")
def get_words():
    return [word.to_dict() for word in Word.query.all()]


@app.route("/words/<deck_id>")
def get_deck_words(deck_id):
    if deck_id == "mistakes":
        words = (
            Word.query.join(Answer, Answer.word == Word.id)
            .filter(Answer.correct == False)
            .limit(10)
            .all()
        )
    else:
        deck = Deck.query.filter_by(id=deck_id).first()
        if not deck:
            abort(404)

        words = deck.words

    words = [word.to_dict() for word in words]
    shuffle(words)

    return words


@app.route("/word", methods=["POST"])
def add_word():
    try:
        data = word_schema.load(request.json)

        found = Word.query.filter_by(recto=data["recto"]).first()
        if found:
            found.picture = data.get("picture")
            found.description = data.get("description")
            db.session.commit()
            return "", 204

        new_noun = Word(
            recto=data["recto"],
            verso=data["verso"],
            picture=data.get("picture"),
            description=data.get("description"),
        )

        db.session.add(new_noun)
        db.session.commit()
    except ValidationError as err:
        return jsonify({"message": "Validation error", "errors": err.messages}), 400

    return "", 201


@app.route("/answers", methods=["DELETE"])
def answers():
    Answer.query.delete()
    db.session.commit()

    return "", 204


@app.route("/answer", methods=["POST"])
def answer():
    try:
        data = answer_schema.load(request.json)

        word = Word.query.filter_by(recto=data["word"]).first()
        if not word:
            abort(400)

        answer = Answer.query.filter_by(word=word.id).first()
        if answer:
            answer.correct = data["correct"]
        else:
            new_answer = Answer(
                word=word.id,
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

    mistakes_deck_size = (
        Answer.query.filter_by(correct=False)
        .order_by(Answer.created_date.desc())
        .limit(10)
        .count()
    )
    if mistakes_deck_size > 0:
        decks.append(
            {
                "score": 0,
                "size": mistakes_deck_size,
                "name": "Mistakes",
                "level": "easy",
                "id": "mistakes",
            }
        )

    profile = Profile.query.filter_by(id=profile_id).first()
    if not profile:
        abort(404)

    for deck in profile.decks:
        score = len(
            db.session.query(func.count(Answer.word))
            .join(Word, Answer.word == Word.id)
            .join(Deck, Word.decks)
            .filter(Deck.id == deck.id)
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


@app.route("/profiles")
def get_profiles():
    profiles = Profile.query.all()
    return [profile.to_dict() for profile in profiles]


@app.route("/deck", methods=["POST"])
def add_deck():
    try:
        data = deck_schema.load(request.json)
        level = DeckLevel[data["level"].upper()]

        deck = Deck.query.filter_by(name=data["name"], level=level).first()
        if not deck:
            deck = Deck(
                name=data["name"],
                level=level,
            )
            db.session.add(deck)

        for word_name in data["words"]:
            if word_name in [w.recto for w in deck.words]:
                continue

            word = Word.query.filter_by(recto=word_name).first()
            if not word:
                continue

            deck.words.append(word)

        db.session.commit()
    except ValidationError as err:
        return jsonify({"message": "Validation error", "errors": err.messages}), 400

    return "", 201


@app.route("/profile", methods=["POST"])
def add_profile():
    try:
        data = profile_schema.load(request.json)

        profile = Profile.query.filter_by(name=data["name"]).first()
        if not profile:
            profile = Profile(
                name=data["name"],
            )
            db.session.add(profile)

        for deck_json in data["decks"]:
            level = DeckLevel[deck_json["level"].upper()]

            if (deck_json["name"], level) in [(d.name, d.level) for d in profile.decks]:
                continue

            deck = Deck.query.filter_by(
                name=deck_json["name"],
                level=level,
            ).first()
            if not deck:
                continue

            profile.decks.append(deck)

        db.session.commit()
    except ValidationError as err:
        return jsonify({"message": "Validation error", "errors": err.messages}), 400

    return "", 201


class WordAdmin(ModelView):
    column_searchable_list = ["recto", "verso"]
    column_list = ("recto", "verso", "picture", "description", "decks")
    column_filters = ("decks",)


class DeckAdmin(ModelView):
    column_searchable_list = ["name"]
    column_list = ("name", "level", "profiles")
    column_filters = ("profiles",)


class ProfileAdmin(ModelView):
    column_searchable_list = ["name"]


admin = Admin(app)
admin.add_view(WordAdmin(Word, db.session))
admin.add_view(DeckAdmin(Deck, db.session))
admin.add_view(ProfileAdmin(Profile, db.session))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
