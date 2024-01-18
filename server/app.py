#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''



class Missions(Resource):
    def post(self):
        data = request.get_json()
        mission = Mission()
        try:
            mission.name = data.get('name')
            mission.planet_id = data.get('planet_id')
            mission.scientist_id = data.get('scientist_id')
            db.session.add(mission)
            db.session.commit()
            return make_response(mission.to_dict(rules=("planet", "scientist")), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
        
api.add_resource(Missions, '/missions')


class Planets(Resource):
    def get(self):
        return make_response([planet.to_dict(rules=("-missions",)) for planet in Planet.query.all()], 200)
    
api.add_resource(Planets, '/planets')


class Scientists(Resource):
    def get(self):
        return make_response([scientist.to_dict() for scientist in Scientist.query.all()], 200)
    
    def post(self):
        data = request.get_json()
        scientist = Scientist()
        try:
            scientist.name = data.get('name')
            scientist.field_of_study = data.get('field_of_study')
            db.session.add(scientist)
            db.session.commit()
            return make_response(scientist.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

# Add a Resource (API endpoint) for each model here
api.add_resource(Scientists, '/scientists')

class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.get(id)
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        else:
            return make_response(scientist.to_dict(rules=("missions", "-missions.scientist")), 200)
        
    def patch(self, id):
        data = request.get_json()
        scientist = Scientist.query.get(id)
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        else:
            try:
                for attr in data:
                    setattr(scientist, attr, data[attr])
                db.session.add(scientist)
                db.session.commit()
                return make_response(scientist.to_dict(), 202)
            except ValueError as e:
                return make_response({"errors": ["validation errors"]}, 400)
    
    def delete(self, id):
        scientist = Scientist.query.get(id)
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        else:
            db.session.delete(scientist)
            db.session.commit()
            return make_response({}, 204)

# Add a Resource (API endpoint) for each model here
api.add_resource(ScientistById, '/scientists/<int:id>')



if __name__ == '__main__':
    app.run(port=5555, debug=True)

