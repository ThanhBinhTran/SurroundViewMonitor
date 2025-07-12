import cv2
import numpy as np

class AutoBrightnessContrast:
  """Auto brightness and contrast adjustment algorithms"""

  @staticmethod
  def analyze_image(image):
    """Analyze image statistics for auto adjustment"""
    if len(image.shape) == 3:
      gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
      gray = image

    mean = np.mean(gray)
    std = np.std(gray)
    min_val = np.min(gray)
    max_val = np.max(gray)

    return {
      'mean': mean,
      'std': std,
      'min': min_val,
      'max': max_val,
      'range': max_val - min_val
    } # type: ignore

  @staticmethod
  def auto_adjust_statistical(image, target_mean=127, target_std=64):
    """Statistical approach: adjust to target mean and standard deviation"""
    stats = AutoBrightnessContrast.analyze_image(image)

    if stats['std'] > 0:
      alpha = target_std / stats['std']
      alpha = np.clip(alpha, 0.5, 3.0) # Limit contrast adjustment
    else:
      alpha = 1.0

    beta = target_mean - (alpha * stats['mean'])
    beta = np.clip(beta, -100, 100) # Limit brightness adjustment

    return alpha, beta

  @staticmethod
  def auto_adjust_histogram(image):
    """Histogram stretching approach"""
    stats = AutoBrightnessContrast.analyze_image(image)

    if stats['range'] > 0:
      alpha = 255.0 / stats['range']
      alpha = np.clip(alpha, 0.5, 4.0)
      beta = -alpha * stats['min']
      beta = np.clip(beta, -100, 100)
    else:
      alpha = 1.0
      beta = 0.0

    return alpha, beta

  @staticmethod
  def auto_adjust_adaptive(image):
    """Adaptive approach combining multiple methods"""
    stats = AutoBrightnessContrast.analyze_image(image)

   # Statistical adjustment
    stat_alpha, stat_beta = AutoBrightnessContrast.auto_adjust_statistical(image)

   # Histogram adjustment
    hist_alpha, hist_beta = AutoBrightnessContrast.auto_adjust_histogram(image)

   # Weighted combination based on image characteristics
    if stats['std'] < 30: # Low contrast image
      alpha = 0.3 * stat_alpha + 0.7 * hist_alpha
      beta = 0.3 * stat_beta + 0.7 * hist_beta
    else: # Normal contrast image
      alpha = 0.7 * stat_alpha + 0.3 * hist_alpha
      beta = 0.7 * stat_beta + 0.3 * hist_beta

    return alpha, beta

  @staticmethod
  def auto_adjust_exposure(image):
    """Exposure-based adjustment"""
    stats = AutoBrightnessContrast.analyze_image(image)

   # Target exposure level (middle gray)
    target_exposure = 127
    exposure_diff = target_exposure - stats['mean']

   # Calculate gamma correction
    if stats['mean'] > 0:
      gamma = np.log(target_exposure / 255.0) / np.log(stats['mean'] / 255.0)
      gamma = np.clip(gamma, 0.5, 2.0)
    else:
      gamma = 1.0

   # Convert gamma to alpha/beta approximation
    alpha = 1.0 + (gamma - 1.0) * 0.5
    beta = exposure_diff * 0.5

    alpha = np.clip(alpha, 0.5, 3.0)
    beta = np.clip(beta, -100, 100)

    return alpha, beta

def on_trackbar(val):
  """Callback for trackbar changes"""
  pass

def create_trackbar(window_name, trackbar_name, initial_value, max_value):
  """Create a trackbar for adjusting parameters"""
  cv2.createTrackbar(trackbar_name, window_name, initial_value, max_value, on_trackbar)
  return initial_value

