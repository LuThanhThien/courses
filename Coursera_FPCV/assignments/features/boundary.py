import numpy as np

### Active Contours Implementation ###    
from features import sobel_2d, gaussian_2d

def initialize_active_contour(magnitude, image_shape, num_points=100, radius_frac=0.5):
    h, w = image_shape

    # Avoid noise dominance: threshold small gradients
    mag = magnitude.copy()
    mag[mag < 0.05 * mag.max()] = 0.0

    # Coordinate grids
    ys, xs = np.mgrid[0:h, 0:w]

    total_mag = np.sum(mag)

    if total_mag > 0:
        center_x = int(np.sum(xs * mag) / total_mag)
        center_y = int(np.sum(ys * mag) / total_mag)
    else:
        # fallback
        center_x = w // 2
        center_y = h // 2

    radius = min(center_x, center_y, w - center_x, h - center_y) * radius_frac

    points = np.zeros((num_points, 2), dtype=np.int32)

    for i in range(num_points):
        theta = 2 * np.pi * i / num_points
        points[i, 0] = (center_x + radius * np.cos(theta)).astype(np.int32)
        points[i, 1] = (center_y + radius * np.sin(theta)).astype(np.int32)

    return points



def resample_contour_uniform(points, num_points):
    """
    points: (N, 2) array of ordered, closed contour points
    num_points: desired number of points

    returns: (num_points, 2) uniformly spaced contour
    """

    points = np.asarray(points, dtype=np.float32)

    # Close the contour
    closed = np.vstack([points, points[0]])

    # Compute segment lengths
    deltas = np.diff(closed, axis=0)
    segment_lengths = np.linalg.norm(deltas, axis=1)

    # Cumulative arc length
    arc_length = np.concatenate([[0], np.cumsum(segment_lengths)])
    total_length = arc_length[-1]

    # Uniform sampling positions
    uniform_distances = np.linspace(0, total_length, num_points + 1)[:-1]

    # Interpolate
    new_points = np.zeros((num_points, 2), dtype=np.float32)
    seg_idx = 0

    for i, d in enumerate(uniform_distances):
        while arc_length[seg_idx + 1] < d:
            seg_idx += 1

        t = (d - arc_length[seg_idx]) / segment_lengths[seg_idx]
        new_points[i] = closed[seg_idx] + t * deltas[seg_idx]

    return new_points.astype(np.int32)


def internal_energy(points, alpha=0.1, beta=0.4):
    assert len(points) == 3, "Internal energy requires 3 consecutive points only"

    p0 = points[0]
    p1 = points[1]
    p2 = points[2]

    Ei = alpha * np.linalg.norm(p1 - p0)**2
    Ei += beta * np.linalg.norm(p0 - 2*p1 + p2)**2

    return Ei

def active_contours(image, 
                    alpha=0.1, 
                    beta=0.4, 
                    gamma=5.0,
                    kernel_size=3,
                    num_points=100, 
                    eps=0.3,
                    max_iterations=250):
    # Step 1: Compute image gradients
    magnitude, _ = sobel_2d(gaussian_2d(image, size=5, sigma=5))
    # magnitude = magnitude ** 2

    # Step 2: Initialize contour points (circle in the center)
    points = initialize_active_contour(magnitude, image.shape, num_points=num_points, radius_frac=0.6)
    
    points_profile = []
    points_profile.append(points)
    
    # Step 3: Interatively update
    start_kernel = - (kernel_size // 2)
    end_kernel = (kernel_size // 2)
    shape = image.shape
    while max_iterations != 0:
        max_iterations -= 1

        new_points = np.zeros_like(points)
        
        for pi in range(num_points):
            Ei_min = float("inf")
            next_point = points[pi].copy()
            candidates = points.copy()

            pin = (pi - 1) % num_points
            pip = (pi + 1) % num_points
            
            for xi in range(start_kernel, end_kernel + 1):
                for yi in range(start_kernel, end_kernel + 1):
                    
                    candidate = np.array([
                        points[pi][0] + xi,
                        points[pi][1] + yi
                    ])

                    # Clip to image bounds
                    candidate[0] = np.clip(candidate[0], 0, shape[1] - 1)
                    candidate[1] = np.clip(candidate[1], 0, shape[0] - 1)
                    
                    candidates[pi] = candidate
                    
                    # Compute internal energy matrix
                    ei = internal_energy(candidates[[pin, pi, pip]], alpha, beta)
                    ei = ei / (ei.max() + 1e-8)
                    
                    # Compute external energy
                    ex = - magnitude[candidate[1], candidate[0]]

                    # Find min Ei
                    Ei_c = - ei + ex

                    # Update next point greedy way
                    if (Ei_min > Ei_c):
                        Ei_min = Ei_c
                        next_point = candidates[pi].copy()

            print(f"Point {points[pi]} change to {next_point}")
            new_points[pi] = next_point

        points = resample_contour_uniform(new_points, num_points)
        points_profile.append(points)

        mean_motion = np.mean(np.linalg.norm(points_profile[-1] - points_profile[-2], axis=1))
        print(f"Mean motion: {mean_motion}")
        if mean_motion < eps:
            break
        

    return points_profile 
