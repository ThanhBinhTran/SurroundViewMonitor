import cv2
import numpy as np
from lib_img import *
from PIL import Image

# Callback function to capture mouse click events
def get_coordinates(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button click
        print(f"Clicked at: ({x}, {y})")
        # Display the coordinates on the image
        image_temp.copyto(image)
        cv2.putText(image, f"({x}, {y})", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        # Draw a filled circle at (x, y) with radius 0
        cv2.circle(image, (x, y), radius=1, color=(0, 0, 255), thickness=-1)  # Red color
        cv2.imshow("output_Original", image)
        print(f'({x},{y})')

class WarpedImageData:
    def __init__(self, warped, srcpt, dstpt, width, height):
        self.warped = warped
        self.srcpt = srcpt
        self.dstpt = dstpt
        self.width = width
        self.height = height
 
def load_and_resize_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Failed to load image: {image_path}")
    return resize_img(image=image)
 
def get_homography_points(image, srcpt, width=200, height=250, offset_x=0):
    warped_image_width = int(image.shape[1] * 2)
    warped_image_height = int(image.shape[0])
    des_offset_x = warped_image_width // 4 + offset_x
    des_offset_y = 0
    dstpt = np.int32([
        [des_offset_x, des_offset_y + width],
        [des_offset_x, des_offset_y + width * 2],
        [des_offset_x + height, des_offset_y + width],
        [des_offset_x + height, des_offset_y + width * 2]
    ])
    return srcpt, dstpt, warped_image_width, warped_image_height
 
def create_mask(image):
    gray = image.convert('L')
    return gray.point(lambda p: 255 if p > 0 else 0).convert('L')
 
def create_transparent_image(width, height):
    return Image.new('RGBA', (width, height), (0, 0, 0, 0))
 
def convert_to_rgba(img):
    if img.mode != 'RGBA':
        return img.convert('RGBA')
    return img
 
def process_and_warp(image, srcpt, width, height, offset_x):
    srcpt, dstpt, w, h = get_homography_points(image, srcpt, width, height, offset_x)
    h_matrix, _ = cv2.findHomography(srcpt, dstpt, cv2.RANSAC)

    warped = cv2.warpPerspective(image, h_matrix, (w, h))
    return warped, dstpt
image = load_and_resize_image('img_right.jpg')
image_temp = image

def main():
    # Image paths
 
    # Source points for each view
    src_points =  np.int32([[347, 469], [103, 640], [690, 477], [972, 653]])
 
    # Load and resize images
    image = load_and_resize_image('img_right.jpg')
    image_temp = image
    # Process and warp images
    warped_img, dst_points = process_and_warp(image, src_points, 200, 250, 250)
    draw_points(image=image, points=src_points)
    draw_points(image=warped_img, points=dst_points)
 
    

    cv2.imshow(f"output_Original", image)
    cv2.setMouseCallback("output_Original", get_coordinates)

    cv2.imshow(f"output_PVM_Warped", warped_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
 
if __name__ == "__main__":
    main()