import cv2
import numpy as np
from lib_img import *
from PIL import Image


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
 
def process_and_warp(image, srcpt, width, height, offset_x, rotate_code=None):
    srcpt, dstpt, w, h = get_homography_points(image, srcpt, width, height, offset_x)
    h_matrix, _ = cv2.findHomography(srcpt, dstpt, cv2.RANSAC)

    warped = cv2.warpPerspective(image, h_matrix, (w, h))
    cv2.imwrite('output_warped.jpg', warped)
    if rotate_code is not None:
        warped = cv2.rotate(warped, rotate_code)
    return WarpedImageData(warped, srcpt, dstpt, w, h)
 
def main():
    # Image paths
    paths = {
        'right': 'img_right.jpg',
        'left': 'img_left.jpg',
        'front': 'img_front.jpg',
        'back': 'img_back.jpg'
    }
 
    # Source points for each view
    src_points = {
        'right': np.int32([[347, 469], [103, 640], [690, 477], [972, 653]]),
        'left':  np.int32([[142, 240], [0,  336], [319, 234], [415, 321]]),
        'front': np.int32([[170, 233], [10, 350], [344, 240], [500, 350]]),
        'back':  np.int32([[170, 233], [10, 350], [344, 240], [500, 350]])
    }
 
    # Load and resize images
    images = {k: load_and_resize_image(v) for k, v in paths.items()}
 
    # Process and warp images
    warped = {}

    warped['left'] = process_and_warp(images['left'], src_points['left'], 200, 250, 0, cv2.ROTATE_90_COUNTERCLOCKWISE)
    warped['front'] = process_and_warp(images['front'], src_points['front'], 200, 250, 0, None)
    warped['back'] = process_and_warp(images['back'], src_points['back'], 200, 250, 0, cv2.ROTATE_180)
    warped['right'] = process_and_warp(images['right'], src_points['right'], 200, 250, 250, cv2.ROTATE_90_CLOCKWISE)
 
    # Draw points on original images
    for k in images:
        draw_points(image=images[k], points=warped[k].srcpt)
 
    # Visualization (stacked images)
    image = stack_img_2_2([images['right'], images['left'], images['front'], images['back']])
    #image_warped = stack_img_2_2([warped['right'], warped['left'], warped['front'], warped['back']])
 
    # Create transparent canvas
    canvas_size = warped['back'].width  # Use back image width for square canvas
    image_pvm = create_transparent_image(canvas_size, canvas_size)
    pvm_width, pvm_height = image_pvm.size
 
    # Convert warped images to PIL RGBA
    warped_pil = {k: convert_to_rgba(Image.fromarray(warped[k].warped)) for k in warped}
 
    # Create masks
    masks = {k: create_mask(warped_pil[k]) for k in warped_pil}
 
    # Paste images onto canvas with masks
    image_pvm.paste(warped_pil['back'], (-90, int(pvm_height/2 + 300)), mask=masks['back'])
    image_pvm.paste(warped_pil['right'], (int(pvm_width/2 + 180), -80), mask=masks['right'])
    image_pvm.paste(warped_pil['front'], (80, 100), mask=masks['front'])
    image_pvm.paste(warped_pil['left'], (0, 0), mask=masks['left'])
 
    # Convert final image to NumPy array for OpenCV display/save
    image_pvm_warped = np.array(image_pvm)
 
    save_image = False
    if save_image:
        cv2.imwrite('output_Original.jpg', image)
        cv2.imwrite('output_PVM_Warped.jpg', image_pvm_warped)
        #cv2.imwrite('output_Warped.jpg', image_warped)
    else:
        cv2.imshow(f"output_Original{image.shape}", image)
        cv2.imshow(f"output_PVM_Warped{image_pvm_warped.shape}", image_pvm_warped)
        #cv2.imshow(f"output_Warped{image_warped.shape}", image_warped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
 
if __name__ == "__main__":
    main()