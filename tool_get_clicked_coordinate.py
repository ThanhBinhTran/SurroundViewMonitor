import cv2
from lib_img import *

# Callback function to capture mouse click events
def get_coordinates(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button click
        print(f"Clicked at: ({x}, {y})")
        # Display the coordinates on the image
        cv2.putText(image, f"({x}, {y})", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        # Draw a filled circle at (x, y) with radius 0
        cv2.circle(image, (x, y), radius=1, color=(0, 0, 255), thickness=-1)  # Red color
        cv2.imshow("Image", image)
        print(f'({x},{y})')

# Load the image
imgName = 'right'
image_path = f"img_{imgName}.jpg"  # Replace with your image path
image = cv2.imread(image_path)
image = resize_img(image=image, scale=0.4)
if image is None:
    print("Error: Could not load image. Check the file path.")
else:
    # Display the image
    cv2.imshow("Image", image)

    # Set the mouse callback function
    cv2.setMouseCallback("Image", get_coordinates)

    
    # Wait until a key is pressed
    cv2.waitKey(0)

    cv2.imwrite(f'output_Orcodinate_{imgname}.jpg', image)
    # Close all OpenCV windows
    cv2.destroyAllWindows()
