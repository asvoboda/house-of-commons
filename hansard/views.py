from hansard import app

from flask import jsonify, render_template
from flask.ext.restful import reqparse

from models import MP, Quotation, Entity, Keyword, from_quotations, to_quotations

from alchemyapi import AlchemyAPI

import unicodedata
import os
import urllib
import collections

import pdb

parser = reqparse.RequestParser()
parser.add_argument('limit', type=int, help='Limit for query length')

parser.add_argument('type', type=str)
parser.add_argument('search', type=str)
parser.add_argument('search_type', type=str)

parser.add_argument('from_date', type=str)
parser.add_argument('to_date', type=str)

alchemyapi = AlchemyAPI()

@app.route('/mps/<int:mp_id>')
def mp(mp_id):
	mp = MP.query.get(mp_id)
	if mp:
		response = {}
		quotations_from = mp.from_quotations
		quotations_to = mp.to_quotations
		
		q_from = [q.serialize for q in quotations_from]
		q_to = [q.serialize for q in quotations_to]
		return jsonify({'mp': mp.serialize, 'quotations_from': q_from, 'quotations_to': q_to})
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
	#entities = args.get("entities") if args.has_key("entities") else None
	#sentiment = args.get("sentiment") if args.has_key("sentiment") else None
	quot = Quotation.query.get(quotation_id)
	response = {'quotation': quot.serialize}
	entities = Entity.query.filter(Entity.quotation_id == quotation_id).all()
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

def unique(list):
	known = set()
	newlist = []

	for item in list:
		if item is None: continue
		id = item.id
		if id in known: continue
		newlist.append(item)
		known.add(id)
	return newlist
	
def top(list, number):
	counter=collections.Counter(list)
	return [i[0] for i in counter.most_common(number)]
	
def serialize_list(list_obj):
	return [l.serialize for l in list_obj]

@app.route('/entities/<string:term>')
def entities(term):
	decoded_term = urllib.unquote(term).decode('utf8') 
	entities = Entity.query.filter(Entity.text.like('%' + decoded_term + '%'))
	
	if entities:
		response = {'entities': [e.serialize for e in entities]}
		return jsonify(response)
	return "Error: Not Found", 404
	
@app.route('/keywords/<string:term>')
def keywords(term):
	decoded_term = urllib.unquote(term).decode('utf8') 
	keywords = Keyword.query.filter(Keyword.text.like('%' + decoded_term + '%'))
	if entities:
		response = {'keywords': [k.serialize for k in keywords]}
		return jsonify(response)
	return "Error: Not Found", 404
	
## PAGES

@app.route('/')
def index():
	return render_template('index.html')
	
@app.route('/explore')
def explore():
	return render_template('explore.html')

	
@app.route('/search')
def search():
	args = parser.parse_args()
	type = args.get("type") if args.has_key("type") else None
	search = args.get("search") if args.has_key("search") else None
	
	if not search:
		return "Error: Not Found", 404

	decoded_search = urllib.unquote(search).decode('utf8') 
	quotations = []
	if type == "mps":
		response = {}
		#entities = Entity.query.filter(Entity.text.like('%' + decoded_search + '%')).order_by(-Entity.relevance)
		keywords = Keyword.query.filter(Keyword.text.like('%' + decoded_search + '%')).order_by(-Keyword.relevance)
		qu = [k.quotation for k in keywords.all()]
		
		from_mps = [q.from_mp for q in qu]
		highest_from = serialize_list(top(from_mps, 5))
		
		target_mps = []
		for q in qu:
			if q.target_mp is not None:
				target_mps.append(q.target_mp)

		highest_target = serialize_list(top(target_mps, 5))
		
		return jsonify({'Speaking': serialize_list(unique(from_mps)), 'Speaking-Often': highest_from, 'Spoken': serialize_list(unique(target_mps)), 'Spoken-Often': highest_target})
	elif type == "quotations":
		keywords = Keyword.query.filter(Keyword.text.like('%' + decoded_search + '%')).order_by(-Keyword.relevance).limit(20)
		q_k = [k.quotation.serialize for k in keywords.all()]
		return jsonify({'quotations': q_k})

	return "Error: Not Found", 404