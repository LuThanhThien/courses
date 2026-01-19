import numpy as np
from scipy.signal import convolve2d
import cv2
import os

from .kernels import (
    SOBEL_KERNEL_X_3, 
    SOBEL_KERNEL_Y_3, 
    SOBEL_KERNEL_X_5, 
    SOBEL_KERNEL_Y_5,
    LAPLACIAN_KERNEL_2D
)

### Edge Detection Methods ###

def single_threshold(magnitude, threshold):
    return (magnitude >= threshold).astype(np.float32)

def hysteresis_threshold(magnitude, low, high):
    strong_edges = (magnitude >= high).astype(np.float32)
    weak_edges = ((magnitude >= low) & (magnitude < high)).astype(np.float32)
    
    # Use connectivity to link weak edges to strong edges
    from scipy.ndimage import label, generate_binary_structure
    structure = generate_binary_structure(2, 2)
    labeled, num_features = label(strong_edges, structure=structure)
    
    final_edges = np.zeros_like(magnitude, dtype=np.float32)
    for i in range(1, num_features + 1):
        mask = (labeled == i)
        final_edges += mask.astype(np.float32)
        # Add weak edges connected to this strong edge
        weak_connected = convolve2d(mask.astype(np.float32), structure, mode='same') > 0
        final_edges += (weak_edges * weak_connected).astype(np.float32)
    
    final_edges = (final_edges > 0).astype(np.float32)
    return final_edges

def sobel_2d(input, kernel_x=SOBEL_KERNEL_X_3, kernel_y=SOBEL_KERNEL_Y_3):
    Ix = convolve2d(input, kernel_x, mode='same')
    Iy = convolve2d(input, kernel_y, mode='same')
    mag = np.sqrt(Ix**2 + Iy**2)
    orient = np.arctan2(Iy, Ix)
    return mag, orient

def sobel_detector(input, 
          sobel_size=3, 
          threshold_method="single", 
          threshold=0.4, 
          hysteresis_low=0.4, 
          hysteresis_high=0.7):
    kernel_x = None
    kernel_y = None
    if sobel_size == 3:
        kernel_x = SOBEL_KERNEL_X_3
        kernel_y = SOBEL_KERNEL_Y_3
    elif sobel_size == 5:
        kernel_x = SOBEL_KERNEL_X_5
        kernel_y = SOBEL_KERNEL_Y_5
    else:
        raise ValueError("Unsupported sobel_size. Use 3 or 5.")

    mag, orient = sobel_2d(input, kernel_x, kernel_y)

    # Apply a threshold to get mask
    mask = None
    if threshold_method == "single":
        mask = single_threshold(mag, threshold)
    elif threshold_method == "hysteresis":
        mask = hysteresis_threshold(mag, hysteresis_low, hysteresis_high)
    else:
        raise ValueError(f"Unsupported threshold_method: {threshold_method}")    
    
    # Apply the mask and return edges
    mag = mag * mask 
    return mag > 0

def gaussian_2d(input, size=5, sigma=1.0):
    ax = np.linspace(-(size // 2), size // 2, size)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx**2 + yy**2) / (2.0 * sigma**2))
    kernel = kernel / np.sum(kernel)
    return convolve2d(input, kernel, mode='same')

### Laplacian of Gaussian (LoG) Edge Detection ###

def zero_crossing(L, threshold_low, threshold_high):
    edges = np.zeros_like(L)
    for i in range(1, L.shape[0]-1):
        for j in range(1, L.shape[1]-1):
            patch = L[i-1:i+2, j-1:j+2]
            if np.max(patch) > threshold_high and np.min(patch) < threshold_low:
                edges[i, j] = 1.0
    return edges


def bilinear_interpolate(I, x, y):
    h, w = I.shape

    x0 = int(np.floor(x))
    y0 = int(np.floor(y))
    x1 = x0 + 1
    y1 = y0 + 1

    # Boundary check
    if x0 < 0 or x1 >= w or y0 < 0 or y1 >= h:
        return 0.0

    Ia = I[y0, x0]
    Ib = I[y0, x1]
    Ic = I[y1, x0]
    Id = I[y1, x1]

    a = x - x0
    b = y - y0

    return (Ia * (1-a) * (1-b) +
            Ib * a * (1-b) +
            Ic * (1-a) * b +
            Id * a * b)

def laplacian_1d(input, theta):
    # calculate the dx, dy
    dx = np.cos(theta)
    dy = np.sin(theta)

    # Initialize the output
    L = np.zeros_like(input)
    for y in range(input.shape[0]):
        for x in range(input.shape[1]):
            # intepolation points
            x_plus = x + dx[y, x]
            y_plus = y + dy[y, x]
            x_minus = x - dx[y, x]
            y_minus = y - dy[y, x]
            I_plus = bilinear_interpolate(input, x_plus, y_plus)
            I_minus = bilinear_interpolate(input, x_minus, y_minus)

            # Laplacian response
            L[y, x] = I_plus - 2 * input[y, x] + I_minus

    return L

def laplacian_2d(input):
    kernel = LAPLACIAN_KERNEL_2D
    L = convolve2d(input, kernel, mode='same')
    return L

def laplacian_detector(input, threshold=0.03):
    # Pre-smooth the image with a Gaussian filter
    input = gaussian_2d(input, size=3, sigma=1.0)
    
    # Apply Laplacian filter
    L = laplacian_2d(input)
    print(f"Laplacian min: {L.min()}, max: {L.max()}")
    
    # Zero-crossing detection    
    edges = zero_crossing(L, -threshold, threshold)

    return edges

### Canyn Edge Detector ###

def canny_detector(input, low_threshold=-0.03, high_threshold=0.03):
    # denoise by Gaussian filter
    input = gaussian_2d(input, size=5, sigma=1.0)
    
    # image gradient and orientation using Sobel
    mag, orient = sobel_2d(input, SOBEL_KERNEL_X_3, SOBEL_KERNEL_Y_3)
    
    # 1D laplacian along gradient direction
    L = laplacian_1d(mag, orient)
    
    # zero-crossing detection
    edges = zero_crossing(L, low_threshold, high_threshold)
    
    return edges
