from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

uri = 'sqlite:///hansard.db'
if os.environ.has_key('DATABASE_URL'):
	uri = os.environ['DATABASE_URL']
	
engine = create_engine(uri, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
	# import all modules here that might define models so that
	# they will be registered properly on the metadata.  Otherwise
	# you will have to import them first before calling init_db()
	import models
	Base.metadata.create_all(bind=engine)