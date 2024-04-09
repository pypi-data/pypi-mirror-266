import numpy as np


def transpose2d(input_matrix: list[list[float]]) -> list:
    """Transpose function that switches the axes of a tensor

    Args:
        input_matrix (list[list[float]]): Matrix as list

    Returns:
        list: Switched matrix
    """
    if not input_matrix or not input_matrix[0]:
        return []

    cols = len(input_matrix[0])
    return [[input_matrix[i][j] for i in range(len(input_matrix))] for j in range(cols)]


def window1d(
    input_array: list | np.ndarray, size: int, shift: int = 1, stride: int = 1
) -> list[list | np.ndarray]:
    """Extracts sliding windows from a 1D array of real numbers,
      such as a time series data.

    Args:
        input_array (list | np.ndarray):
        A list or 1D NumPy array of real numbers representing the time series data.
        size (int): An integer specifying the size of the window.
        shift (int, optional): Step size between different windows. Defaults to 1.
        stride (int, optional): Step size between each windows. Defaults to 1.

    Returns:
        list[list | np.ndarray]: Returns a list of lists or 1D NumPy arrays,
        containing the windows extracted from the input array.
    """
    if isinstance(input_array, list):
        input_array = np.array(input_array)

    return [
        input_array[i : i + size : stride]
        for i in range(0, len(input_array) - size + 1, shift)
    ]


def convolution2d(
    input_matrix: np.ndarray, kernel: np.ndarray, stride: int = 1
) -> np.ndarray:
    """Performs a 2D convolution operation between an input matrix and a kernel matrix.

    Args:
        input_matrix (np.ndarray):
          A 2D NumPy array of real numbers representing the input image or feature map.
        kernel (np.ndarray):
          A 2D NumPy array of real numbers representing the convolution kernel or filter.
        stride (int, optional): Step size for the convolution operation. Defaults to 1.

    Returns:
        np.ndarray: Returns a 2D Numpy array of real numbers
    """

    input_height, input_width = input_matrix.shape
    kernel_height, kernel_width = kernel.shape
    output_matrix = np.array(
        [
            [
                np.sum(
                    input_matrix[i : i + kernel_height, j : j + kernel_width] * kernel
                )
                for j in range(0, input_width - kernel_width + 1, stride)
            ]
            for i in range(0, input_height - kernel_height + 1, stride)
        ]
    )

    return output_matrix
