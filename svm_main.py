from lib_img import *
import cv2
import numpy as np
from base_image_configuration import BaseImagePoints
from lib_SVM import *

src_points = np.array( (
# front image
    [ 79, 273],
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
points = {
    'sx0': src_points[0][0], 'sy0': src_points[0][1],
    'sx1': src_points[1][0], 'sy1': src_points[1][1],
    'sx2': src_points[2][0], 'sy2': src_points[2][1],
    'sx3': src_points[3][0], 'sy3': src_points[3][1],
}
def on_blur_radius(x):
    global imsvm
    imsvm.create_mask(radius=x)

def on_selectedimage(selected_button):
    global image_selected
    image_selected = selected_button 
    cv2.setTrackbarPos('sx0', 'Control', src_points[0 + selected_button*4, 0])  # Set position to 75
    cv2.setTrackbarPos('sy0', 'Control', src_points[0 + selected_button*4, 1])  # Set position to 75
    cv2.setTrackbarPos('sx1', 'Control', src_points[1 + selected_button*4, 0])  # Set position to 75
    cv2.setTrackbarPos('sy1', 'Control', src_points[1 + selected_button*4, 1])  # Set position to 75
    cv2.setTrackbarPos('sx2', 'Control', src_points[2 + selected_button*4, 0])  # Set position to 75
    cv2.setTrackbarPos('sy2', 'Control', src_points[2 + selected_button*4, 1])  # Set position to 75
    cv2.setTrackbarPos('sx3', 'Control', src_points[3 + selected_button*4, 0])  # Set position to 75
    cv2.setTrackbarPos('sy3', 'Control', src_points[3 + selected_button*4, 1])  # Set position to 75

def deep_image_copy(key):
    images[f'copy_{key}'] = images[key].copy()



if __name__ == '__main__':
    imlib = ImageLib()
    imsvm = SVM_Lib()

    keys = {'front', 'back', 'left', 'right'}

    images = {key: imlib.load_image(f'image_{key}.jpg') for key in keys}
    height, width = images['left'].shape[:2]

    cv2.namedWindow('Control')
    cv2.resizeWindow('Control', 400, 600)

    for pt in points:
        if 'x' in pt:
            cv2.createTrackbar(pt, 'Control', points[pt], width, lambda x: None)
        else:
            cv2.createTrackbar(pt, 'Control', points[pt], height, lambda x: None)

    cv2.createTrackbar("image select", 'Control', 0 , 3, on_selectedimage)
    cv2.createTrackbar("blur radius", 'Control', 10 , 100, on_blur_radius)
    while True:
        points['sx0'] = cv2.getTrackbarPos('sx0', 'Control')
        points['sy0'] = cv2.getTrackbarPos('sy0', 'Control')
        points['sx1'] = cv2.getTrackbarPos('sx1', 'Control')
        points['sy1'] = cv2.getTrackbarPos('sy1', 'Control')
        points['sx2'] = cv2.getTrackbarPos('sx2', 'Control')
        points['sy2'] = cv2.getTrackbarPos('sy2', 'Control')
        points['sx3'] = cv2.getTrackbarPos('sx3', 'Control')
        points['sy3'] = cv2.getTrackbarPos('sy3', 'Control')
        blur_radius = cv2.getTrackbarPos('blur radius', 'Control')

        src_points[image_selected*4 + 0] = [points['sx0'], points['sy0']]
        src_points[image_selected*4 + 1] = [points['sx1'], points['sy1']]
        src_points[image_selected*4 + 2] = [points['sx2'], points['sy2']]
        src_points[image_selected*4 + 3] = [points['sx3'], points['sy3']]

        imsvm.set_source_points(src_points=src_points)
        #findHomography
        imsvm.findPerspectiveTransform()

        # warping image
        for key in keys:
            images[f'warp_{key}'] = imlib.warpPerspective(images[key], imsvm.perspectiveMatrix[key], (imsvm.image_width, imsvm.image_height))

        # apply mask
        for key in keys:
            images[f'masked_{key}'] = imsvm.apply_mask(image=images[f'warp_{key}'], mask=imsvm.mask[key])

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

        save_and_break_app = False
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
            imlib.imshow("Output_perspective_image", out_perspective_image)
            imlib.imshow("Output_mask_image", out_mask_image)
            imlib.imshow("Output_svm_image", images['svm'])
        if cv2.waitKey(10) & 0xFF == 27:
            break
    cv2.destroyAllWindows()