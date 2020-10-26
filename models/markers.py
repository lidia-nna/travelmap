from db import db

class MarkerModel(db.Model):

    __tablename__ = 'markers'

    id = db.Column(db.String(100), primary_key=True)
    icon = db.Column(db.String(250))
    anchor_x = db.Column(db.SMALLINT)
    anchor_y = db.Column(db.SMALLINT)
    # country = db.relationship('CountryModel')
    images = db.relationship("ImagesModel")
    trips = db.relationship("TripsModel")
    
    @classmethod
    def find_all_markers(cls):
        return [marker.id for marker in cls.query.all()]

    @classmethod
    def find_by_id(cls, marker_id):
        return cls.query.filter_by(id=marker_id).first()


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
