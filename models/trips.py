from db import db
from models.images import ImagesModel
from models.markers import MarkerModel


class TripsModel(db.Model):

    __tablename__ = 'trips'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    trip_id = db.Column(db.String(255),primary_key=True)
    description = db.Column(db.String(255))
    marker_colour = db.Column(db.String(100))
    marker_id = db.Column(db.String(100), db.ForeignKey('markers.id'))
    countries = db.Column(db.PickleType)
    markers = db.relationship("MarkerModel")
    images = db.relationship("ImagesModel")
    users = db.relationship("UserModel")#, cascade="all, delete", backref="children")
    
    def __init__(self, user_id, trip_id, description, marker_colour, marker_id, countries):
        self.user_id = user_id
        self.trip_id = trip_id
        self.description = description
        self.marker_colour = marker_colour
        self.marker_id = marker_id
        if countries:
            self.countries = countries
        else:
            self.countries = None


    # (select * from trip_details join markers on trip_details.trip_marker_id=markers.id) as foo
    @classmethod
    def find_trip_markers(cls):
        return db.session.query(cls,MarkerModel).join(MarkerModel, cls.trip_marker_id == MarkerModel.id).subquery()

    # select images.lattitude, images.longitude, images.city, foo.icon, foo.anchor_x, foo.anchor_y from images where images.user="user" join
    # (select * from trip_details join markers on trip_details.trip_marker_id=markers.id) as foo on images.trip_id=foo.trip_id;
    @classmethod
    def find_all_trips(cls, user_id):
        trip_id_markers = cls.find_trip_markers()
        rows = db.session.query(ImagesModel.lattitude.label('lat'), ImagesModel.longitude.label('lng'),
                                ImagesModel.city, trip_id_markers.c.icon, trip_id_markers.c.anchor_x,
                                trip_id_markers.c.anchor_y)\
            .join(trip_id_markers, ImagesModel.trip_id == trip_id_markers.c.trip_id)#.filter(ImagesModel.user_id==user) #filter by user
        
        return rows
    @classmethod
    def find_trip_list(cls, user_id):
        return [trip_id_tuple[0] for trip_id_tuple in list(db.session.query(cls.trip_id).filter_by(user_id=user_id))]

    @staticmethod
    def json():
        rows = TripsModel.find_all_trips()
        return [
            {
                'lat': row.lat,
                'lng': row.lng,
                'city': row.city,
                'icon_uri': row.icon,
                'anchor_x': row.anchor_x,
                'anchor_y': row.anchor_y
            }
            for row in rows
        ]
    @classmethod
    def find_by_id(cls, trip_id, user_id):
        return cls.query.filter_by(trip_id=trip_id).filter_by(user_id=user_id).first()

    @classmethod
    def find_all(cls, user_id):
        #with user
        query = db.session.query(ImagesModel.user_id, cls).join(ImagesModel.trip_id==cls.trip_id)#.filter(cls.user_id==user)
        # without user
        # query = cls.query.all()
        if len(query) != 0:
            return query


    @classmethod
    def find_coordinates(cls, user_id):
        query = db.session.query(
            cls.marker_colour, 
            ImagesModel.filepath, 
            ImagesModel.lattitude, 
            ImagesModel.longitude).join(ImagesModel, (ImagesModel.trip_id==cls.trip_id) & (ImagesModel.user_id==cls.user_id)).filter(cls.user_id == user_id)
        return [
            {
                'lat': row.lattitude,
                'lng': row.longitude,
                'filepath': row.filepath,
                'colour': row.marker_colour
            }
            for row in query
        ]
    @classmethod
    def find_trip_colours(cls, user_id):
        return db.session.query(cls.trip_id, cls.marker_colour).filter_by(user_id=user_id).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

