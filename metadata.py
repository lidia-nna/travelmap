import googlemaps
import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from pprint import pprint
from time import time


class MetadataExtractor:

    def __init__(self, filepath):
        self.GpsTagNames = {
            'GPSLatitudeRef': None,
            'GPSLongitudeRef': None,
            'GPSLatitude': None,
            'GPSLongitude': None
        }
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.orientation = None
        self.timestamp = None
        self.lat = None
        self.lng = None
        self.country = None
        self.city = None
        self.format = None
        self.size = None

    def lookupGpsTag(self, gpsInfo):
        for gk in gpsInfo.keys():
            if GPSTAGS[gk] in self.GpsTagNames.keys():
                self.GpsTagNames[GPSTAGS[gk]] = gpsInfo[gk]
                # print(f'GPSTAGS[gk]: {GPSTAGS[gk]}')

    def extract(self):
        img = Image.open(self.filepath)
        self.filename, ext = os.path.splitext(self.filename)
        try:
            self.format = img.format
            self.size = img.size
            exif = img._getexif()
        except Exception as e:
            print(str(e))

        for k in exif.keys():
            if k in TAGS:
                if TAGS[k] == "DateTimeOriginal":
                    timestamp = exif[k]
                    self.timestamp = timestamp[:10].replace(
                        ':', '-') + timestamp[10:]
                    # for thumbnail generation
                elif TAGS[k] == "Orientation":
                    self.orientation = exif[k]
                elif TAGS[k] == "GPSInfo":
                    print('GPSinfo')
                    self.lookupGpsTag(exif[k])
        # except AttributeError as e:
        #     return "Unknown type: e"
        try:
            # print('GPSLatitude:' + str(self.GpsTagNames['GPSLatitude']))
            # print('GPSLongitude:' + str(self.GpsTagNames['GPSLongitude']))
            self.lat = self.convert_to_decimal_deg(
                self.GpsTagNames['GPSLatitude'], self.GpsTagNames['GPSLatitudeRef'])
            self.lng = self.convert_to_decimal_deg(
                self.GpsTagNames['GPSLongitude'], self.GpsTagNames['GPSLongitudeRef'])
        # distinguishing could be useful for adding custom pins when no GPS data is supplied in the image
        except ValueError as e:
            raise('Lat and Lng not set, invalid geocoordinates' + str(e))
        except TypeError as e:
            raise('No GPS metdata in the image' + str(e))

    @staticmethod
    def division(z):
        """Helper to a helper function, performs division of tuple elements"""
        x, y = z
        try:
            return float(x)/y
        except ZeroDivisionError as e:
            raise ValueError('Invalid input!') from e

    def convert_to_decimal_deg(self, coordinates, ref):
        """Helper function to convert the GPS coordinates
        stored in the EXIF to degress in decimal format"""
        try:
            deg, min, sec = tuple(map(lambda z: self.division(z), coordinates))
        except ValueError as e:
            raise ValueError('Invalid geocoordinates!') from e
        except TypeError as e:
            raise

        if ref in ['N', 'E']:
            ref = 1
        elif ref in ['S', 'W']:
            ref = -1
        if ref:
            return round((deg + min / 60 + sec / 3600) * ref, 7)

    # def find_location(self):
    #     gmaps = googlemaps.Client(
    #         key='{{key}}'
    #         )
    #     address = gmaps.latlng_to_address(self.lat, self.lng)
    #     results = gmaps.reverse_geocode(
    #         (self.lat, self.lng)#, ['administrative_area_level_1']
    #         )

    def find_empty_tags(self):
        """Returns null class instance variables """
        return [k for k, v in vars(self).items() if v is None]

    # def print_me(self):
    #     print('filepath: {}\nfilename: {}\norientation: {}\ntimestamp: {}\ncountry: {}\ncity: {}\nlat: {}\nlng: {}\nformat: {}\nsize: {}\n'.format(
    #         self.filepath,
    #         self.filename,
    #         self.orientation,
    #         self.timestamp,
    #         self.country,
    #         self.city,
    #         self.lat,
    #         self.lng,
    #         self.format,
    #         self.size
    #     ))


class ReverseGeocoding:

    def __init__(self, lat, lng):
        self.lng = lng
        self.lat = lat
        self.results = None

    def find_locations(self):
        """Returns a list of a single dictionary (single result) 
        or many dictionaries (multiple results) if lat/lng are not precise """
        try:
            gmaps = googlemaps.Client(
                key=os.environ.get('GM_API_KEY')
            )
            self.results = gmaps.reverse_geocode(
                (self.lat, self.lng)
            )
        except Exception as e:  # create a googlemaps API exception class
            raise RuntimeError("Error retrieving results: " + str(e)) from e

    def find_component(self, result, component_type):
        """ Helper method, filters single result for 
        desired component type like city, country or area level"""
        return [
            component for component in result['address_components']
            if component_type in component['types']
        ]

    def get_component(self, *args):
        """ Gmaps address component parser, 
        In case more than one result is associated with single lat/lng, 
        group all unique results together 
        i.e. if more than one town is associated with lat/lng show all"""
        components = (
            self.find_component(result, *args)[0]['long_name']
            for result in self.results
            if self.find_component(result, *args)
        )
        return set(components)

        # component_set = set()
        # if self.results:
        #     for result in self.results:
        #         try:
        #             name = next(self.find_component(result, *args))['long_name']
        #             component_set.add(name)
        #         except StopIteration:
        #             # print( f'No component found')
        #             pass
        # return component_set

    def get_city(self):
        return [city for city in self.get_component('locality')]

    def get_country(self):
        return [country for country in self.get_component('country')]

    def get_area_level1(self):
        return [region for region in self.get_component('administrative_area_level_1')]

    def get_area_level2(self):
        return [region for region in self.get_component('administrative_area_level_2')]

    def get_area_level3(self):
        return [region for region in self.get_component('administrative_area_level_3')]

    def get_postal_town(self):
        return [town for town in self.get_component('postal_town')]

    # CHANGE FROM GENERATOR TO LIST
    def get_postal_code(self):
        for postcode in self.get_component('postal_code'):
            yield postcode

    def get_address(self):
        for address in self.get_component('street_address'):
            yield address

    def get_formatted_address(self):
        try:
            addresses = [result['formatted_address']
                         for result in self.results]
        except Exception as e:
            print(str(e))
            return None
        else:
            return set(addresses)


if __name__ == '__main__':
    # imageMetadata = MetadataExtractor("C:\\Users\\lidia\\Software\\travellog\\uploads\\IMG_1060.jpg")
    for pic in os.listdir("./photos/0"):
        picture = os.path.join('./photos/0', pic)
        imageMetadata = MetadataExtractor(picture)
        imageMetadata.extract()
        print(imageMetadata.find_empty_tags())
        # deg, min, sec = tuple(map(lambda z: imageMetadata.division(z), None))
        # print(imageMetadata.convert_to_decimal_deg(None, 'N'))
        # imageMetadata.extract()
        # imageMetadata.find_location()
        # imageMetadata.print_me()

    # geo = ReverseGeocoding(36.0217944, -5.6178611)
    # geo.find_locations()
    # start_time = time()
    # print(list(geo.get_city()))
    # print(list(geo.get_adm_level1()))
    # print(time() - start_time)

    # for country in geo.get_component('country'):
    #     print(country)

    #imageMetadata = MetadataExtractor("C:\\Users\\lidia\\Pictures\\IMG_2055.jpg")

    #
