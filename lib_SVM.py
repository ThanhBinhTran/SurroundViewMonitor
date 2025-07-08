from lib_img import *
from base_image_configuration import BaseImagePoints
import numpy as np
import cv2

class SVM_Lib(BaseImagePoints):
    def __init__(self, image_width=2000//2, image_height=2800//2,
                 car_width=700//2, car_height=1500//2,
                 calibration_width=1800//2, calibration_height=2600//2, calibration_cell_size=400//2,
                 margin = 400//2):
        super().__init__(image_width, image_height,
                         car_width, car_height,
                         calibration_width, calibration_height, calibration_cell_size)

        self.margin = margin
        self.set_margin()

        self.srcPts = {}
        self.dstPts = {}
        self.perspectiveMatrix = {}
        self.mask = {}

        self.create_mask()
        self.set_destination_points()

    def set_source_points(self, src_points):
        self.srcPts['front'] = np.array(src_points[0*4: 0*4 + 4 ], np.float32)
        self.srcPts['back' ] = np.array(src_points[1*4: 1*4 + 4 ], np.float32)
        self.srcPts['left' ] = np.array(src_points[2*4: 2*4 + 4 ], np.float32)
        self.srcPts['right'] = np.array(src_points[3*4: 3*4 + 4 ], np.float32)

    def set_destination_points(self):
        self.dstPts['front'] = np.array([self.dstP0, self.dstP3, self.dstP7, self.dstP4], np.float32)
        self.dstPts['back' ] = np.array([self.dstPF, self.dstPC, self.dstP8, self.dstPB], np.float32)
        self.dstPts['left' ] = np.array([self.dstPC, self.dstP0, self.dstP1, self.dstPD], np.float32)
        self.dstPts['right'] = np.array([self.dstP3, self.dstPF, self.dstPE, self.dstP2], np.float32)

    def findPerspectiveTransform(self):
        for key in ['front', 'back', 'left', 'right']:
            self.perspectiveMatrix[key] = cv2.getPerspectiveTransform(self.srcPts[key], self.dstPts[key])

    def set_margin(self):
        self.margin_top_left = (0, self.margin)
        self.margin_top_right = (self.image_width - 1, self.margin)
        self.margin_bottom_left = (0, self.image_height - self.margin - 1)
        self.margin_bottom_right = (self.image_width - 1, self.image_height - self.margin - 1)

    def create_mask(self, radius=20):
        # Define polygons for each area
        polygons = {
                'front': np.array([self.car_top_left, self.margin_top_left, self.image_top_left,
                          self.image_top_right, self.margin_top_right, self.car_top_right], np.int32),
                'back': np.array([self.car_bottom_left, self.car_bottom_right, self.margin_bottom_right,
                         self.image_bottom_right, self.image_bottom_left, self.margin_bottom_left], np.int32),
                'left': np.array([self.car_top_left, self.car_bottom_left, self.margin_bottom_left, self.margin_top_left], np.int32),
                'right': np.array([self.car_top_right, self.margin_top_right, self.margin_bottom_right, self.car_bottom_right], np.int32),
        }

        # Create and fill masks
        for key in ['front', 'back', 'left', 'right']:
            mask = np.zeros((self.image_height, self.image_width), dtype=np.float)

            # Fill the polygon on the mask
            cv2.fillPoly(mask, [polygons[key]], 1.0)

            # Step 3: Apply Gaussian Blur to the mask
            #if key in ['left', 'right']:
            kernel_size = (2*radius + 1, 2*radius + 1)
            mask = cv2.GaussianBlur(mask, kernel_size, sigmaX=0)
            # Step 4: Expand alpha to 3 channels
            mask_3ch = cv2.merge([mask, mask, mask])
            self.mask[key] = mask_3ch

    def apply_mask(self, image, mask):
        return (image*mask).astype(np.uint8)

    def get_result_image(self, image_front, image_back, image_left, image_right):
        blended = cv2.bitwise_or(image_front,image_back)
        blended = (image_left * self.mask['left'] + blended * (1 - self.mask['left']))
        blended = (image_right * self.mask['right'] + blended * (1 - self.mask['right'])).astype(np.uint8)

        return blended
    
    def draw_region(self, image, linecolor = (0,0,255), thickness=2):
        cv2.line(img=image,pt1=self.car_top_left, pt2=self.car_top_right,color=linecolor,thickness=thickness)
        cv2.line(img=image,pt1=self.car_bottom_left, pt2=self.car_bottom_right,color=linecolor,thickness=thickness)
        cv2.line(img=image,pt1=self.car_top_left, pt2=self.car_bottom_left,color=linecolor,thickness=thickness)
        cv2.line(img=image,pt1=self.car_top_right, pt2=self.car_bottom_right,color=linecolor,thickness=thickness)

        cv2.line(img=image,pt1=self.car_top_left, pt2=self.margin_top_left,color=linecolor,thickness=thickness)
        cv2.line(img=image,pt1=self.car_top_right, pt2=self.margin_top_right,color=linecolor,thickness=thickness)
        cv2.line(img=image,pt1=self.car_bottom_left, pt2=self.margin_bottom_left,color=linecolor,thickness=thickness)
        cv2.line(img=image,pt1=self.car_bottom_right, pt2=self.margin_bottom_right,color=linecolor,thickness=thickness)
if __name__ == '__main__':
    svm = SVM_Lib()
    imlib= ImageLib()
    # Create solid color images (BGR format)
    red_img    = np.full((svm.image_height, svm.image_width, 3), (0, 0, 255), dtype=np.uint8)   # Red
    yellow_img = np.full((svm.image_height, svm.image_width, 3), (0, 255, 255), dtype=np.uint8) # Yellow
    blue_img   = np.full((svm.image_height, svm.image_width, 3), (255, 0, 0), dtype=np.uint8)   # Blue
    green_img  = np.full((svm.image_height, svm.image_width, 3), (0, 255, 0), dtype=np.uint8)   # Green

    blended = svm.get_result_image(image_front=red_img, image_back=yellow_img, image_left=green_img, image_right=blue_img)

    # Display the images
    imlib.save_image(image=blended, name='svm_lib_test')

    cv2.waitKey(0)
    cv2.destroyAllWindows()