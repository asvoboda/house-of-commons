from flask import Flask, jsonify, abort, request, make_response, url_for
from flask.ext.restful import reqparse, abort, Api, Resource
from flask.ext.sqlalchemy import SQLAlchemy

from flask import render_template

from database import init_db
from models import MP, Quotation

import pdb

def create_app():
	app = Flask(__name__)
	db = SQLAlchemy(app)
	db.init_app(app)
	return app
	
app = create_app()
api = Api(app)

parser = reqparse.RequestParser()

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
		return jsonify(mps=[mp.serialize for mp in MP.query.all()])
		
class QuotationR(Resource):
	def abort(self):
		return 'No Quotation', 404
		
	def get(self, quotation_id):
		quot = Quotation.query.get(quotation_id)
		if quot:
			return jsonify(quot.serialize)
		return self.abort()
		
class QuotationListR(Resource):
	def get(self):
		return [q.serialize for q in Quotation.query.all()]

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