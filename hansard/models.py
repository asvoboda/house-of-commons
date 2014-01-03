from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float

from hansard import db

from_quotations = db.Table('to_quotations', Base.metadata,
                           db.Column('mp_id', db.Integer, db.ForeignKey('mp.id')),
                           db.Column('quotation_id', db.Integer, db.ForeignKey('quotation.id'))
)

to_quotations = db.Table('from_quotations', Base.metadata,
                         db.Column('mp_id', db.Integer, db.ForeignKey('mp.id')),
                         db.Column('quotation_id', db.Integer, db.ForeignKey('quotation.id'))
)


class MP(Base):
    __tablename__ = 'mp'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    riding = Column(String(128))
    party = Column(String(64))

    def __init__(self, name, riding, party):
        self.name = name
        self.riding = riding
        self.party = party

    def __repr__(self):
        return '<MP %r>' % self.id

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'riding': self.riding,
            'party': self.party
        }


class Quotation(Base):
    __tablename__ = 'quotation'
    id = Column(Integer, primary_key=True)
    from_mp = db.relationship('MP', secondary=to_quotations, backref="to_quotations", uselist=False)
    target_mp = db.relationship('MP', secondary=from_quotations, backref="from_quotations", uselist=False)
    language = Column(String(5))
    subject = Column(String(128))
    business = Column(String(128))
    date = Column(DateTime)
    text = Column(String)
    entities = db.relationship('Entity', backref='quotation', lazy='joined')
    keywords = db.relationship('Keyword', backref='quotation', lazy='joined')

    def __init__(self, from_mp, target_mp, language, subject, business, date, text):
        self.from_mp = from_mp
        self.target_mp = target_mp
        self.language = language
        self.subject = subject
        self.business = business
        self.date = date
        self.text = text

    def __repr__(self):
        return '<Quotation %r>' % self.id

    @property
    def serialize(self):
        if self.target_mp:
            t_mp = self.target_mp.serialize
        else:
            t_mp = {}
        return {
            'id': self.id,
            'from_mp': self.from_mp.serialize,
            'target_mp': t_mp,
            'language': self.language,
            'subject': self.subject,
            'business': self.business,
            'date': self.date.strftime("%B %d, %Y"),
            'text': self.text,
            'keywords': [k.serialize for k in self.keywords],
            'entities': [e.serialize for e in self.entities],
        }


class Entity(Base):
    __tablename__ = 'entity'
    id = Column(Integer, primary_key=True)
    quotation_id = Column(Integer, ForeignKey('quotation.id'))
    type = Column(String(128))
    relevance = Column(Float)
    text = Column(String(256))
    sentiment = Column(String(128))
    score = Column(Float, nullable=True)
    mixed = Column(Float, nullable=True)

    def __init__(self, quotation_id, type, relevance, text, sentiment, score, mixed):
        self.quotation_id = quotation_id
        self.type = type
        self.relevance = relevance
        self.text = text
        self.sentiment = sentiment
        self.score = score
        self.mixed = mixed

    def __repr__(self):
        return '<Entity %r>' % self.id

    @property
    def serialize(self):
        return {
            'type': self.type,
            'quotation_id': self.quotation_id,
            'relevance': self.relevance,
            'text': self.text,
            'sentiment': self.sentiment,
            'score': self.score,
            'mixed': self.mixed
        }


class Keyword(Base):
    __tablename__ = 'keyword'
    id = Column(Integer, primary_key=True)
    quotation_id = Column(Integer, ForeignKey('quotation.id'))
    relevance = Column(Float)
    text = Column(String(256))
    sentiment = Column(String(128))
    score = Column(Float, nullable=True)

    def __init__(self, quotation_id, relevance, text, sentiment, score):
        self.quotation_id = quotation_id
        self.relevance = relevance
        self.text = text
        self.sentiment = sentiment
        self.score = score

    def __repr__(self):
        return '<Keyword %r>' % self.id

    @property
    def serialize(self):
        return {
            'quotation_id': self.quotation_id,
            'relevance': self.relevance,
            'text': self.text,
            'sentiment': self.sentiment,
            'score': self.score,
            'type': 'Keyword'
        }