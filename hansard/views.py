from hansard import app

from flask import jsonify, render_template
from flask.ext.restful import reqparse

from models import MP, Quotation

from alchemyapi import AlchemyAPI

import unicodedata
import os

parser = reqparse.RequestParser()
parser.add_argument('limit', type=int, help='Limit for query length')
parser.add_argument('sentiment', type=int, help='Perform sentiment analysis')
parser.add_argument('entities', type=int, help='Perform entity analysis')

alchemyapi = AlchemyAPI()

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