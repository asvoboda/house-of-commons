from flask import Flask, jsonify, abort, request, make_response, url_for
from flask import render_template

from flask.ext.restful import reqparse, abort, Api, Resource
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.heroku import Heroku

from database import init_db
from models import MP, Quotation

import unicodedata
import simplejson as json
from urllib2 import quote as urlquote
from alchemyapi.alchemyapi import AlchemyAPI
import requests

import os

## START UP

def create_app():
	app = Flask(__name__)
	if os.environ.has_key('DATABASE_URL'):
		app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
	db = SQLAlchemy(app)
	db.init_app(app)
	return app

alchemyapi = AlchemyAPI()
	
app = create_app()
api = Api(app)
heroku = Heroku(app)

#heroku hack
if os.environ.has_key('ALCHEMYAPIKEY'):
	alchemyapi.apiKey = os.environ['ALCHEMYAPIKEY']

parser = reqparse.RequestParser()
parser.add_argument('limit', type=int, help='Limit for query length')
parser.add_argument('sentiment', type=int, help='Perform sentiment analysis')
parser.add_argument('entities', type=int, help='Perform entity analysis')

### API
class MPR(Resource):
	def abort(self):
		return 'No MP', 404

	def get(self, mp_id):
		mp = MP.query.get(mp_id)
		if mp:
			return jsonify(mp.serialize)
		return self.abort()
	
class MPListR(Resource):
	def get(self):
		args = parser.parse_args()
		limit = args.get("limit") if args.has_key("limit") else None
		mp_query = MP.query.limit(limit) if limit else MP.query
		return jsonify(data=[mp.serialize for mp in mp_query.all()])
		
class QuotationR(Resource):
	def abort(self):
		return 'No Quotation', 404
		
	def get(self, quotation_id):
		args = parser.parse_args()
		entities = args.get("entities") if args.has_key("entities") else None
		sentiment = args.get("sentiment") if args.has_key("sentiment") else None
		quot = Quotation.query.get(quotation_id)
		response = {'quotation': quot.serialize}

		if quot:
			if entities:
				text = unicodedata.normalize('NFKD', quot.text).encode('ascii','ignore')
				entities = alchemyapi.entities('text', text, {'sentiment': sentiment})
				response['entities'] = entities
			return jsonify(response)
		return self.abort()
		
class QuotationListR(Resource):
	def get(self):
		args = parser.parse_args()
		limit = args.get("limit") if args.has_key("limit") else None
		q_query = Quotation.query.limit(limit) if limit else Quotation.query
		return jsonify(data=[q.serialize for q in data])

api.add_resource(MPR, '/mps/<int:mp_id>')
api.add_resource(MPListR, '/mps')

api.add_resource(QuotationR, '/quotations/<int:quotation_id>')
api.add_resource(QuotationListR, '/quotations')



## PAGES

@app.route('/')
def index():
	#return app.root_path
	return render_template('index.html')
	
@app.route('/explore')
def explore():
	#return app.root_path
	return render_template('explore.html')

if __name__ == '__main__':
    app.run(debug=True)