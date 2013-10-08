from database import Base
import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref

class Quotation(Base):
	__tablename__ = 'quotation'
	id = Column(Integer, primary_key=True)
	mp = Column(Integer, ForeignKey('mp.id'))
	target_mp = Column(Integer, ForeignKey('mp.id'), nullable=True)
	language = Column(String(5))
	subject = Column(String(128))
	business = Column(String(128))
	date = Column(DateTime)
	text = Column(String)

	def __init__(self, mp, target_mp, language, subject, business, date, text):
		self.mp = mp
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
			'mp'        : self.mp,
			'target_mp' : self.target_mp,
			'language'  : self.language,
			'subject'   : self.subject,
			'business'  : self.business,
			'date'      : self.date.strftime("%B %d, %Y"),
			'text'      : self.text
		}
		
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