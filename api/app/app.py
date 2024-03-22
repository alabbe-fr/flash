import os
from flask import Flask, request, abort, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from marshmallow import ValidationError

from models import Word, Noun, Deck
from validators import noun_schema, deck_schema
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


@app.route("/word/<word_type>", methods=["POST"])
def add_word(word_type):
    try:
        match word_type:
            case "noun":
                data = noun_schema.load(request.json)

                if Word.query.filter_by(translation=data["translation"]).first():
                    abort(400)

                new_noun = Noun(
                    translation=data["translation"],
                    value=data["value"],
                    gender=data["gender"],
                )

                db.session.add(new_noun)
                db.session.commit()
            case _:
                abort(400)
    except ValidationError as err:
        return jsonify({"message": "Validation error", "errors": err.messages}), 400

    return "", 201


@app.route("/decks")
def get_decks():
    return [deck.to_dict() for deck in Deck.query.all()]


@app.route("/deck", methods=["POST"])
def add_deck():
    try:
        data = deck_schema.load(request.json)

        deck = Deck.query.filter_by(name=data["name"]).first()
        if not deck:
            deck = Deck(
                name=data["name"],
            )
            db.session.add(deck)

        for word_name in data["words"]:
            if word_name in [w.translation for w in deck.words]:
                continue

            word = Word.query.filter_by(translation=word_name).first()
            if not word:
                continue

            deck.words.append(word)

        db.session.commit()
    except ValidationError as err:
        return jsonify({"message": "Validation error", "errors": err.messages}), 400

    return "", 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
