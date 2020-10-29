from flask import Flask, render_template, redirect
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_script import Manager
from resources.user import AllUsers, SecretResource, TokenRefresh, TokenRemove, UserHome,UserLogin, UserRegistration, ConfirmRegistration, UnconfirmedRegistration
from resources.images import ImageSummary, ImageUpload, ImageCollection, ImageRetrieve
from resources.trips import NewTrip, Trips
from models.trips import TripsModel
from models.markers import MarkerModel
from models.images import ImagesModel
from models.user import UserModel
import datetime
# create flask application
app = Flask(__name__)
# create restful api
api = Api(app)
app.config.from_pyfile('yourconfig.cfg')

jwt = JWTManager(app)


@app.before_first_request
def create_tables():
    #db.drop_all()
    db.create_all()

    user = UserModel(
        email = "play.python.test@gmail.com",
        confirmed= True,
        registered_on=datetime.datetime(2020, 10, 23)
    )
    user.set_password("Test123#")
    # user.set_username()

    marker = MarkerModel(
        id = 'pin',
        icon = 'filepath',
        anchor_x = 1,
        anchor_y = 1
    )
    # define user_id depending on wheather user exists or not
    # if UserModel.check_user(email=user.email):
    #     user_id = int(UserModel.check_user(email=user.email).id) + 1
    # else:
    #     user_id = 1

    trip = TripsModel(
        user_id = user.id,
        trip_id = 'Covid w PL',
        description = 'Pandemia time in Poland',
        marker_colour = 'pink',
        marker_id= 'pin',
        countries= ['Poland']
    )

    if not UserModel.check_user(email=user.email):
        user.save_to_db()
        if not MarkerModel.find_by_id(marker_id=marker.id):
            marker.save_to_db()
        trip.user_id = UserModel.check_user(email=user.email).id
        trip.save_to_db()

        
   
        
    # try: 
    #     UserModel.check_user(email=user.email).delete()
    # except Exception:
    #     user.save_to_db()
    # else:
    #     user.save_to_db()
    # try:
    #     MarkerModel.find_by_id(marker_id=marker.id).delete()
    # except Exception:
    #     marker.save_to_db()
    # else:
    #     marker.save_to_db()
    # try:
    #     TripsModel.find_by_id(trip_id=trip.trip_id).delete()
    # except Exception:
    #     trip.save_to_db()
    # else:
    #     trip.save_to_db()

        

@app.route('/')
def home():
    return redirect('/signin')

# @app.route('/<string:user>/home')



api.add_resource(UserLogin, '/signin')
api.add_resource(UserRegistration, '/register')
api.add_resource(ConfirmRegistration, '/confirmreg/<token>')
api.add_resource(UnconfirmedRegistration, '/unconfirmed')
api.add_resource(AllUsers, '/users')
api.add_resource(TokenRefresh, '/token/refresh')
api.add_resource(SecretResource, '/secret')
api.add_resource(UserHome, '/home/<user_id>')
api.add_resource(TokenRemove,'/token/remove')
# api.add_resource(ImageSummary,'/home/<user_id>/photos')
# api.add_resource(ImageRetrieve,'/home/<user_id>/photos/<trip_id>')
# api.add_resource(ImageUpload, '/home/<user_id>/upload')
api.add_resource(ImageRetrieve,'/photos/<user_id>/<filename>')
api.add_resource(ImageSummary,'/home/photos/<user_id>')
api.add_resource(ImageCollection,'/home/photos/<user_id>/<trip_id>')
api.add_resource(ImageUpload, '/home/upload/<user_id>')
api.add_resource(NewTrip, '/home/trips/<user_id>/addtrip')
api.add_resource(Trips, '/home/trips/<user_id>')


if __name__ == "__main__":
    from db import db
    from mail import mail
    db.init_app(app)
    mail.init_app(app)
    app.run(port=5000, debug=True)

