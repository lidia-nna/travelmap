from flask import redirect, request, flash
from flask.templating import render_template
from flask.helpers import make_response
from flask_restful import Resource, reqparse
from models.trips import TripsModel
from models.images import ImagesModel
from flask_jwt_extended import jwt_required
from flask.helpers import url_for
import os
import werkzeug
from metadata import MetadataExtractor

global trips
trips = ['Spain', 'France', 'Poland', 'UK']

class Images(Resource):
    # @jwt_required
    def get(self, user_id):
        return make_response(render_template("album.html",  user_id=user_id, trips=trips), 200)
        # return make_response(render_template("album_bootstr.html", trips=TripsModel.find_trip_list()), 200)

class ImageUpload(Resource):
    UPLOAD_FOLDER = os.getcwd() + '\\uploads'

    # @jwt_required
    def get(self, user_id):
        headers = {'Content-Type': 'text/html'}
        return make_response(
            render_template('upload.html', user_id=user_id, trips=trips), 200, headers)

    # @jwt_required
    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'files', type=werkzeug.datastructures.FileStorage, location='files', action='append')
        parser.add_argument('trip_id', location='form')
        # parser.add_argument('filenames[]', location='form',  action='append')
        data = parser.parse_args()
        # try if not data['files']:
        if data['files'] == "" or data['files'] == []:
            return redirect(request.url)
        photos = data['files']
        trip_id = data['trip_id']
        # filenames = data['filenames[]']
        # record files with missing geodata
        missing_tags = {}
        # r' in split expression acts as raw literal
        # filename = re.split(r'\\|/|//', filename)[-1]
        # names = [photo.filename for photo in photos]
        # assert len(names) == len(filenames)

        for i, photo in enumerate(photos):
            filepath = os.path.join(ImageUpload.UPLOAD_FOLDER, photo.filename)
            photo.save(filepath)
            try:
                imageMetadata = MetadataExtractor(filepath)
                imageMetadata.extract()
                if imageMetadata.find_empty_tags():
                    missing_tags[filepath] = imageMetadata.find_empty_tags()
            except Exception as e:
                print(str(e))
                raise str(e)
            newImage = ImagesModel(
                None,
                filepath,
                imageMetadata.country,
                imageMetadata.city,
                trip_id,
                imageMetadata.lat,
                imageMetadata.lng,
                imageMetadata.timestamp,
                None,
                user_id
            )
            #newImage.save_to_db()
            flash('File successfully uploaded')
            # return redirect('/')
        return [
            11,
            filepath,
            imageMetadata.country,
            imageMetadata.city,
            trip_id,
            imageMetadata.lat,
            imageMetadata.lng,
            imageMetadata.timestamp,
            None,
            user_id
        ]
        return {'message': 'Could not find the image'}, 400
        # return redirect(request.url)