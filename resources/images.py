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
from metadata import MetadataExtractor, ReverseGeocoding
from thumbnail import SquaredThumbnail

global UPLOAD_FOLDER
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')

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
                #print(ImagesModel.find_thumbnails(trip_id=trip, user_id=user_id))
                _ , front_image = ImagesModel.find_thumbnails(
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
            images=ImagesModel.find_thumbnails(trip_id=trip_id, user_id=user_id),
            description=TripsModel.find_by_id(trip_id=trip_id, user_id=user_id).description
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

    @staticmethod
    def set_city(x):
        try:
            city = x[0]
        except IndexError:
            pass
        else:
            if len(x)> 1:
                city = ", ".join(x)
            return city

    def get_geolocation(self, lat, lng):
        try:
            gmaps = ReverseGeocoding(lat, lng)
            gmaps.find_locations()
        except RuntimeError as e:
            raise TypeError('Googlemaps API exception, no results restrieved') from e
        if gmaps.get_country():
            country = gmaps.get_country()[0]
        geodata = [
            gmaps.get_city(), 
            gmaps.get_area_level1(), 
            gmaps.get_area_level2()
        ]
        for loc in geodata:
            if self.set_city(loc):
                return self.set_city(loc), country

    def make_thumbnail(self, *args, **kwargs):
        thumb=SquaredThumbnail(*args, **kwargs)
        thumb.gen_thumbnail()
        thumb.crop_thumbnail()    

    # @jwt_required
    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'files', 
            type=werkzeug.datastructures.FileStorage, 
            location='files', 
            action='append')
        parser.add_argument(
            'trip_id', 
            location='form')
        data = parser.parse_args()
        # try if not data['files']:
        if not data['files']:
            return redirect(request.url)
        photos = data['files']
        trip_id = data['trip_id']
        missing_tags = {}
        upload_dir = os.path.join(UPLOAD_FOLDER, user_id)
        if not os.path.isdir(upload_dir):
            os.makedirs(upload_dir)
        for i, photo in enumerate(photos):
            filepath = os.path.join(upload_dir, photo.filename)
            photo.save(filepath)
            try:
                imageMetadata = MetadataExtractor(filepath)
                imageMetadata.extract()
            except Exception as e:
                # TODO case with no/wrong GPS data, extract info about countries
                print('No GPS data')
            else:
                lat = imageMetadata.lat
                lng = imageMetadata.lng
                if lat is not None and lng is not None:
                    # should city, country be part of imageMetadata class if not set by the instance method
                    try:
                        imageMetadata.city, imageMetadata.country = self.get_geolocation(lat, lng)
                    #catch googlemaps API fuilure
                    except TypeError as e:
                        raise RuntimeWarning('Googlemaps API failure no geolocation results retrieved!') from e
                    
            finally:
                missing_tags[filepath] = imageMetadata.find_empty_tags() 
            # crete ORM image record       
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
            print(vars(newImage))
            # save record to db
            try:
                newImage.save_to_db()
            except Exception as e:
                print('Postgres Error while saving image data' + str(e))
                os.remove(filepath)
                flash('Upload failed!', 'failure')
                return redirect(url_for('imageupload', user_id=user_id, trips=TripsModel.find_trip_list(user_id=user_id)))    
            else:
                # generate thumbnail
                self.make_thumbnail(
                filepath = filepath, 
                new_side = 400,
                orientation = imageMetadata.orientation
                )

        print(f'----------Missing_tags----------------------: {missing_tags}')
        flash('Files successfully uploaded!', 'success')
            # return redirect('/')
        return redirect(url_for('imageupload', user_id=user_id, trips=TripsModel.find_trip_list(user_id=user_id)))    

    def delete(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument(
        'image_id', 
        type=int # trip_id set to None for cases when upload is done to an existing trip (using trips parameter) as opposed to just added one (trip_id)
    )
        data = parser.parse_args()
        print(data)
        headers = {'Content-Type': 'text/html'}
        image = ImagesModel.find_by_id(data.image_id)
        # change delete method
        try:
            ImagesModel.delete(image)
        except OSError as e:
            print(f'Image does not exist --- {e}')
            return {'message': 'Removal unsuccessul'}
        except IOError as e: 
            print(f'No permissions to remove the image --- {e}')
            return {'message': 'Removal unsuccessul'}
        else:
            return {'message': 'Image removed'}
        


        
