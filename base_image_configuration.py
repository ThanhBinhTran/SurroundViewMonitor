from PIL import Image, ImageDraw, ImageFont
import math
import numpy as np

class BaseImagePoints:
    def __init__(self,image_width = 2000, image_height = 2800,
                 car_width = 700, car_height = 1500,
                 calibration_width = 1800, calibration_height = 2600, calibration_cell_size = 400):
        # image info
        self.image_width = image_width
        self.image_height = image_height
        # car area
        self.car_width = car_width
        self.car_height = car_height
        self.actual_height = 720.0
        self.ratio = self.actual_height/self.image_height
        # calibration landmark
        self.calibration_width = calibration_width
        self.calibration_height = calibration_height
        self.calibration_cell_size = calibration_cell_size

        self.set_image_corners()
        self.set_car_corners()
        self.define_destination_points()

    def define_destination_points(self):
        self.calibration_left =  (self.image_width - self.calibration_width )// 2
        self.calibration_right = self.calibration_left + self.calibration_width
        self.calibration_left_in = self.calibration_left + self.calibration_cell_size
        self.calibration_right_in = self.calibration_right - self.calibration_cell_size
        self.calibration_top = (self.image_height - self.calibration_height) // 2
        self.calibration_bottom = self.calibration_top + self.calibration_height
        self.calibration_top_in = self.calibration_top + self.calibration_cell_size
        self.calibration_bottom_in = self.calibration_bottom - self.calibration_cell_size

        self.dstP0 = (self.calibration_left    , self.calibration_top)
        self.dstP1 = (self.calibration_left_in , self.calibration_top)
        self.dstP2 = (self.calibration_right_in, self.calibration_top)
        self.dstP3 = (self.calibration_right   , self.calibration_top)

        self.dstP4 = (self.calibration_left    , self.calibration_top_in)
        self.dstP5 = (self.calibration_left_in , self.calibration_top_in)
        self.dstP6 = (self.calibration_right_in, self.calibration_top_in)
        self.dstP7 = (self.calibration_right   , self.calibration_top_in)

        self.dstP8 = (self.calibration_left    , self.calibration_bottom_in)
        self.dstP9 = (self.calibration_left_in , self.calibration_bottom_in)
        self.dstPA = (self.calibration_right_in, self.calibration_bottom_in)
        self.dstPB = (self.calibration_right   , self.calibration_bottom_in)

        self.dstPC = (self.calibration_left    , self.calibration_bottom)
        self.dstPD = (self.calibration_left_in , self.calibration_bottom)
        self.dstPE = (self.calibration_right_in, self.calibration_bottom)
        self.dstPF = (self.calibration_right   , self.calibration_bottom)


    def set_image_corners(self):
        """
        Returns the four corner points of an image.
        Parameters:
        - width: int, the width of the image
        - height: int, the height of the image
        """
        self.image_top_left = (0, 0)
        self.image_top_right = (self.image_width - 1, 0)
        self.image_bottom_left = (0, self.image_height - 1)
        self.image_bottom_right = (self.image_width - 1, self.image_height - 1)

    def set_car_corners(self):
        """
        Returns the four corner points of a centered rectangle.
        Each point is in (x, y) format.
        """
        self.car_left =  (self.image_width - self.car_width )// 2
        self.car_right = self.car_left + self.car_width
        self.car_top = (self.image_height - self.car_height) // 2
        self.car_bottom = self.car_top + self.car_height

        self.car_top_left = (self.car_left, self.car_top)
        self.car_top_right = (self.car_right, self.car_top)
        self.car_bottom_left = (self.car_left, self.car_bottom)
        self.car_bottom_right = (self.car_right, self.car_bottom)

class CheckerBoard:
    def __init__(self, cols = 8, rows = 8, cell_size = 100):
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size

def draw_destination_points(draw, pts:BaseImagePoints):
    fill_rec = "brown"
    draw.rectangle([pts.dstP0, pts.dstP5], fill=fill_rec)
    draw.rectangle([pts.dstP2, pts.dstP7], fill=fill_rec)
    draw.rectangle([pts.dstP8, pts.dstPD], fill=fill_rec)
    draw.rectangle([pts.dstPA, pts.dstPF], fill=fill_rec)

