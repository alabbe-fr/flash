import os
from flask import Flask, request, abort, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from marshmallow import ValidationError
from sqlalchemy import func
from random import shuffle

from models import Word, Answer, Deck, DeckLevel
from validators import word_schema, deck_schema, answer_schema
from db import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app, origins=["http://localhost:8000"])

db.init_app(app)
migrate = Migrate(app, db)


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


@app.route("/word", methods=["POST"])
def add_word():
    try:
        data = word_schema.load(request.json)

        if Word.query.filter_by(recto=data["recto"]).first():
            abort(400)

        new_noun = Word(
            recto=data["recto"],
            verso=data["verso"],
        )

        db.session.add(new_noun)
        db.session.commit()
    except ValidationError as err:
        return jsonify({"message": "Validation error", "errors": err.messages}), 400

    return "", 201


@app.route("/answer", methods=["POST"])
def answer():
    try:
        data = answer_schema.load(request.json)

        word = Word.query.filter_by(recto=data["word"]).first()
        if not word:
            abort(400)

        new_answer = Answer(
            word=word.id,
            correct=data["correct"],
        )

        db.session.add(new_answer)
        db.session.commit()
    except ValidationError as err:
        return jsonify({"message": "Validation error", "errors": err.messages}), 400

    return "", 200


@app.route("/decks")
def get_decks():
    decks = []
    for deck in Deck.query.all():
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
