from lib_img import *
import cv2
import numpy as np
from base_image_configuration import BaseImagePoints
from lib_SVM import *

src_points = np.array( (
# front image
    [ 85, 268],
    [445, 272],
    [473, 350],
    [ 48, 349],
# back image
    [ 92, 274],
    [451, 262],
    [477, 344],
    [ 66, 351],
# left image
    [ 49, 293],
    [482, 296],
    [507, 360],
    [ 26, 360],
# right image
    [ 50, 295],
    [482, 295],
    [508, 361],
    [ 24, 359]
), np.int32)



image_selected = 0
control_title = 'Control'
zoom_title = 'Zoom points'
image_selected_name = 'front'

points = {
    'sx0': src_points[0][0], 'sy0': src_points[0][1],
    'sx1': src_points[1][0], 'sy1': src_points[1][1],
    'sx2': src_points[2][0], 'sy2': src_points[2][1],
    'sx3': src_points[3][0], 'sy3': src_points[3][1],
}
def on_changePoints(val, trackbar_name):
    global src_points

    sec_idx = 1 if 'y' in trackbar_name else 0
    if '1' in trackbar_name:
        first_idx = 1
    elif '2' in trackbar_name:
        first_idx = 2
    elif '3' in trackbar_name:
        first_idx = 3
    else:
        first_idx = 0

    src_points[image_selected*4 + first_idx][sec_idx] = val
    centre = src_points[image_selected*4 + first_idx]
    x_start, y_start = centre[0] - 10, centre[1] - 10
    x_end, y_end = centre[0] + 10, centre[1] + 10

    roi = images[image_selected_name][y_start:y_end, x_start:x_end].copy()
    print(image_selected_name)
    scale = 20
    
    roi = imlib.resize_image_scale(roi, scale)
    cv2.circle(roi, (10*scale,10*scale), radius=2, color=(0, 0, 255), thickness=-1)
    cv2.imshow(zoom_title, roi)

def on_blur_radius(x):
    global imsvm
    imsvm.create_mask(radius=x)

def on_selectedimage(selected_button):
    global image_selected, image_selected_name
    image_selected = selected_button
    cv2.setTrackbarPos('P0x', control_title, src_points[0 + selected_button*4, 0])
    cv2.setTrackbarPos('P0y', control_title, src_points[0 + selected_button*4, 1])
    cv2.setTrackbarPos('P1x', control_title, src_points[1 + selected_button*4, 0])
    cv2.setTrackbarPos('P1y', control_title, src_points[1 + selected_button*4, 1])
    cv2.setTrackbarPos('P2x', control_title, src_points[2 + selected_button*4, 0])
    cv2.setTrackbarPos('P2y', control_title, src_points[2 + selected_button*4, 1])
    cv2.setTrackbarPos('P3x', control_title, src_points[3 + selected_button*4, 0])
    cv2.setTrackbarPos('P3y', control_title, src_points[3 + selected_button*4, 1])
    if image_selected == 0:
        image_selected_name = 'front'
    elif image_selected == 1:
        image_selected_name = 'back'
    elif image_selected == 2:
        image_selected_name = 'left'
    else:
        image_selected_name = 'right'

def create_trackbar_control(width, height):
    cv2.namedWindow(control_title)
    cv2.resizeWindow(control_title, 800, 600)
    cv2.namedWindow(zoom_title)
    cv2.createTrackbar('P0x', control_title, src_points[0][0], width , lambda x: on_changePoints(x, 'P0x'))
    cv2.createTrackbar('P0y', control_title, src_points[0][1], height, lambda x: on_changePoints(x, 'P0y'))
    cv2.createTrackbar('P1x', control_title, src_points[1][0], width , lambda x: on_changePoints(x, 'P1x'))
    cv2.createTrackbar('P1y', control_title, src_points[1][1], height, lambda x: on_changePoints(x, 'P1y'))
    cv2.createTrackbar('P2x', control_title, src_points[2][0], width , lambda x: on_changePoints(x, 'P2x'))
    cv2.createTrackbar('P2y', control_title, src_points[2][1], height, lambda x: on_changePoints(x, 'P2y'))
    cv2.createTrackbar('P3x', control_title, src_points[3][0], width , lambda x: on_changePoints(x, 'P3x'))
    cv2.createTrackbar('P3y', control_title, src_points[3][1], height, lambda x: on_changePoints(x, 'P3y'))

    cv2.createTrackbar("image select", control_title, 0 , 3, on_selectedimage)
    cv2.createTrackbar("blur radius", control_title, 10 , 100, on_blur_radius)

def deep_image_copy(key):
    images[f'copy_{key}'] = images[key].copy()

if __name__ == '__main__':
    imlib = ImageLib()
    # create SVM image metadata including:
    # image size
    # car area size
    # alignment region and its gradient masks
    imsvm = SVM_Lib()

    
    keys = {'front', 'back', 'left', 'right'}

    images = {key: imlib.load_image(f'image_{key}.jpg') for key in keys}
    height, width = images['front'].shape[:2]
    save_and_break_app = False
    if not save_and_break_app:

        create_trackbar_control(width, height)

    while True:
        # step 1 set source, destination points
        imsvm.set_source_points(src_points=src_points)

        # step 2: calculate perspective transformation base on source and destination points
        #findHomography
        imsvm.findPerspectiveTransform()

        # step 3: warping perspective image
        for key in keys:
            images[f'warp_{key}'] = imlib.warpPerspective(images[key], imsvm.perspectiveMatrix[key], (imsvm.image_width, imsvm.image_height))

        # apply mask to see temp images
        for key in keys:
            images[f'masked_{key}'] = imsvm.apply_mask(image=images[f'warp_{key}'], mask=imsvm.mask[key])

        # step 4: image stitching = alignment image and blending seam
        images['svm'] = imsvm.get_result_image(image_front=images['warp_front'], image_back=images['warp_back'],
                                           image_left=images['warp_left'], image_right=images['warp_right'])
        for key in keys:
            deep_image_copy(key)
        for key in keys:
            imlib.draw_points_lines(image=images[f'copy_{key}'], points=imsvm.srcPts[key], color=(0,0,255))

        out_image = imlib.stack_img_col_row([images['copy_front'], images['copy_back'], images['copy_left'], images['copy_right']], col=2, row=2)
        out_perspective_image = imlib.stack_img_col_row([images['warp_front'], images['warp_back'], images['warp_left'], images['warp_right']], col=2, row=2)
        out_mask_image = imlib.stack_img_col_row([images['masked_front'], images['masked_back'], images['masked_left'], images['masked_right']], col=2, row=2)

        out_perspective_image = imlib.resize_image_scale(image=out_perspective_image, scale=0.12)

        #imsvm.draw_region(image=images['svm'])


        if save_and_break_app:
            imlib.save_images(images=images, keys=['copy_front', 'copy_back', 'copy_left', 'copy_right',
                                             'warp_front', 'warp_back', 'warp_left', 'warp_right',
                                             'masked_front', 'masked_back', 'masked_left', 'masked_right',
                                             'svm'])
            break
        else:
            out_mask_image = imlib.resize_image_scale(image=out_mask_image, scale=0.12)
            images['svm'] = imlib.resize_image_scale(image=images['svm'], scale=0.51)
            imlib.imshow("Output", out_image)
            #imlib.imshow("Output_perspective_image", out_perspective_image)
            #imlib.imshow("Output_mask_image", out_mask_image)
            imlib.imshow("Output_svm_image", images['svm'])
        if cv2.waitKey(10) & 0xFF == 27:
            break
    cv2.destroyAllWindows()