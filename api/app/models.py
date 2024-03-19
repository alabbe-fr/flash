import enum

from db import db

class Word(db.Model):
    __tablename__ = "words"
    
    id = db.Column(db.Integer, primary_key=True)
    word_type = db.Column(db.String(32), nullable=False)
    translation = db.Column(db.String(256), nullable=False)
    
    __mapper_args__ = {'polymorphic_on': word_type}
    
    def to_dict(self):
        return {
            "translation": self.translation
        }
    
class Noun(Word):
    __mapper_args__ = {'polymorphic_identity': 'noun'}
    
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
            **super().to_dict()
        )
