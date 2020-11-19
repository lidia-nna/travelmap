from flask import render_template, make_response
from flask_restful import Resource, reqparse
from models.trips import TripsModel
from models.images import ImagesModel
import werkzeug
import os

class Trips(Resource):



    def get(self, user_id):
        return make_response(
            render_template(
                'trips.html', 
                user_id = user_id, 
                markers = TripsModel.find_coordinates(user_id=user_id), 
                trips = TripsModel.find_trip_colours(user_id=user_id),
                key = os.environ.get('GM_API_KEY')),
            200)

    def delete(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument(
        'trip_id', 
        type=str # trip_id set to None for cases when upload is done to an existing trip (using trips parameter) as opposed to just added one (trip_id)
    )
        data = parser.parse_args()
        record = TripsModel.find_by_id(trip_id=data.trip_id, user_id=user_id)
        images = ImagesModel.find_by_trip(trip_id=data.trip_id, user_id=user_id)
        filepaths = (image.filepath for image in images)
        
        try:
            TripsModel.delete(record)
        except Exception as e:
            print(f'Could not remove trip {data.trip_id}: {e}')
            return {'message': 'Removal unsuccessul'}
        else:
            for filepath in filepaths:
                try:
                    ImagesModel.delete_files(filepath)
                except OSError as e:
                    raise RuntimeWarning(f'Image does not exist') from e
                except IOError as e: 
                    raise RuntimeWarning(f'No permissions to remove the image') from e
                else:
                    print(f'Image {filepath} removed!') 
                    




class NewTrip(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'trip_id',
        type=str,
        location='form',
        required=True,
        help="This field cannot be left blank!"
    )
    parser.add_argument(
        'description',
        type=str,
        location='form',
        required=True,
        help="This field cannot be left blank!"
    )
    parser.add_argument(
        'marker_colour',
        type=str,
        location='form',
        required=True,
        help="This field cannot be left blank!"
    )
    parser.add_argument(
        'marker_id',
        type=str,
        location='form',
        required=True,
        help="This field cannot be left blank!"
    )
        
    parser.add_argument(
        'countries',
        type=list,
        location='form',
        help="This field cannot be left blank!"
    )

    def get(self, user_id):
        return make_response(
            render_template(
                'add_trip.html', user_id=user_id
                ),
            200, {'Content-Type': 'text/html'})

    def post(self, user_id):
        data = NewTrip.parser.parse_args()
        if TripsModel.find_by_id(trip_id=data['trip_id'], user_id=user_id):
            return {'message': 'Trip already exists'}, 201
        try:
            trip_id = data['trip_id']
            description = data['description']
            marker_colour = data['marker_colour']
            marker_id = data['marker_id']           
            countries = data['countries']
            newTrip = TripsModel(
                user_id = user_id,
                trip_id=trip_id, 
                description=description, 
                marker_colour=marker_colour, 
                marker_id = marker_id,
                countries=countries)
        except Exception as e:
            return (str(e)), 400
        else:
            newTrip.save_to_db()
            #return make_response(render_template('add_images.html', markers=TripsModel.json()),200,headers)
            return 200



