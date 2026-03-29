import os
import cv2
import numpy as np

# Utilities

def load_image(path):
    path = os.path.abspath(path)
    assert os.path.exists(path), f"Image path {path} does not exist."
    cv2_image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    return np.array(cv2_image, dtype=np.float32) / 255

def save_image(image, path):
    path = os.path.abspath(path)
    folder = os.path.dirname(path)

    if not os.path.exists(folder):
        os.makedirs(folder)

    img = image.copy()

    # If float image [0,1] → convert to uint8
    if img.dtype != np.uint8:
        img = (img * 255).clip(0, 255).astype(np.uint8)

    # If RGB → convert to BGR before saving
    if img.ndim == 3 and img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    cv2.imwrite(path, img)
    print(f"Saved image to {path}")


def visualize(image, points_set: list, close_shape=False):
    """
    rgb_image: numpy array (H, W, 3) in RGB format
    points_set: list of iterable points, each point is np.array([x, y])
    close_shape: if True, connects last point to first
    """

    # ---------------------------
    # Ensure RGB format
    # ---------------------------
    if image.ndim == 2:
        # grayscale → RGB
        img = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    elif image.ndim == 3 and image.shape[2] == 3:
        img = image.copy()

        # Heuristic: assume OpenCV BGR and convert to RGB
        # If you're sure it's already RGB, remove this line
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    else:
        raise ValueError("Unsupported image format")

    yellow_bgr = (255, 255, 0)  # Yellow in OpenCV (BGR)
    thickness = 1

    for points in points_set:
        pts = np.array(list(points), dtype=np.int32)

        for i in range(len(pts) - 1):
            pt1 = tuple(pts[i])
            pt2 = tuple(pts[i + 1])
            cv2.line(img, pt1, pt2, color=yellow_bgr, thickness=thickness)

        if close_shape and len(pts) > 2:
            cv2.line(img, tuple(pts[-1]), tuple(pts[0]), color=yellow_bgr, thickness=thickness)

    return img


# Hough Transform
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from features.edges import canny_detector
from scipy.ndimage import maximum_filter

def visualize_accumulator(accumulator, save_path, cmap="jet", normalize=True):
    """
    accumulator: 2D numpy array
    save_path: file path to save the image (e.g., "output.png")
    cmap: matplotlib colormap (jet, hot, viridis, plasma, inferno, etc.)
    normalize: scale values to [0,1] for better contrast
    """

    acc = accumulator.copy()

    if normalize:
        max_val = np.max(acc)
        if max_val > 0:
            acc = acc / max_val

    plt.figure(figsize=(6, 6))
    plt.imshow(acc, cmap=cmap, aspect="auto")
    plt.colorbar(label="Votes")
    plt.title("Hough Accumulator")
    plt.xlabel("m")
    plt.ylabel("c")
    plt.tight_layout()

    save_path = Path(save_path).absolute()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()  # important when sav

    print(f"Save to {save_path}")


def generate_accumulator(size=[50, 50], default=0):
    return np.zeros(size) * default


def non_max_suppression_2d(accumulator, 
                           window_size=5, 
                           threshold=0, 
                           max_peaks=None):
    """
    Perform non-maximum suppression on a 2D accumulator.

    Parameters:
        accumulator : 2D numpy array
        window_size : size of suppression window (odd integer)
        threshold   : minimum vote value to keep a peak
        max_peaks   : maximum number of peaks to return (None = all)

    Returns:
        peaks : list of (row, col) indices of detected peaks
    """

    if window_size % 2 == 0:
        raise ValueError("window_size must be odd")

    # Compute local maximum filter
    local_max = maximum_filter(accumulator, size=window_size)

    # Keep only true local maxima
    mask = (accumulator == local_max)

    # Apply threshold
    mask &= (accumulator > threshold)

    # Get peak indices
    peak_indices = np.argwhere(mask)

    # Sort peaks by vote strength (descending)
    peak_values = accumulator[mask]
    sorted_idx = np.argsort(-peak_values)

    peak_indices = peak_indices[sorted_idx]

    if max_peaks is not None:
        peak_indices = peak_indices[:max_peaks]

    return [tuple(idx) for idx in peak_indices]