def apply_clahe(image, clip_limit=3.0, tile_grid_size=(8, 8)):
  """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)"""
  if len(image.shape) == 3:
   # Convert to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)

   # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    l_channel = clahe.apply(l_channel)
    a
   # Merge channels and convert back to BGR
    enhanced = cv2.merge([l_channel, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
  else:
   # Grayscale image
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    enhanced = clahe.apply(image)

  return enhanced

def main():
 # Load an image
  img = cv2.imread('output\image_out_svm.jpg') # Update with your own image path
  if img is None:
    print("Error: Unable to load image. Creating synthetic image for demo.")
   # Create a synthetic image for demo
    img = np.zeros((400, 600, 3), dtype=np.uint8)
   # Add some patterns
    cv2.rectangle(img, (50, 50), (200, 200), (100, 100, 100), -1)
    cv2.rectangle(img, (250, 50), (400, 200), (150, 150, 150), -1)
    cv2.rectangle(img, (450, 50), (550, 200), (200, 200, 200), -1)
    cv2.rectangle(img, (50, 250), (200, 350), (80, 80, 80), -1)
    cv2.rectangle(img, (250, 250), (400, 350), (120, 120, 120), -1)
    cv2.rectangle(img, (450, 250), (550, 350), (180, 180, 180), -1)
 
 # Get original image dimensions
  original_height, original_width = img.shape[:2]
  print(f"Original image size: {original_width}x{original_height}")
 
 # Create windows - keep original size
  window_name = 'Manual Adjustment'
  auto_window = 'Auto Adjustment Comparison'
  cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
  cv2.namedWindow(auto_window, cv2.WINDOW_NORMAL)
 
 # Resize windows to fit original image size
  cv2.resizeWindow(window_name, original_width, original_height + 100) # Extra space for trackbars
 
 # Create trackbars for manual adjustment
  brightness = create_trackbar(window_name, 'Brightness', 50, 100)
  contrast = create_trackbar(window_name, 'Contrast', 100, 200)
 
 # Create trackbars for auto adjustment selection
  cv2.createTrackbar('Auto Mode', window_name, 0, 5, on_trackbar)
 # 0: Manual, 1: Statistical, 2: Histogram, 3: Adaptive, 4: Exposure, 5: CLAHE
 
 # Initialize auto adjustment
  auto_bc = AutoBrightnessContrast()
 
 # Create comparison display - keep original image size
  def create_comparison_display(original, results, labels):
    """Create a comparison display of different adjustment methods keeping original size"""
    h, w = original.shape[:2]
   
   # Calculate grid layout based on original image size
   # Use 2 rows, 3 columns
    grid_img = np.zeros((h * 2, w * 3, 3), dtype=np.uint8)
   
    for i, (result, label) in enumerate(zip(results, labels)):
      row = i // 3
      col = i % 3
     
     # Keep original image size - no resizing
      y_start = row * h
      y_end = y_start + h
      x_start = col * w
      x_end = x_start + w
     
      grid_img[y_start:y_end, x_start:x_end] = result
     
     # Add label with better positioning for original size
      label_scale = max(0.4, min(1.2, w / 500.0)) # Scale font based on image width
      label_thickness = max(1, int(w / 400))
     
      cv2.putText(grid_img, label, (x_start + 10, y_start + 30),
           cv2.FONT_HERSHEY_SIMPLEX, label_scale, (255, 255, 255), label_thickness + 1)
      cv2.putText(grid_img, label, (x_start + 10, y_start + 30),
           cv2.FONT_HERSHEY_SIMPLEX, label_scale, (0, 0, 0), label_thickness)
   
    return grid_img
 
  print("Controls:")
  print("- Brightness: Adjust image brightness")
  print("- Contrast: Adjust image contrast")
  print("- Auto Mode: 0=Manual, 1=Statistical, 2=Histogram, 3=Adaptive, 4=Exposure, 5=CLAHE")
  print("- Press 'a' to show auto adjustment analysis")
  print("- Press 'r' to reset to original")
  print("- Press 'q' to quit")
 
  while True:
   # Get current trackbar positions
    brightness = cv2.getTrackbarPos('Brightness', window_name)
    contrast = cv2.getTrackbarPos('Contrast', window_name)
    auto_mode = cv2.getTrackbarPos('Auto Mode', window_name)
   
   # Manual adjustment
    if auto_mode == 0:
      alpha = contrast / 100.0
      beta = brightness - 50
      adjusted_img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
      mode_text = f"Manual: Alpha={alpha:.2f}, Beta={beta}"
   
   # Auto adjustments
    elif auto_mode == 1: # Statistical
      alpha, beta = auto_bc.auto_adjust_statistical(img)
      adjusted_img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
      mode_text = f"Statistical: Alpha={alpha:.2f}, Beta={beta:.1f}"
   
    elif auto_mode == 2: # Histogram
      alpha, beta = auto_bc.auto_adjust_histogram(img)
      adjusted_img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
      mode_text = f"Histogram: Alpha={alpha:.2f}, Beta={beta:.1f}"
   
    elif auto_mode == 3: # Adaptive
      alpha, beta = auto_bc.auto_adjust_adaptive(img)
      adjusted_img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
      mode_text = f"Adaptive: Alpha={alpha:.2f}, Beta={beta:.1f}"
   
    elif auto_mode == 4: # Exposure
      alpha, beta = auto_bc.auto_adjust_exposure(img)
      adjusted_img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
      mode_text = f"Exposure: Alpha={alpha:.2f}, Beta={beta:.1f}"
   
    elif auto_mode == 5: # CLAHE
      adjusted_img = apply_clahe(img)
      mode_text = "CLAHE: Adaptive Histogram Equalization"
   
   # Add mode text to image - scale text based on image size
    display_img = adjusted_img.copy()
    text_scale = max(0.5, min(1.5, original_width / 600.0))
    text_thickness = max(1, int(original_width / 400))
   
    cv2.putText(display_img, mode_text, (10, 30),
         cv2.FONT_HERSHEY_SIMPLEX, text_scale, (255, 255, 255), text_thickness + 1)
    cv2.putText(display_img, mode_text, (10, 30),
         cv2.FONT_HERSHEY_SIMPLEX, text_scale, (0, 0, 0), text_thickness)
   
   # Display the adjusted image at original size
    cv2.imshow(window_name, display_img)
   
   # Handle key presses
    key = cv2.waitKey(1) & 0xFF
   
    if key == ord('q'):
      break
    elif key == ord('r'): # Reset
      cv2.setTrackbarPos('Brightness', window_name, 50)
      cv2.setTrackbarPos('Contrast', window_name, 100)
      cv2.setTrackbarPos('Auto Mode', window_name, 0)
    elif key == ord('a'): # Show auto adjustment comparison
     # Generate all auto adjustments
      stat_alpha, stat_beta = auto_bc.auto_adjust_statistical(img)
      hist_alpha, hist_beta = auto_bc.auto_adjust_histogram(img)
      adap_alpha, adap_beta = auto_bc.auto_adjust_adaptive(img)
      expo_alpha, expo_beta = auto_bc.auto_adjust_exposure(img)
     
      results = [
        img, # Original
        cv2.convertScaleAbs(img, alpha=stat_alpha, beta=stat_beta), # Statistical
        cv2.convertScaleAbs(img, alpha=hist_alpha, beta=hist_beta), # Histogram
        cv2.convertScaleAbs(img, alpha=adap_alpha, beta=adap_beta), # Adaptive
        cv2.convertScaleAbs(img, alpha=expo_alpha, beta=expo_beta), # Exposure
        apply_clahe(img) # CLAHE
      ]
     
      labels = [
        "Original",
        f"Statistical\nα={stat_alpha:.2f} β={stat_beta:.1f}",
        f"Histogram\nα={hist_alpha:.2f} β={hist_beta:.1f}",
        f"Adaptive\nα={adap_alpha:.2f} β={adap_beta:.1f}",
        f"Exposure\nα={expo_alpha:.2f} β={expo_beta:.1f}",
        "CLAHE"
      ]
     
      comparison = create_comparison_display(img, results, labels)
      cv2.imshow(auto_window, comparison)
     

     # Resize comparison window to fit the grid
      grid_height, grid_width = comparison.shape[:2]
      cv2.resizeWindow(auto_window, grid_width, grid_height)
     
     # Print image statistics
      stats = auto_bc.analyze_image(img)
      print(f"\nImage Statistics:")
      print(f"Mean: {stats['mean']:.1f}")
      print(f"Std: {stats['std']:.1f}")
      print(f"Range: {stats['min']:.0f} - {stats['max']:.0f}")
      print(f"Dynamic Range: {stats['range']:.0f}")
 
  cv2.destroyAllWindows()

if __name__ == "__main__":
  main()