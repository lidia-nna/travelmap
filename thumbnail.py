from PIL import Image, ExifTags
import os

class SquaredThumbnail:
    def __init__(self, filepath, new_side, orientation):
        self.filename, self.ext = os.path.splitext(filepath)
        self.imOrg = Image.open(filepath)
        self.new_side = float(new_side)
        self.thumbnail = None
        self.orientation = orientation
        
    def rotate(self):
        try:
             self.orientation = int(self.orientation)
        except ValueError:
            print('Orientation is a non-numerical string')
        except TypeError:
            print('Orientation is null')
        else:
            if self.orientation == 3:
                self.imOrg = self.imOrg.rotate(180, expand=True)
            elif self.orientation == 6:
                self.imOrg = self.imOrg.rotate(270, expand=True)
            elif self.orientation == 8:
                self.imOrg = self.imOrg.rotate(90, expand=True)


    def gen_thumbnail(self):
        """ get shorter side and set the scale factor for the thumbnail, you want thumbnail to be a fixed size"""
        width, height = self.imOrg.size
        # get scale factor; height is by default shorter than width hence using height
        scale = height/self.new_side
        # in case the above is not met
        if width < height:
            print("Width smaller than height!!!!")
            scale = width/self.new_side
        print(f'Img size before rotation:{width}, {height}')
        #rotate image if needed
        self.rotate()
        print('Img size after rotation:')
        # possible change to width annd height after rotation
        rotated_width, rotated_heigth = self.imOrg.size
        # set new dim
        w = rotated_width/scale
        h = rotated_heigth/scale
        print(w, h)
        # gen thumbnail
        self.imOrg.thumbnail((w,h))
        #print(f'Thumbnail size: {self.imOrg.size}')
        self.thumbnail = self.filename + '_thumbnail' + self.ext
        self.imOrg.save(self.thumbnail)
        return "Thumbnail generated"

    def crop_thumbnail(self):
        im = Image.open(self.thumbnail)
        # Get dimensions
        width, height = im.size 
        print('Thumbnail width and height:')
        print(width, height)  
        
        left = (width - self.new_side)/2
        top = (height - self.new_side)/2
        right = (width + self.new_side)/2
        bottom = (height + self.new_side)/2

        # Crop the center of the image
        im = im.crop((left, top, right, bottom))
        im.save(self.thumbnail)
        #print(f'Cropped size: {im.size}')
        return 0


# gen_thumbnail('./uploads/IMG_2838.jpg', (400,500))
# crop_img('./uploads/IMG_2838_thumbnail.jpeg', (400,400))

if __name__ == "__main__":
    squaredthumb=SquaredThumbnail('./uploads/IMG_2856.jpg', 400, 6)
    squaredthumb.gen_thumbnail()
    squaredthumb.crop_thumbnail()
    print(squaredthumb.thumbnail)