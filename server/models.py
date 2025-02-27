from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship

    missions = db.relationship('Mission', back_populates='planet', cascade='all, delete-orphan')
    scientists = association_proxy('missions', 'scientist')
    
    # Add serialization rules to prevent recursion
    serialize_rules = ('-missions.planet', '-missions.scientist')

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)

    # Add relationship

    missions = db.relationship('Mission', back_populates='scientist', cascade='all, delete-orphan')
    planets = association_proxy('missions', 'planet')
    
    # Add serialization rules to prevent recursion
    serialize_rules = ('-missions',)
    
    # Add validation

    @validates('name', 'field_of_study')
    def valiestes_presence(self, key, value):
        if not value:
            raise ValueError(f"Scientists must have a {key}.")
        return value
    

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))

    # Add relationships

    planet = db.relationship('Planet', back_populates='missions')
    scientist = db.relationship('Scientist', back_populates='missions')
    
    # Add serialization rules to prevent recursion
    serialize_rules = ('-planet.missions', '-scientist.missions')
    
    # Add validation
    
    @validates('name')
    def validates_name(self, key, name):
        if not name:
            raise ValueError("Missions must have a name.")
        return name
    
    @validates('planet_id')
    def validates_planet_id(self, key, planet_id):
        planet = Planet.query.get(planet_id)
        if not planet:
            raise ValueError("Planet id must reference an existing planet.")
        if not planet_id:
            raise ValueError("Missions must have a planet.")
        return planet_id
    
    @validates('scientist_id')
    def validates_scientist_id(self, key, scientist_id):
        scientist = Scientist.query.get(scientist_id)
        if not scientist:
            raise ValueError("Scientist id must reference an existing scientist.")
        if not scientist_id:
            raise ValueError("Missions must have a scientist.")
        return scientist_id


# add any models you may need.
