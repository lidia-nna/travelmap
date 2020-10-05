from db import db
from datetime import datetime
from flask import jsonify

class ImagesModel(db.Model):

    __tablename__ = 'images'

    image_id = db.Column(db.Integer, primary_key=True)
    filepath = db.Column(db.String(255))
    country = db.Column(db.String(255))#, db.ForeignKey('country_centre.name'))
    city = db.Column(db.String(255))
    trip_id = db.Column(db.String(255), db.ForeignKey('trips.trip_id'))
    lattitude = db.Column(db.Float(precision=3))
    longitude = db.Column(db.Float(precision=3))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    marker_id = db.Column(db.String(100), db.ForeignKey('markers.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # countries = db.relationship("CountryModel")
    markers = db.relationship("MarkerModel")
    trips = db.relationship("TripsModel")
    users = db.relationship("UserModel")
    

    def __init__(self, user_id, image_id, filepath, country, city, trip_id, lattitude, longitude, timestamp, marker_id):
        self.image_id = image_id
        self.filepath = filepath
        self.country = country
        self.city = city
        self.trip_id = trip_id
        self.lattitude = lattitude
        self.longitude = longitude
        self.timestamp = timestamp
        self.marker_id = marker_id
        self.user_id = user_id

    @classmethod
    def find_by_trip(cls, id, user_id):
        return cls.query.filter_by(trip_id=id, user_id=user_id).all()

    @classmethod
    def find_all_images(cls):
        return cls.query.all()

    @staticmethod
    def json(id):
        return jsonify([(row.country, row.city) for row in ImagesModel.find_by_id(id=id)])


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
