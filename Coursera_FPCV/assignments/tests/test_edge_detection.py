import numpy as np
from scipy.signal import convolve2d
import cv2
import os

from features import edges

### Edge Detection Pipeline ###


### Utility functions ###

def load_image(path):
    path = os.path.abspath(path)
    assert os.path.exists(path), f"Image path {path} does not exist."
    cv2_image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    return np.array(cv2_image, dtype=np.float32) / 255

def save_image(path, image):
    path = os.path.abspath(path)
    folder = os.path.dirname(path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    cv2.imwrite(path, (image * 255).astype(np.uint8))
    print(f"Saved image to {path}")

def save_output(path, input, edges):

    # Stack 2 images side by side for comparison
    if len(edges.shape) == 2:
        edges = np.stack([edges, edges, edges], axis=-1)
    if len(input.shape) == 2:
        input = np.stack([input, input, input], axis=-1)

    combined_image = np.concatenate([input, edges], axis=1)
    save_image(path, combined_image)

EDGE_DETECTION_METHODS = {
    "sobel": edges.sobel_detector,
    "laplacian": edges.laplacian_detector,
    "canny": edges.canny_detector
}

def edge_detection(images, method="sobel", **kwargs):
    for i, image_path in enumerate(images):
        # Load an image
        image_name = os.path.basename(image_path).split('.')[0]
        image = load_image(image_path)

        # Apply edge detection
        if method not in EDGE_DETECTION_METHODS:
            raise ValueError(f"Unsupported edge detection method: {method}")
        edges = EDGE_DETECTION_METHODS[method](image, **kwargs)
        
        print("Processed image {}/{}: {}".format(i+1, len(images), image_name))
        # Save the result
        kwargs_values = "-".join([f"{k}{v}" for k, v in kwargs.items()])
        subfolder = f"{method}-{kwargs_values}" if kwargs_values else method
        save_output(f"output/{subfolder}/{image_name}-edges.png", image, edges)

if __name__=="__main__":
    # Collect all images in the images/ directory
    images = []
    for os_file in os.listdir("images/"):
        images.append(os.path.join("images/", os_file))    
    
    # images = ["images/Logo.png"]
    edge_detection(images, 
                   method="sobel", 
                   sobel_size=3, 
                   threshold_method="single", 
                   threshold=0.4)
    edge_detection(images, 
                   method="sobel", 
                   sobel_size=5, 
                   threshold_method="hysteresis", 
                   hysteresis_low=2.5, 
                   hysteresis_high=3)
    edge_detection(images, 
                   method="laplacian")
    edge_detection(images, 
                   method="canny", 
                   low_threshold=-0.12, 
                   high_threshold=0.12)