from scipy.stats import zscore
from .utils import filter_save_kwargs
import numpy as np

zscore = filter_save_kwargs("a")(zscore)


@filter_save_kwargs("array")
def delta_over_F(array, F0_index=0, F0_span=1):
    """Performs deltaF over F0 ( with eq : DF0 = F - F0 / F0 )"""

    if array.min() <= 0:
        array = non_zero_raw_fluorescence(array.copy())

    F0_frame = array[F0_index : F0_index + F0_span].mean(axis=0)

    F0_frames = np.repeat(F0_frame[np.newaxis], array.shape[0], axis=0)
    return (array - F0_frames) / F0_frames


def non_zero_raw_fluorescence(array):
    """This simply ensures that raw fluorescence is strictly positive to avoid 0 division errors."""
    return (array - array.min()) + 1


def normalize(values, outmin=0, outmax=1, min_val=None, max_val=None):
    """This function normalizes the input values between a specified range [outmin, outmax].

    The minimum value of the provided values array will be snapped to outmin and the maximum value, to outmax,
    in the output array.
    However, in case you want to account for extra cases of unelikely data
    (ex : minimum of unrealistically low value compared to all the resto of calues)
    you can supply min_val and max_val directly to the function, for example by externally calculating the 99.9
    percentile of the values, thus not taking into account the uncannyly large single value.
    If min_val and max_val are set to None, they are automatically detected with min() and max() from values.
    If they are supplied, the output values can then be out of the range defined by min and max.

    Args:
        values (array_like): The input values to be normalized.
        outmin (float, optional): The lower boundary of the output range. Defaults to 0.
        outmax (float, optional): The upper boundary of the output range. Defaults to 1.
        min_val (float, optional): The curent values lower bound that will be snapped to outmin.
            If none, it is automatically calculated from values.min(). Defaults to None.
        max_val (float, optional): The curent values upper bound that will be snapped to outmax.
            If none, it is automatically calculated from values.max(). Defaults to None.

    Raises:
        ValueError: If the provided min is not strictly inferior to max.

    Returns:
        norm (array_like): The normalized values.
    """
    if outmin >= outmax:
        raise ValueError("min must be strictly inferior to max")

    min_val = values.min() if min_val is None else min_val
    max_val = values.max() if max_val is None else max_val

    ampl = max_val - min_val
    norm = (values - min_val) / ampl  # normalisation between 0 and 1 with eq : Fnorm = F - Fmin / Fmax - Fmin
    target_ampl = outmax - outmin
    norm = (norm * target_ampl) + outmin  # normalization between arbitraty values
    return norm


def center_normalize(array, outmin=0, outmax=1, percentile=None):
    """Normalizes and centers an input array around its mean.
    The values are then scaled so that the mean will be at equidistance of outmin and outmax in the output array.
    The relationship between outmin and outmax and the original data values are :
    outmin, outmax values are snapped from - , + (respectively) of max( abolute (min) vs abolute(max))
    from the values of the data after mean substraction (at 0)

    It accepts an input array, subtracts its mean (thus centering it around zero),
    and then normalizes it to be within a specified range (outmin and outmax).
    By default, the range is between 0 and 1.

    Args:
        array (numpy.ndarray): Input array to be centered and normalized.
        outmin (float, optional): Minimum value for the output normalized array. Defaults to 0.
        outmax (float, optional): Maximum value for the output normalized array. Defaults to 1.
        percentile (float, optionnal) : The maximum percentile that corresponds to the un-normalized value that
            will snap to the output bounds (symetrically around the mean)
            If set to None (default) the current value snapped to the bounds is the maximum absolute value
            between array.min() and array.max() (e.g. normalization via scaling but not translation,
            to stay centered around the mean at 0, that occurs at the 2n line in the code)

    Returns:
        numpy.ndarray: Normalized and centered array with values ranging between specified minimum and maximum values.
    """

    mean = array.mean()
    centered_array = array - mean
    if percentile:
        outermost_bound = max(
            abs(np.percentile(centered_array, 100 - percentile)), abs(np.percentile(centered_array, percentile))
        )
    else:
        outermost_bound = max(abs(centered_array.min()), abs(centered_array.max()))
    return normalize(centered_array, min_val=-outermost_bound, max_val=outermost_bound, outmin=outmin, outmax=outmax)
