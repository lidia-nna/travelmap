from flask_script import Manager
from db import db
from models.trips import TripsModel
from models.markers import MarkerModel
from models.images import ImagesModel

from app import app

manager = Manager(app)

marker = MarkerModel(
    id = 'pin',
    icon = 'filepath',
    anchor_x = 1,
    anchor_y = 1
    )
trip = TripsModel(
    user_id = 'lid.mijas',
    trip_id = 'Covid w PL',
    trip_marker_id = 'pin' 
    )

@manager.command
def populator():
    marker.save_to_db()
    trip.save_to_db()

if __name__ == "__main__":
    manager.run()