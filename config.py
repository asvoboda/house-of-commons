import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
if os.environ.has_key('DATABASE_URL'):
	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
	
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')