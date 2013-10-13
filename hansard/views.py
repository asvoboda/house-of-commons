from hansard import app

from flask import jsonify, render_template
from flask.ext.restful import reqparse

from models import MP, Quotation, Entity, from_quotations, to_quotations

from alchemyapi import AlchemyAPI

import unicodedata
import os

import pdb

parser = reqparse.RequestParser()
parser.add_argument('limit', type=int, help='Limit for query length')
parser.add_argument('sentiment', type=int, help='Perform sentiment analysis')
parser.add_argument('entities', type=int, help='Perform entity analysis')

alchemyapi = AlchemyAPI()

@app.route('/mps/<int:mp_id>')
def mp(mp_id):
	mp = MP.query.get(mp_id)
	
	if mp:
		response = {'mp': mp.serialize}
		response['from_quotations'] = [q.serialize for q in mp.from_quotations]
		response['to_quotations'] = [q.serialize for q in mp.to_quotations]
		return jsonify(response)
	return "Error: Not Found", 404

@app.route('/mps')
def mps():
	args = parser.parse_args()
	limit = args.get("limit") if args.has_key("limit") else None
	mp_query = MP.query.limit(limit) if limit else MP.query
	return jsonify(data=[mp.serialize for mp in mp_query.all()])
		
@app.route('/quotations/<int:quotation_id>')
@app.route('/explore/quotations/<int:quotation_id>', alias=True)
def quotation(quotation_id):
	args = parser.parse_args()
	#entities = args.get("entities") if args.has_key("entities") else None
	#sentiment = args.get("sentiment") if args.has_key("sentiment") else None
	quot = Quotation.query.get(quotation_id)
	response = {'quotation': quot.serialize}
	entities = Entity.query.filter(Entity.quotation==quotation_id).all()
	if entities:
		response['entities'] = [e.serialize for e in entities]

	if quot:
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
	return render_template('index.html')
	
@app.route('/explore')
def explore():
	return render_template('explore.html')
	
@app.route('/explore/mps/<int:mp_id>')
def explore_mps(mp_id):
	mp = MP.query.get(mp_id)
	if mp:
		response = {}
		quotations_from = mp.from_quotations
		quotations_to = mp.to_quotations
		
		q_from = [q.serialize for q in quotations_from]
		q_to = [q.serialize for q in quotations_to]
		return jsonify({'mp': mp.serialize, 'q_from': q_from, 'q_to': q_to})
	return "Error: Not Found", 404