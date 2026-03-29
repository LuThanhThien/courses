import matplotlib.pyplot as plt
import numpy as np
import cv2
import os
from features.boundary import active_contours

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
    
def save_active_contours(path, image, contour, color=(0, 255, 0), thickness=2):
    # Ensure 3-channel image
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Ensure contour shape: (N, 1, 2)
    contour = np.asarray(contour, dtype=np.int32)
    contour = contour.reshape((-1, 1, 2))

    overlay = image.copy()
    cv2.drawContours(overlay, [contour], -1, color, thickness)

    save_image(path, overlay)


def save_magnitude_image(path, magnitude, cmap="inferno"):
    """
    magnitude: 2D numpy array (float)
    cmap: e.g. 'gray', 'viridis', 'inferno', 'plasma'
    """

    mag = magnitude.astype(np.float32)

    # Normalize to [0, 1]
    mag -= mag.min()
    if mag.max() > 0:
        mag /= mag.max()

    plt.figure(figsize=(6, 6))
    plt.axis("off")
    plt.imshow(mag, cmap=cmap)
    plt.savefig(path, bbox_inches="tight", pad_inches=0)
    plt.close()


def save_contour_evolution_video(
    path,
    image,
    contours_profile,
    fps=10,
    color=(0, 255, 0),
    thickness=2
):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Ensure base image is uint8 BGR
    if len(image.shape) == 2:
        base_img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        base_img = image.copy()

    if base_img.dtype != np.uint8:
        base_img = np.clip(base_img, 0, 255)
        if base_img.max() <= 1.0:
            base_img = (base_img * 255)
        base_img = base_img.astype(np.uint8)

    h, w = base_img.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, fps, (w, h))

    for i, contour in enumerate(contours_profile):
        frame = base_img.copy()

        contour = np.asarray(contour, dtype=np.int32).reshape((-1, 1, 2))
        cv2.drawContours(frame, [contour], -1, color, thickness)

        cv2.putText(
            frame,
            f"Iteration {i}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        writer.write(frame)

    writer.release()


def save_binary_circle(
    path,
    image_size=(256, 256),
    radius=80,
    center=None
):
    """
    Saves a binary image containing a filled circle.
    
    path: output file path
    image_size: (H, W)
    radius: circle radius in pixels
    center: (x, y), defaults to image center
    """

    h, w = image_size
    img = np.zeros((h, w), dtype=np.uint8)

    if center is None:
        center = (w // 2, h // 2)

    cv2.circle(
        img,
        center=center,
        radius=radius,
        color=255,
        thickness=-1  # filled circle
    )

    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, img)

    print(f"Saved binary circle image to {path}")


### Boundary detection pipeline ###

def boundary_detection(images, **kwargs):
    
    for image_path in images:
        # Loading image
        print(f"Processing image: {image_path}")
        image = load_image(image_path)

        # Apply active contours
        contours_profile = active_contours(image, **kwargs)
        
        # Save results
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        save_active_contours(f"output/boundary/{base_name}_active_contours_mid.png", image, contours_profile[len(contours_profile)//2])
        save_active_contours(f"output/boundary/{base_name}_active_contours.png", image, contours_profile[-1])
        save_contour_evolution_video(f"output/boundary/{base_name}_active_contours.mp4", image, contours_profile, fps=1)


if __name__=="__main__":
    # Collect all images in the images/ directory
    images = []
    for os_file in os.listdir("images/"):
        images.append(os.path.join("images/", os_file))    
    
    save_binary_circle("images/Circle.png", radius=100)
    images = ["images/Circle.png"]
    
    boundary_detection(images, 
                       alpha=0.1, 
                       beta=0.4, 
                       gamma=5.0,
                       kernel_size=5,
                       num_points=30, 
                       eps=0.03,
                       max_iterations=100)
    
    
    