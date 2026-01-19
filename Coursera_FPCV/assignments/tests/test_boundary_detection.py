import numpy as np
from scipy.signal import convolve2d
import cv2
import os

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
    
def save_active_contours(path, input, contours):

    # Stack 2 images side by side for comparison
    if len(input.shape) == 2:
        input = np.stack([input, input, input], axis=-1)

    combined_image = np.concatenate([input, contours], axis=1)
    save_image(path, combined_image)

### Active Contours Implementation ###    
from features import sobel_2d, gaussian_2d

def internal_energy(points, alpha, beta):
    num_points = len(points)
    points_shifted_right = np.roll(points, -1, axis=0)
    points_shifted_left = np.roll(points, 1, axis=0)
    
    # Elasticity 
    Ei = alpha * np.sum(np.square(points - points_shifted_right), axis=1)
    
    # Bending
    Ei += beta * np.sum(np.square(points - 2 * points_shifted_right + points_shifted_left), axis=1)

    return Ei

def external_energy(image, points, kernel_size=3):
    # Compute external energy based on image gradient
    return np.zeros(len(points))  # Placeholder

def active_contours(image, 
                    alpha=0.1, 
                    beta=0.4, 
                    gamma=0.1, 
                    kernel_size=3,
                    num_points=100, 
                    threshold=0.3,
                    max_iterations=250):
    contours = None
    
    # Step 1: Compute image gradients
    magnitude, _ = sobel_2d(gaussian_2d(image))

    # Step 2: Initialize contour points (circle in the center)
    points = np.zeros((num_points, 2), dtype=np.float32)
    center_x, center_y = image.shape[1] // 2, image.shape[0] // 2
    radius = min(center_x, center_y) // 2
    for i in range(num_points):
        theta = 2 * np.pi * i / num_points
        points[i, 0] = center_x + radius * np.cos(theta)
        points[i, 1] = center_y + radius * np.sin(theta)
    
    # Step 3: Interatively update
    while max_iterations > 0:
        max_iterations -= 1
        
        # Compute internal energy matrix
        Ei = internal_energy_matrix(points, alpha, beta)
        
        # Compute external energy
        #todo
    
    return contours 

### Boundary detection pipeline ###

def boundary_detection(images, **kwargs):
    
    for image_path in images:
        # Loading image
        print(f"Processing image: {image_path}")
        image = load_image(image_path)

        # Apply active contours
        contours = active_contours(image, **kwargs)
        
        # Save results
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        save_active_contours(f"output/boundary/{base_name}_active_contours.png", image, contours)


if __name__=="__main__":
    # Collect all images in the images/ directory
    images = []
    for os_file in os.listdir("images/"):
        images.append(os.path.join("images/", os_file))    
    
    images = ["images/Flower-Pot.jpg"]
    
    boundary_detection(images, 
                       alpha=0.1, 
                       beta=0.4, 
                       gamma=0.1, 
                       num_points=100, 
                       threshold=0.3,
                       max_iterations=250)
    
    
    