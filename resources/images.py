from flask import redirect, request, flash
from flask.templating import render_template
from flask.helpers import make_response
from flask_restful import Resource, reqparse
from models.trips import TripsModel
from models.images import ImagesModel
from flask_jwt_extended import jwt_required
from flask.helpers import send_from_directory, url_for
import os
import werkzeug
from metadata import MetadataExtractor
from thumbnail import SquaredThumbnail

global UPLOAD_FOLDER
UPLOAD_FOLDER = os.path.join( os.getcwd(), 'photos')

class ImageRetrieve(Resource):
    def get(self, user_id, filename):
        return send_from_directory(os.path.join(UPLOAD_FOLDER, user_id), filename)

class ImageSummary(Resource):
    # @jwt_required
    def get(self, user_id):
        trips=TripsModel.find_trip_list(user_id=user_id) 
        #images=[ImagesModel.find_thumbnails( trip_id=trip, user_id=user_id) for trip in trips][0] 
        cover_pairs = dict()
        for trip in trips:
            # no images in trip
            if ImagesModel.find_thumbnails(trip_id=trip, user_id=user_id):
                front_image = ImagesModel.find_thumbnails(
                trip_id=trip, user_id=user_id)[0]
            else:
                front_image = "blank_page.png"
            cover_pairs.update({trip:front_image})
        return make_response(render_template("photo_album.html",  user_id=user_id, covers=cover_pairs), 200)

class ImageCollection(Resource):
    def get(self, trip_id, user_id):
        return make_response( render_template(
            'trip_collection.html', 
            trip_id=trip_id, 
            user_id=user_id, 
            images=ImagesModel.find_thumbnails(trip_id=trip_id, user_id=user_id)
            )
        )
class ShowImage(Resource):
    def get(self, trip_id, user_id):
        return make_response( render_template(
            'trip_collection.html', 
            trip_id=trip_id, 
            user_id=user_id, 
            images=ImagesModel.find_thumbnails(trip_id=trip_id, user_id=user_id)
            )
        )

class ImageUpload(Resource):
    # @jwt_required
    def get(self, user_id): 
        parser = reqparse.RequestParser()
        parser.add_argument(
            'trip_id', 
            type=str # trip_id set to None for cases when upload is done to an existing trip (using trips parameter) as opposed to just added one (trip_id)
        )
        data = parser.parse_args()
        print(data)
        headers = {'Content-Type': 'text/html'}
        return make_response(
            render_template('upload.html', user_id=user_id, trip_id = data.trip_id, trips=TripsModel.find_trip_list(user_id=user_id)), 200, headers)


    # @jwt_required
    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'files', 
            type=werkzeug.datastructures.FileStorage, 
            location='files', 
            action='append')
        parser.add_argument('trip_id', location='form')
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
        upload_dir = os.path.join(UPLOAD_FOLDER, user_id)
        print(f'upload_dir: {upload_dir}')
        if not os.path.isdir(upload_dir):
            os.makedirs(upload_dir)
        for i, photo in enumerate(photos):
            filepath = os.path.join(upload_dir, photo.filename)
            photo.save(filepath)
            print(f'filepath: {filepath}')
            try:
                imageMetadata = MetadataExtractor(filepath)
                imageMetadata.extract()
                if imageMetadata.find_empty_tags():
                    missing_tags[filepath] = imageMetadata.find_empty_tags()
                
            except Exception as e:
                print(str(e))
                raise str(e)     
            thumb=SquaredThumbnail(
                filepath = filepath, 
                new_side = 400,
                orientation = imageMetadata.orientation
                )
            thumb.gen_thumbnail()
            thumb.crop_thumbnail()           
            newImage = ImagesModel(
                image_id = None,
                filepath = filepath,
                country = imageMetadata.country,
                city = imageMetadata.city,
                trip_id = trip_id,
                lattitude = imageMetadata.lat,
                longitude = imageMetadata.lng,
                timestamp = imageMetadata.timestamp,
                marker_id = None,
                user_id = user_id
            )
            newImage.save_to_db()

        print(f'----------Missing_tags----------------------: {missing_tags}')
        flash('Files successfully uploaded!', 'success')
            # return redirect('/')
        return redirect(url_for('imageupload', user_id=user_id, trips=TripsModel.find_trip_list(user_id=user_id)))
        # return [
        #     11,
        #     filepath,
        #     imageMetadata.country,
        #     imageMetadata.city,
        #     trip_id,
        #     imageMetadata.lat,
        #     imageMetadata.lng,
        #     imageMetadata.timestamp,
        #     None,
        #     user_id
        # ]
        #return {'message': 'Could not find the image'}, 400
        # return redirect(request.url)