import cv2
from PIL import Image, ImageDraw
 
def resize_img(image, scale=0.4):
   # Calculate new dimensions
   print(f"Original image shape: {image.shape}")
   width = int(image.shape[1] * scale)
   height = int(image.shape[0] * scale)
   # Resize the image
   return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
 
def draw_points(image, points, color = (0,255,0)):
   idx = 0
   for pt in points:
       x,y = int(pt[0]), int(pt[1])
       cv2.putText(image, f"P{idx} ({x},{y})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
       draw_point(image=image, center_coordinates=(x,y),color=color)
       idx += 1

def draw_point(image, center_coordinates= (200, 200), color=(0, 0, 255)):
   radius = 3
   thickness = -1  # Filled circle
   # Draw the point
   cv2.circle(image, center_coordinates, radius, color, thickness)

# stack image
def stack_img_2_2(imgs):
   # Stack images horizontally
   row1 = cv2.hconcat([imgs[0], imgs[1]])  # First row with image1 and image2
   row2 = cv2.hconcat([imgs[2], imgs[3]])  # Second row with image3 and image4
   # Stack rows vertically
   return  cv2.vconcat([row1, row2])  # Final stacked image
 
def stack_img_1_2(imgs):
   # Stack images horizontally
   return cv2.hconcat([imgs[0], imgs[1]])  # First row with image1 and image2
 
def text_img(image, text, position ):
   font = cv2.FONT_HERSHEY_SIMPLEX
   font_scale = 0.5
   color = (255, 0, 0)  # Blue in BGR
   thickness = 1
   # Write text on image
   cv2.putText(image, text, position, font, font_scale, color, thickness, lineType=cv2.LINE_AA)
 

def paste_image_to_area(base_img_path, paste_img_path_l, paste_img_path_r,
                        paste_img_path_b,paste_img_path_f, output_path, rect_ratio=0.1):
   # Open base and paste images
   base_img = Image.open(base_img_path).convert('RGB')
   paste_img_l = Image.open(paste_img_path_l).convert('RGB')
   paste_img_r = Image.open(paste_img_path_r).convert('RGB')
   paste_img_b = Image.open(paste_img_path_b).convert('RGB')
   paste_img_f = Image.open(paste_img_path_f).convert('RGB')
 
   img_width, img_height = base_img.size
 
   # Rectangle size (10% of image size)
   rect_w = int(img_width * rect_ratio)
   rect_h = int(img_height * rect_ratio)
 
   # Rectangle coordinates (centered)
   left = (img_width - rect_w) // 2
   top = (img_height - rect_h) // 2
   right = left + rect_w
   bottom = top + rect_h
   
   # Source quad is the corners of the paste image
   src_quad = [
            (0, 0),
            (paste_img_f.width-1, 0),
            (paste_img_f.width-1, paste_img_f.height-1),
            (0, paste_img_f.height-1)
         ]
 
      # Define the four points: rect top-left, rect top-right, img top-right, img top-left
   dst_quad_f = [
            (left, top),         # rect_points(top-left)
(right, top),        # rect_points(top-right)
            (img_width-1, 0),    # img_points(top-right)
            (0, 0)               # img_points(top-left)
         ]
         # Define the four points: rect bottom-left, rect bottom-right, img bottom-right, img bottom-left
   dst_quad_b = [
            (left, bottom),  # rect_points(bottom-left)
            (right, bottom), # rect_points(bottom-right)
            (img_width-1, img_height-1),   # img_points(bottom-right)
            (0, img_height-1)              # img_points(bottom-left)
         ]
         # Define the four points: rect top-left, img bottom-left, img top-right, img bottom-left
   dst_quad_l = [
            (left, top),         # rect_points(top-left)
            (left, bottom),  # rect_points(bottom-left)
            (0, img_height-1),   # img_points(bottom-left)
            (0, 0)               # img_points(top-left)
         ]
         # Define the four points: rect top-right, img bottom-right, img top-left, img bottom-right
   dst_quad_r = [
            (right, top),        # rect_points(top-right)
            (right, bottom), # rect_points(bottom-right)
            (img_width-1, img_height-1),   # img_points(bottom-right)
            (img_width-1, 0)    # img_points(top-right)
         ]
   
   # Transform the paste image to fit the destination quad
   paste_img_transformed_l = paste_img_l.transform(
        base_img.size,
        Image.QUAD,
        data=sum(src_quad, ()),
        resample=Image.BICUBIC
   )
   paste_img_transformed_l.save('paste_img_transformed_l.jpg')
   # Transform the paste image to fit the destination quad
   paste_img_transformed_r = paste_img_r.transform(
        base_img.size,
        Image.QUAD,
        data=sum(src_quad, ()),
        resample=Image.BICUBIC
   )
   paste_img_transformed_r.save('paste_img_transformed_r.jpg')
   # Transform the paste image to fit the destination quad
   paste_img_transformed_b = paste_img_b.transform(
        base_img.size,
        Image.QUAD,
        data=sum(src_quad, ()),
        resample=Image.BICUBIC
   )
   paste_img_transformed_b.save('paste_img_transformed_b.jpg')
   # Transform the paste image to fit the destination quad
   paste_img_transformed_f = paste_img_f.transform(
        base_img.size,
        Image.QUAD,
        data=sum(src_quad, ()),
        resample=Image.BICUBIC
   )
   paste_img_transformed_f.save('paste_img_transformed_f.jpg')
   # Create a mask for the transformed area
   mask_l = Image.new('L', (img_width, img_height), 0)
   draw = ImageDraw.Draw(mask_l)
   draw.polygon(dst_quad_l, fill=255)
 
   # Create a mask for the transformed area
   mask_r = Image.new('L', (img_width, img_height), 0)
   draw = ImageDraw.Draw(mask_r)
   draw.polygon(dst_quad_r, fill=255)
   
   # Create a mask for the transformed area
   mask_b = Image.new('L', (img_width, img_height), 0)
   draw = ImageDraw.Draw(mask_b)
   draw.polygon(dst_quad_b, fill=255)
 
   # Create a mask for the transformed area
   mask_f = Image.new('L', (img_width, img_height), 0)
   draw = ImageDraw.Draw(mask_f)
   draw.polygon(dst_quad_f, fill=255)
   # Composite the transformed image onto the base image
   base_img.paste(paste_img_transformed_f, (0, 0), mask_f)
   base_img.paste(paste_img_transformed_l, (0, 0), mask_l)
   base_img.paste(paste_img_transformed_r, (0, 0), mask_r)
   base_img.paste(paste_img_transformed_b, (0, 0), mask_b)
 
   base_img.save(output_path)