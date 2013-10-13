from database import Base
import datetime
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
		"""Return object data in easily serializeable format"""
		return {
			'id'     : self.id,
			'name'   : self.name,
			'riding' : self.riding,
			'party'  : self.party
		}

class Quotation(Base):
	__tablename__ = 'quotation'
	id = Column(Integer, primary_key=True)
	from_mp = db.relationship('MP', secondary=from_quotations, backref="from_quotations")
	target_mp = db.relationship('MP', secondary=to_quotations, backref="to_quotations")
	language = Column(String(5))
	subject = Column(String(128))
	business = Column(String(128))
	date = Column(DateTime)
	text = Column(String)

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
		"""Return object data in easily serializeable format"""
		return {
			'id'        : self.id,
			'from_mp'   : [m.serialize for m in self.from_mp],
			'target_mp' : [m.serialize for m in self.target_mp],
			'language'  : self.language,
			'subject'   : self.subject,
			'business'  : self.business,
			'date'      : self.date.strftime("%B %d, %Y"),
			'text'      : self.text
		}

class Entity(Base):
	__tablename__ = 'entity'
	id = Column(Integer, primary_key=True)
	quotation = Column(Integer, ForeignKey('quotation.id'))
	type = Column(String(128))
	relevance = Column(Float)
	text = Column(String(256))
	sentiment = Column(String(128))
	score = Column(Float, nullable=True)
	mixed = Column(Float, nullable=True)

	def __init__(self, quotation, type, relevance, text, sentiment, score, mixed):
		self.quotation = quotation
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
		"""Return object data in easily serializeable format"""
		return {
			'type'      : self.type,
			'relevance' : self.relevance,
			'text'      : self.text,
			'sentiment' : self.sentiment,
			'score'     : self.score,
			'mixed'     : self.mixed
		}