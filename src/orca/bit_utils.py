import numpy as np


def get_lsb(value: np.int32) -> int:
    """Gets the least significant bits of a given 32bit int."""
    return np.bitwise_and([value], [0xFFFF])[0].item()


def get_msb(value: np.int32) -> int:
    """Gets the most significant bits of a given 32bit int."""
    return np.right_shift(value, 16).item()


def combine_low_high(low: np.uint16, high: np.uint16) -> int:
    """Returns a uint32 (as int) from combining the low and high bits."""
    return ((high * (np.left_shift(1, 16))) + low).item()