def hough_transform(edge_image):

    h, w = edge_image.shape

    # ----------------------------
    # Accumulator resolution
    # ----------------------------
    num_theta = 180
    num_rho = 200

    accumulator = np.zeros((num_theta, num_rho))

    # ----------------------------
    # Parameter space definition
    # ----------------------------
    theta_min = -np.pi / 2
    theta_max =  np.pi / 2
    theta_vals = np.linspace(theta_min, theta_max, num_theta)[:, None]

    rho_max = np.sqrt(h*h + w*w)
    rho_min = -rho_max

    # ----------------------------
    # Get edge points
    # ----------------------------
    ys, xs = np.nonzero(edge_image)

    if len(xs) == 0:
        return []

    # ----------------------------
    # Vectorized Hough voting
    # ρ = x cosθ + y sinθ
    # ----------------------------
    rho_vals = xs * np.cos(theta_vals) + ys * np.sin(theta_vals)

    # Map ρ to bin index
    rho_bin = ((rho_vals - rho_min) / (rho_max - rho_min) * (num_rho - 1)).astype(int)

    # Valid mask
    valid_mask = (rho_bin >= 0) & (rho_bin < num_rho)

    theta_indices, point_indices = np.nonzero(valid_mask)
    rho_indices = rho_bin[theta_indices, point_indices]

    # Accumulate votes
    np.add.at(accumulator, (theta_indices, rho_indices), 1)

    visualize_accumulator(accumulator, "output/hough/accumulator.png")

    # ----------------------------
    # Non-Max Suppression
    # ----------------------------
    threshold = 0.3 * accumulator.max()

    peaks = non_max_suppression_2d(
        accumulator,
        window_size=7,
        threshold=threshold,
        max_peaks=20
    )

    # ----------------------------
    # Convert peaks to lines
    # ----------------------------
    lines = []

    for theta_idx, rho_idx in peaks:

        theta = theta_min + (theta_max - theta_min) * theta_idx / (num_theta - 1)
        rho = rho_min + (rho_max - rho_min) * rho_idx / (num_rho - 1)

        # Convert to 2 points
        if abs(np.sin(theta)) > 1e-6:
            x1 = 0
            y1 = (rho - x1 * np.cos(theta)) / np.sin(theta)

            x2 = w - 1
            y2 = (rho - x2 * np.cos(theta)) / np.sin(theta)

            lines.append(((int(x1), int(y1)),
                          (int(x2), int(y2))))
        else:
            # Vertical line case
            x = rho / np.cos(theta)
            lines.append(((int(x), 0),
                          (int(x), h - 1)))

    return lines


# Pipeline

def detector(
        image,
        *args, 
        **kwargs 
):
    output = canny_detector(image, 
                            low_threshold=-0.3, 
                            high_threshold=0.3,
                            gaussian_kwargs=dict(
                                size=5,
                                sigma=1
                            ))
    save_image(output, f"output/hough/edges.png")
    
    points = hough_transform(output)

    output = visualize(image, points)

    return output


def hough_opencv(image, save_path):

    # Ensure uint8 grayscale
    if image.dtype != np.uint8:
        img_gray = (image * 255).clip(0, 255).astype(np.uint8)
    else:
        img_gray = image.copy()

    # ----------------------------
    # Canny Edge Detection
    # ----------------------------
    edges = cv2.Canny(img_gray, 100, 200)
    save_image(edges, "output/hough/edges_cv2.png")

    # ----------------------------
    # Hough Transform (θ–ρ)
    # ----------------------------
    lines = cv2.HoughLines(
        edges,
        rho=1,                # ρ resolution (pixels)
        theta=np.pi/180,      # θ resolution (radians)
        threshold=150         # minimum votes
    )

    # Convert to RGB for drawing
    img_color = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)

    # ----------------------------
    # Draw Lines
    # ----------------------------
    if lines is not None:
        for v in lines[:50]:  # limit for visualization
            rho, theta = v[0][0], v[0][1]
            a = np.cos(theta)
            b = np.sin(theta)

            x0 = a * rho
            y0 = b * rho

            # Two points far away for drawing
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * ( a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * ( a))

            cv2.line(img_color, (x1, y1), (x2, y2),
                     (0, 255, 255), 2)  # Yellow (BGR)

    # ----------------------------
    # Save result
    # ----------------------------
    save_path = os.path.abspath(save_path)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    cv2.imwrite(save_path, img_color)

    print(f"Saved OpenCV Hough result to {save_path}")

    return img_color


def main():
    # Load image
    image_name = "image-03.1"
    image = load_image(f"images/hough/{image_name}.png")

    # # Run program
    # result = detector(image=image)
    
    # # Save results
    # save_image(result, f"output/hough/{image_name}.png")

    # CV2
    hough_opencv(image, f"output/hough/{image_name}_cv2.png")

    return


if __name__=="__main__": 
    main()
