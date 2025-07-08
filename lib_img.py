import cv2
import numpy as np

class ImageLib:
   def load_image(self, image_path):
      """Load an image from the specified path."""
      image = cv2.imread(image_path)
      if image is None:
         raise FileNotFoundError(f"Failed to load image: {image_path}")
      return image

   def resize_image_scale(self, image, scale=1):
      # Calculate new dimensions
      width = int(image.shape[1] * scale)
      height = int(image.shape[0] * scale)
      # Resize the image
      return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

   def resize_image_w_h(self, image, width, height):
      # Resize the image
      return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

   def load_and_resize_image(self, image_path, scale=1):
      image = self.load_image(image_path)
      return self.resize_image_scale(image=image, scale=scale)

   def draw_points_lines(self, image, points, color = (0,0,255), linecolor=(0,255,0)):
      self.draw_points(image=image,points=points,color=color)
      ipts = np.int32(points)
      for i in range (len(ipts)-1):
         cv2.line(img=image,pt1=ipts[i], pt2=ipts[i+1],color=linecolor,thickness=2)
      cv2.line(img=image,pt1=ipts[0], pt2=ipts[-1],color=linecolor,thickness=2)

   def draw_points(self, image, points, color = (0,0,255), radius = 3, thickness = -1):
      idx = 0
      ipt = np.int32(points)
      for pt in ipt:
         cv2.putText(image, f"P{idx}{pt}", pt, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
         self.draw_point(image=image, center_coordinates=pt,radius=radius, color=color, thickness=thickness)
         idx += 1

   def draw_point(self, image, center_coordinates= (200, 200), color=(0, 0, 255), radius = 3, thickness = -1):
      x,y = int(center_coordinates[0]), int(center_coordinates[1])
      # Draw the point
      cv2.circle(image, (x,y), radius, color, thickness)

   # stack image as columns and rows
   def stack_img_col_row(self, imgs, col=2, row=2):
      if len(imgs) != col * row:
         raise ValueError(f"Expected {col * row} images, got {len(imgs)}")
      if col < 1 or row < 1:
         raise ValueError("Number of columns and rows must be at least 1")
      if len(imgs) == 1:
         return imgs[0]
      else:
         # Stack images horizontally
         rows = []
         for i in range(row):
            start_idx = i * col
            end_idx = start_idx + col
            rows.append(cv2.hconcat(imgs[start_idx:end_idx]))
         # Stack rows vertically
         return cv2.vconcat(rows)
   def text_img(self, image, text, position , font_scale = 1 , thickness =1):
      font = cv2.FONT_HERSHEY_SIMPLEX
      color = (0, 0, 255)  # red in BGR
      # Write text on image
      cv2.putText(image, text, position, font, font_scale, color, thickness, lineType=cv2.LINE_AA)

   def imshow(self, title="output", image=None):
      cv2.imshow(title, image)

   def imshowROI(self, image, title, centre, scale=5, offset= 10):
    x_start, y_start = centre[0] - offset, centre[1] - offset
    x_end, y_end = centre + offset, centre + offset

    roi = image[y_start:y_end, x_start:x_end]
    cv2.circle(roi, centre, radius=1, color=(0, 0, 255), thickness=-1)
    self.resize_image_scale(roi, scale)
    cv2.imshow(title, roi)
   
   def warpPerspective(self, image, homographyMatric, warpImgSize):
      return cv2.warpPerspective(image, homographyMatric, warpImgSize)
   
   def save_images(self, images, keys):
      for key in keys:
         print(f'saving ... image_out_{key}.jpg')
         cv2.imwrite(f'output/image_out_{key}.jpg', images[key])
   
   def save_image(self, image, name):
         print(f'saving ... output/image_out_{name}.jpg')
         cv2.imwrite(f'output/image_out_{name}.jpg', image)

   def convert_to_rgba(self, img):
      if img.mode != 'RGBA':
         return img.convert('RGBA')
      return img