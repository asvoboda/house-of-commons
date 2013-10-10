from flask import Flask, jsonify, abort, request, make_response, url_for
from flask import render_template

from flask.ext.restful import reqparse, abort, Resource
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.heroku import Heroku

from database import init_db
from models import MP, Quotation

import unicodedata
import simplejson as json
from urllib2 import quote as urlquote
from alchemyapi import AlchemyAPI
import requests
import os

## START UP
def create_app():
	app = Flask(__name__)
	heroku = Heroku(app)
	if os.environ.has_key('DATABASE_URL'):
		app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
	db = SQLAlchemy(app)
	#db.init_app(app)
	return app

alchemyapi = AlchemyAPI()
	
app = create_app()

parser = reqparse.RequestParser()
parser.add_argument('limit', type=int, help='Limit for query length')
parser.add_argument('sentiment', type=int, help='Perform sentiment analysis')
parser.add_argument('entities', type=int, help='Perform entity analysis')

### API
@app.route('/mps/<int:mp_id>')
def mp(mp_id):
	mp = MP.query.get(mp_id)
	if mp:
		return jsonify(mp.serialize)
	return "Error: Not Found", 404

@app.route('/mps')
def mps():
	args = parser.parse_args()
	limit = args.get("limit") if args.has_key("limit") else None
	mp_query = MP.query.limit(limit) if limit else MP.query
	return jsonify(data=[mp.serialize for mp in mp_query.all()])
		
@app.route('/quotations/<int:quotation_id>')
def quotation(quotation_id):
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
	return "Error: Not Found", 404
		
@app.route('/quotations')
def quotations():
	args = parser.parse_args()
	limit = args.get("limit") if args.has_key("limit") else None
	q_query = Quotation.query.limit(limit) if limit else Quotation.query
	return jsonify(data=[q.serialize for q in q_query.all()])

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
	debug = True
	if os.environ.has_key('DATABASE_URL'):
		debug = False
	app.run(debug=debug)