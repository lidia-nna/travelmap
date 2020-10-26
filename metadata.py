import googlemaps, os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

class MetadataExtractor:

    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.orientation = None
        self.timestamp = None
        self.country = None
        self.city = None
        self.lat = None
        self.lng = None
        self.format = None
        self.size = None
        self.lat_ref = None
        self.lng_ref = None
        self.geo_data = {
            'timestamp': self.timestamp,
            'country': self.country,
            'city': self.city,
            'lat': self.lat,
            'lng': self.lng
        }
        self.GpsTagNames = {
            'GPSLatitudeRef': self.lat_ref,
            'GPSLongitudeRef': self.lng_ref,
            'GPSLatitude': self.lat,
            'GPSLongitude': self.lng
        }        
    def lookupGpsTag(self, gpsInfo):
        for gk in gpsInfo.keys():
            if GPSTAGS[gk] in self.GpsTagNames.keys():
                self.GpsTagNames[GPSTAGS[gk]] = gpsInfo[gk]


    def extract(self):
        img = Image.open(self.filepath)
        self.filename, ext = os.path.splitext(self.filename)
        self.format = img.format
        self.size = img.size
        
        try:
            exif = img._getexif()
            for k in exif.keys():
                if k in TAGS:
                    if TAGS[k] == "DateTimeOriginal":
                        timestamp = exif[k]
                        self.timestamp = timestamp[:10].replace(':', '-') + timestamp[10:]
                        print(self.timestamp)
                        # for thumbnail generation
                    elif TAGS[k] == "Orientation":
                        self.orientation = exif[k]
                    elif TAGS[k] == "GPSInfo":
                        self.lookupGpsTag(exif[k])
                        print(self.GpsTagNames)
                        #     exit(0)
                        #     print('found GPS info')
                        #     for gk in exif[k].keys():
                        #         if GPSTAGS[gk] == 'GPSLatitudeRef':
                        #             self.lat_ref = exif[k][gk]
                        #             print(f'found GPS info: GPSLatitudeRef:{self.lat_ref}')
                        #         if GPSTAGS[gk] == 'GPSLongitudeRef':
                        #             self.lng_ref = exif[k][gk]
                        #         if GPSTAGS[gk] == 'GPSLatitude':
                        #             self.lat = exif[k][gk]
                        #             print(f'found GPS info: GPSLatitude{self.lat}')
                        #         if GPSTAGS[gk] == 'GPSLongitude':
                        #             self.lng = exif[k][gk]
                        #             print(f'found GPS info: GPSLongitude:{self.lng}')
                        # #bodytext = '({:04x})   [{}]'.format(gk, exif[k][gk])
        except AttributeError as e:
            return "Unknown type: e"
        try:
            self.lat = self.convert_to_decimal_deg(self.lat, self.lat_ref)
            self.lng = self.convert_to_decimal_deg(self.lng, self.lng_ref)
            self.city, self.country = self.find_location()
        except Exception:
            pass

    @staticmethod
    def division(z):
        x,y = z
        return x/y

    def convert_to_decimal_deg(self, coordinates=None, ref=None):
        deg, min, sec = tuple(map(lambda x: self.division(x), coordinates))
        if ref in ['N', 'E']:
            ref = 1
        elif ref in ['S', 'W']:
            ref = -1
        if ref:
            print(round((deg + min / 60 + sec / 3600) * ref, 7))
            return round((deg + min / 60 + sec / 3600) * ref, 7)

    def find_location(self):
        gmaps = googlemaps.Client(
            key='AIzaSyBZTMjDgOFNnaYJREz7vAauJ6rUN2od6Ow'
            )
        results = gmaps.reverse_geocode(
            (self.lat, self.lng), ['administrative_area_level_1']
            )
        print(f'fin_location:{results}')
        #return results
        return [
            result.strip() 
            for result in results[0]['formatted_address'].split(',')
            ]

    def find_empty_tags(self):
        return [k for k, v in self.geo_data.items() if v is None]


    def print_me(self):
        print('filepath: {}\nfilename: {}\norientation: {}\ntimestamp: {}\ncountry: {}\ncity: {}\nlat: {}\nlng: {}\nformat: {}\nsize: {}\nlat_ref: {}\nlng_ref: {}\n'.format(
            self.filepath,
            self.filename,
            self.orientation,
            self.timestamp,
            self.country,
            self.city,
            self.lat,
            self.lng,
            self.format,
            self.size,
            self.lat_ref,
            self.lng_ref
        ))



if __name__ == '__main__':
    #imageMetadata = MetadataExtractor("C:\\Users\\lidia\\Software\\travellog\\uploads\\IMG_1060.jpg")
    for pic in os.listdir("./photos"):
        picture = os.path.join('./photos', pic)
        imageMetadata = MetadataExtractor(picture)
        imageMetadata.extract()
        imageMetadata.print_me()
        

    
    #imageMetadata = MetadataExtractor("C:\\Users\\lidia\\Pictures\\IMG_2055.jpg")
    
    # 