from hansard import app

from flask import jsonify, render_template
from flask.ext.restful import reqparse
from hansard.utils import serialize_list, top, unique

from models import MP, Quotation, Entity, Keyword, from_quotations, to_quotations

import urllib
import collections

parser = reqparse.RequestParser()
parser.add_argument('limit', type=int, help='Limit for query length')

parser.add_argument('type', type=str)
parser.add_argument('search', type=str)
parser.add_argument('search_type', type=str)

parser.add_argument('from_date', type=str)
parser.add_argument('to_date', type=str)


@app.route('/mps/<int:mp_id>')
def mp_by_id(mp_id):
    mp = MP.query.get(mp_id)
    if mp:
        quotations_from = mp.from_quotations
        quotations_to = mp.to_quotations

        q_from = [q.serialize for q in quotations_from]
        q_to = [q.serialize for q in quotations_to]
        return jsonify(data=[{'mp': mp.serialize, 'quotations_from': q_from, 'quotations_to': q_to}])
    return "Error: Not Found", 404


@app.route('/mps/<string:term>')
def mps_by_term(term):
    decoded_term = urllib.unquote(term).decode('utf8')
    mps = MP.query.filter(MP.name.ilike('%' + decoded_term + '%'))
    response = []
    for mp in mps:
        quotations_from = [q.serialize for q in mp.from_quotations]
        quotations_to = [q.serialize for q in mp.to_quotations]
        response.append({'mp': mp.serialize, 'quotations_from': quotations_from, 'quotations_to': quotations_to})
    return jsonify(data=response)


@app.route('/mps')
def mps():
    args = parser.parse_args()
    limit = args.get("limit") if args.has_key("limit") else None
    mps = MP.query.limit(limit) if limit else MP.query
    return jsonify(data=[mp.serialize for mp in mps.all()])


@app.route('/quotations/<int:quotation_id>')
def quotation_by_id(quotation_id):
    args = parser.parse_args()
    #entities = args.get("entities") if args.has_key("entities") else None
    #sentiment = args.get("sentiment") if args.has_key("sentiment") else None
    quot = Quotation.query.get(quotation_id)
    response = {'quotation': quot.serialize}
    entities = Entity.query.filter(Entity.quotation_id == quotation_id).all()
    if entities:
        response['entities'] = [e.serialize for e in entities]

    if quot:
        return jsonify(data=[response])
    return "Error: Not Found", 404


@app.route('/quotations/<string:term>')
def quotations_by_term(term):
    decoded_term = urllib.unquote(term).decode('utf8')
    entities = Entity.query.filter(Entity.text.ilike('%' + decoded_term + '%')).order_by(-Entity.relevance).limit(20)
    keywords = Keyword.query.filter(Keyword.text.ilike('%' + decoded_term + '%')).order_by(-Keyword.relevance).limit(20)

    q_k = [k.quotation for k in keywords.all()]
    q_e = [e.quotation for e in entities.all()]
    quotations = list(set((q_k + q_e)))
    response = []
    for quotation in quotations:
        q = {'quotation': quotation.serialize}
        entities = Entity.query.filter(Entity.quotation_id == quotation.id).all()
        keywords = Keyword.query.filter(Keyword.quotation_id == quotation.id).limit(10)
        if entities:
            q['entities'] = [e.serialize for e in entities]
        if keywords:
            q['keywords'] = [k.serialize for k in keywords]
        response.append(q)

    return jsonify(data=response)


@app.route('/quotations')
def quotations():
    args = parser.parse_args()
    limit = args.get("limit") if args.has_key("limit") else None
    q_query = Quotation.query.limit(limit) if limit else Quotation.query

    return jsonify(data=[q.serialize for q in q_query.all()])


@app.route('/entities/<string:term>')
def entities(term):
    decoded_term = urllib.unquote(term).decode('utf8')
    entities = Entity.query.filter(Entity.text.ilike('%' + decoded_term + '%'))

    if entities:
        response = {'entities': [e.serialize for e in entities]}
        return jsonify(response)
    return "Error: Not Found", 404


@app.route('/keywords/<string:term>')
def keywords(term):
    decoded_term = urllib.unquote(term).decode('utf8')
    keywords = Keyword.query.filter(Keyword.text.ilike('%' + decoded_term + '%'))
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
    type = args.get("type") if "type" in args else None
    search = args.get("search") if "search" in args else None

    if not search:
        return "Error: Not Found", 404

    decoded_search = urllib.unquote(search).decode('utf8')
    quotations = []
    if type == "mps":
        response = {}
        #entities = Entity.query.filter(Entity.text.like('%' + decoded_search + '%')).order_by(-Entity.relevance)
        keywords = Keyword.query.filter(Keyword.text.ilike('%' + decoded_search + '%')).order_by(-Keyword.relevance)
        qu = [k.quotation for k in keywords.all()]

        from_mps = [q.from_mp for q in qu]
        highest_from = serialize_list(top(from_mps, 5))

        target_mps = []
        for q in qu:
            if q.target_mp is not None:
                target_mps.append(q.target_mp)

        highest_target = serialize_list(top(target_mps, 5))

        return jsonify({'Speaking': serialize_list(unique(from_mps)), 'Speaking-Often': highest_from,
                        'Spoken': serialize_list(unique(target_mps)), 'Spoken-Often': highest_target})
    elif type == "quotations":
        keywords = Keyword.query.filter(Keyword.text.ilike('%' + decoded_search + '%')).order_by(-Keyword.relevance).limit(20)
        q_k = [k.quotation.serialize for k in keywords.all()]
        return jsonify({'quotations': q_k})

    return "Error: Not Found", 404