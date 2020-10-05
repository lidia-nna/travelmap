from flask import Flask, render_template, redirect
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_script import Manager
from resources.user import AllUsers, SecretResource, TokenRefresh, TokenRemove, UserHome,UserLogin, UserRegistration, ConfirmRegistration, UnconfirmedRegistration
from resources.images import Images, ImageUpload
from models.trips import TripsModel
from models.markers import MarkerModel
from models.images import ImagesModel
from models.user import UserModel
# create flask application
app = Flask(__name__)
# create restful api
api = Api(app)
app.config.from_pyfile('yourconfig.cfg')

jwt = JWTManager(app)


@app.before_first_request
def create_tables():
    db.drop_all()
    db.create_all()

    user = UserModel(
        email = "play.python.test@gmail.com",
        confirmed= True
    )
    user.set_password("Test123#")
    user.set_username()

    marker = MarkerModel(
        id = 'pin',
        icon = 'filepath',
        anchor_x = 1,
        anchor_y = 1
    )
    trip = TripsModel(
        user_id = '1',
        trip_id = 'Covid w PL',
        trip_marker_id = 'pin' 
    )
    # user.save_to_db()
    # marker.save_to_db()
    # trip.save_to_db()
    try: 
        user.delete()
    except Exception:
        user.save_to_db()
    else:
        user.save_to_db()
    try:
        marker.delete()
    except Exception:
        marker.save_to_db()
    else:
        marker.save_to_db()
    try:
        trip.delete()
    except Exception:
        trip.save_to_db()
    else:
        trip.save_to_db()

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
api.add_resource(Images,'/home/<user_id>/photos')
api.add_resource(ImageUpload, '/home/<user_id>/upload')


if __name__ == "__main__":
    from db import db
    from mail import mail
    db.init_app(app)
    mail.init_app(app)
    app.run(port=5000, debug=True)

