import os
from flask import Flask, request, abort, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from marshmallow import ValidationError

from models import Word, Noun
from validators import noun_schema
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