def draw_checkerBoard(draw, offset_x, offset_y, cb: CheckerBoard):

    # Draw checkerboard
    for row in range(cb.rows):
        for col in range(cb.cols):
            top_left = (offset_x + col * cb.cell_size, offset_y + row * cb.cell_size)
            bottom_right = (offset_x + (col + 1) * cb.cell_size, offset_y + (row + 1) * cb.cell_size)
            if (row + col) % 2 == 0:
                fill = "black"
            else:
                fill = "green" 
            draw.rectangle([top_left, bottom_right], fill=fill)

def draw_layout(draw, pts:BaseImagePoints):
    # Draw the line in black
    draw.line([(0,pts.car_top), (pts.image_width, pts.car_top)], fill="blue", width=5) # top horizontal line 
    draw.line([(0,pts.car_bottom), (pts.image_width, pts.car_bottom)], fill="blue", width=5) # bottom horizontal line 
    draw.line([(pts.car_left,0), (pts.car_left, pts.image_height)], fill="blue", width=5) # left vertical line
    draw.line([(pts.car_right,0), (pts.car_right, pts.image_height)], fill="blue", width=5) # left vertical line
    # Draw the rectangle in blue for visibility


def draw_measure_line(draw, Pa, Pb, offset= (0, 10)):
    draw_measure(draw=draw, Pa = Pa, Pb = Pb, offset=offset)
    draw.line([Pa, Pb], fill="red", width = 7)

def draw_measure(draw, Pa, Pb, offset= (0, 10)):
    print ("draw_measure")
    print (Pa)
    print (Pb)
    x1, y1 = Pa
    x2, y2 = Pb
    distance = math.hypot(x2 - x1, y2 - y1)
    # Choose a font and size (you may need to specify the full path to the .ttf file)
    font = ImageFont.truetype('arial.ttf', size=40)
    x = abs (x2 + x1) //2 + offset[0]
    y = abs (y2 + y1) //2 + offset[1]
    print (x, y)
    # Calculate distance
    text = str(distance)
    # Add text to the image
    draw.text((x, y), text, fill='black', font=font)

def draw_point_text(draw, pt, ptName="1", offset = (0, 10)):
    x, y = pt
    font = ImageFont.truetype('arial.ttf', size=40)
    draw.text((x + offset[0], y + offset[1]), f"{ptName}({pt[0]}, {pt[1]})", fill='black', font=font)

def draw_point_text_scale(draw, pt, text, offset = (0,10)):
    x, y = pt
    font = ImageFont.truetype('arial.ttf', size=40)
    draw.text((x + offset[0], y + offset[1]), text, fill='black', font=font)

def calculate_angle_vector(x=1, y = 1):
    # Calculate angle in radians
    angle_rad = math.atan2(y, x)

    # Convert to degrees
    angle_deg = math.degrees(angle_rad)

    print(f"Angle: {angle_deg} degrees")


if __name__ == "__main__":
    # Create image
    pts = BaseImagePoints()
    cb_1 = CheckerBoard(cell_size=75)
    cb_2 = CheckerBoard(cols=4, rows= 12, cell_size=100)
    image = Image.new("RGB", (pts.image_width, pts.image_height), "white")
    draw = ImageDraw.Draw(image)
    
    draw_layout(draw=draw, pts=pts)

    # calculate offset
    offset_yf = (pts.car_top - cb_1.height) // 2
    offset_yb = pts.car_bottom + (pts.image_height - pts.car_bottom - cb_1.height)//2
    offset_xl = (pts.car_left - cb_1.width) // 2
    offset_xc = pts.car_left + (pts.car_width - cb_1.width) // 2
    offset_xr = pts.car_right + ( (pts.image_width - pts.car_right) - cb_1.width) // 2

    offset_yc = pts.car_top + (pts.car_height - cb_2.height) // 2
    offset_xcl = (pts.car_left - cb_2.width) // 2
    offset_xcr = pts.car_right + ( (pts.image_width - pts.car_right) - cb_2.width) // 2

    draw_checkerBoard(draw=draw, offset_x= offset_xc, offset_y= offset_yf , cb=cb_1)
    draw_checkerBoard(draw=draw, offset_x= offset_xc, offset_y= offset_yb , cb=cb_1)

    draw_checkerBoard(draw=draw, offset_x= offset_xcl, offset_y= offset_yc , cb=cb_2)
    draw_checkerBoard(draw=draw, offset_x= offset_xcr, offset_y= offset_yc , cb=cb_2)


    draw_destination_points(draw=draw, pts=pts)

    # Save image
    image.save(f"img_CheckerBase_{pts.image_width}_{pts.image_height}.png")
