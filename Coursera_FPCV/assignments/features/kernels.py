import numpy as np

### Kernels ###

SOBEL_KERNEL_X_3 = np.array([[-1, 0, 1],
                            [-2, 0, 2],
                            [-1, 0, 1]], dtype=np.float32)

SOBEL_KERNEL_Y_3 = np.array([[1, 2, 1],
                            [0, 0, 0],
                            [-1, -2, -1]], dtype=np.float32)

SOBEL_KERNEL_X_5 = np.array([[-2, -1, 0, 1, 2],
                            [-3, -2, 0, 2, 3],
                            [-4, -3, 0, 3, 4],
                            [-3, -2, 0, 2, 3],
                            [-2, -1, 0, 1, 2]], dtype=np.float32)

SOBEL_KERNEL_Y_5 = np.array([[2, 3, 4, 3, 2],
                            [1, 2, 3, 2, 1],
                            [0, 0, 0, 0, 0],
                            [-1, -2, -3, -2, -1],
                            [-2, -3, -4, -3, -2]], dtype=np.float32)

LAPLACIAN_KERNEL_1D_X = np.array([[1, -2, 1]], dtype=np.float32)
LAPLACIAN_KERNEL_1D_Y = np.array([[1], [-2], [1]], dtype=np.float32)

LAPLACIAN_KERNEL_2D = np.array([[0, 1, 0],
                             [1, -4, 1],
                             [0, 1, 0]], dtype=np.float32)

    