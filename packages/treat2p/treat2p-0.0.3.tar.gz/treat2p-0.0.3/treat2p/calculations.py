import numpy as np
from logging import getLogger
from scipy.signal import savgol_filter, filtfilt, butter
from scipy.signal.windows import boxcar
from .utils import filter_save_kwargs

### Main functions, used directly in correction


@filter_save_kwargs("F")
def estimate_slow_trend(
    F,
    *,
    window=120,
    slow_trend_percentile=10,
    fps=30,
    step=10,
    filter_savgol=True,
    filter_lowpass=False,
    filter_percentiles=True,
    savgol_window_length=50,
    savgol_polyorder=2,
    lowpass_order=3,
    lowpass_fcut=0.001,  # in Hz
    lowpass_method="gust",
):
    """
    Calculate a slow trend in a calcium imaging trace and correct for it.

    Args:
        F (1D array): The F trace to correct.
        window (int): Time window in seconds to use for percentile
            calculation. Defaults to 120.
        slow_trend_percentile (int): Percentile to use for slow trend
            calculation. Defaults to 10.
        fps (int): Sampling rate of the acquisition. Defaults to 30.
        step (int): Number of samples in between percentile calculation.
            Defaults to 10.
        filter_savgol (bool): Whether to filter the slow trend using
            a Savitzky-Golay filter. Defaults to True.
        savgol_window_length (int): Window length of Savitzky-Golay
            filter. Defaults to 50.
        savgol_polyorder (int): Polynomial order of Savitzky-Golay
            filter. Defaults to 2.

    Returns:
        numpy.array: The corrected trace with the slow trend removed.
    """

    slow_trend = F.copy()

    if filter_percentiles:
        _slow_trend = []
        frames_half_window = int((fps * window) / 2)
        for i in range(0, len(F), 10):
            start = i - frames_half_window
            start = start if start >= 0 else 0
            stop = i + frames_half_window
            stop = stop if stop <= len(F) else len(F)

            value = np.percentile(F[start:stop], slow_trend_percentile)
            _slow_trend.extend([value for _ in range(step)])
        slow_trend = np.asarray(_slow_trend)

    if filter_savgol:
        slow_trend = savgol_filter(slow_trend, window_length=savgol_window_length, polyorder=savgol_polyorder)

    if filter_lowpass:
        b, a = butter(lowpass_order, lowpass_fcut, btype="low", fs=fps, output="ba", analog=False)
        slow_trend = filtfilt(
            b,
            a,
            slow_trend,
            padlen=None,
            padtype="odd",
            method=lowpass_method,
            irlen=None,
            axis=0,
        )

    return np.asarray(slow_trend)[0 : len(F)]


@filter_save_kwargs("F_Cell", "F_Neu")
def neuropil_factor_ARDSIP(
    F_Cell,
    F_Neu,
    *,
    max_iterations=10,
    long_window_length=30,
    short_window_length=3,
    baseline_percentile=10,
    convergence_criteria=0.025,
    autoregressed_activity_threshold=0.5,
    initial_neuropil_factor=0.5,
    downsampling=4,
    zscoring_mid_percentile=16,
    zscoring_low_percentile=2.3,
):
    """This function performs neuropil correction using an AutoRegressed DownSampling Iteration Protocol (ARD-SIP).

    Args:
        F_Cell (numpy.ndarray): The array of fluorescence intensity for the cell.
        F_Neu (numpy.ndarray): The array of fluorescence intensity for the neuropil.
        max_iterations (int, optional): The maximum number of iterations to perform. Default is 10.
        long_window_length (int, optional): The length of the long sliding window. Default is 30.
        short_window_length (int, optional): The length of the short sliding window. Default is 3.
        baseline_percentile (float, optional): The percentile of the baseline fluorescence. Default is 10.
        convergence_criteria (float, optional): The criteria for convergence. Default is 0.025.
        autoregressed_activity_threshold (float, optional): The threshold for determining if there is activity in the
            cell based on autoregression. Default is 0.5.
        initial_neuropil_factor (float, optional): The initial neuropil factor. Default is 0.5.
        downsampling (float, optional): How much downsampled is the original aray when computing baseline.
            1 means no downsampling, 4 means 1 smple out of 4 is used.
            Higher values speedup the computation at fidelity cost. Default is 4.
        zscoring_mid_percentile (float, optional): Upper percentile used for zscoring. Default is 16.
        zscoring_low_percentile (float, optional): Lower percentile used for zscoring. Default is 2.3.
            Both of zscoring_mid_percentile and zscoring_low_percentile refer to z_score_from_percentile arguments.
            See that function for more details.

    Returns:
        dict: A dictionary containing :
            the calculated neuropil factor (float),
            the final neuropil factor after bounding to [0.1, 0.7] (float),
            a list of the neuropil factor across all iterations (list[float])
            a boolean indicating whether the function converged (bool).
    """

    F_Cell = np.asarray(F_Cell)
    F_Neu = np.asarray(F_Neu)

    # loop changing variable :
    neuropil_factor = initial_neuropil_factor
    local_log = getLogger("neuropil_factor_ardsip")
    local_log.debug("Starting Neuropil Refined Correction")
    iteration_results = [initial_neuropil_factor]
    converged = False

    iteration = 0
    activity_periods_mask = None

    for iteration in range(max_iterations):
        local_log.debug(f"Starting new iteration with neuropil_factor : {neuropil_factor:.2f} ")
        F_Corrected = F_Cell - (neuropil_factor * F_Neu)

        if iteration == 0:  # activity_periods_mask is None at that stage, and for further iterations,
            # it has an array shape like F_Corrected
            activity_periods_mask = np.zeros_like(F_Corrected, dtype=bool)

        F_Corrected_activity_removed = F_Corrected.copy()
        F_Corrected_activity_removed[activity_periods_mask] = np.nan
        # suppress periods of ROI activity , in the first iteration include all data
        # ( activity_periods_mask is redefined later)

        low_percentiles = sliding_window_percentile(
            F_Corrected_activity_removed,
            percentile=baseline_percentile,
            window_length=long_window_length,
            window_sample_displacement=downsampling,
            window_internal_downsampling=downsampling + 1,
        )

        # why not using standard zscoring here >?
        F_Corrected_normalized = z_score_percentile(
            F_Corrected - low_percentiles,
            mid_percentile=zscoring_mid_percentile,
            low_percentile=zscoring_low_percentile,
        )

        F_Autoregressed = autoregress(F_Corrected_normalized)

        bool_no_activity = (F_Autoregressed < autoregressed_activity_threshold) & (
            F_Autoregressed > -autoregressed_activity_threshold
        )  # periods without activity
        bool_state_nochange = ~np.abs(np.diff(bool_no_activity.astype(int), prepend=False)).astype(
            bool
        )  # periods of changes between activity / non activity
        bool_stable_no_activity = (
            bool_no_activity & bool_state_nochange
        )  # stable periods without activity nor instantaneous changes

        if np.sum(bool_stable_no_activity) < 0.1 * len(bool_stable_no_activity):
            local_log.warning(
                "Non activity periods cannot realistically consist of less than 10% of all time. Skipping."
            )
            iteration_results.append(np.nan)
            neuropil_factor = neuropil_factor + convergence_criteria
            continue

        activity_periods_mask = ~bool_stable_no_activity  # activity periods are the inverse of no  activity periods

        # loop's final estimation of neuropil_factor through

        F_Cell_copy = F_Cell.copy()
        F_Cell_copy[activity_periods_mask] = np.nan

        F_Neu_copy = F_Neu.copy()
        F_Neu_copy[activity_periods_mask] = np.nan

        short_window_indices = rolling_indices(
            F_Cell_copy,
            window_displacement=short_window_length,
            window_length=short_window_length,
            window_internal_downsampling=1,
        )[0]

        F_Cell_windows = F_Cell_copy[short_window_indices]
        F_Neu_windows = F_Neu_copy[short_window_indices]

        new_neuropil_factor = []
        for cell_chunk, neu_chunk in zip(F_Cell_windows, F_Neu_windows):
            non_nan_vec = ~np.isnan(cell_chunk)
            if sum(non_nan_vec) > 5:  # at least 5 non nan data points needed for regression
                new_neuropil_factor.append(np.polyfit(neu_chunk[non_nan_vec], cell_chunk[non_nan_vec], 1)[0])
            else:
                new_neuropil_factor.append(np.nan)
        new_neuropil_factor = np.array(new_neuropil_factor)
        local_log.debug(
            "Finished calculating chunks regressions with "
            f"{len(new_neuropil_factor[~np.isnan(new_neuropil_factor)])} valid chunks"
        )
        new_neuropil_factor_mean = np.nanmean(new_neuropil_factor)

        divergence = abs(neuropil_factor - new_neuropil_factor_mean)
        neuropil_factor = new_neuropil_factor_mean
        iteration_results.append(neuropil_factor)  # type: ignore
        if divergence < convergence_criteria:
            local_log.info(
                f"Found convergence in {iteration + 1} iterations. Ending with neuropil_factor value : "
                f"{neuropil_factor:.2f} (last run divergence : {divergence:.3f})."
            )
            converged = True
            break

    if converged == False:
        local_log.info(
            f"Found no convergence in {iteration + 1} iterations. "
            f"Ending with neuropil_factor value : {neuropil_factor:.2f}."
        )

    if neuropil_factor < 0.1:
        constrained_neuropil_factor = 0.1
    elif neuropil_factor > 0.7:
        constrained_neuropil_factor = 0.7
    else:
        constrained_neuropil_factor = neuropil_factor

    return {
        "neuropil_factor": neuropil_factor,
        "neuropil_factor_constrained": constrained_neuropil_factor,
        "neuropil_factor_iterations": iteration_results,
        "neuropil_factor_converged": converged,
    }


### Helper functions made to make life easy / enhance speed of above calculations


def rolling_indices(
    array,
    *,
    window_displacement=None,  # how much each window moves from the next one, in seconds units.
    # Results in general downsampling from initial array length
    # after collapsing windows to one number by merging operations such as averaging etc.
    window_length=30,  # in seconds units
    samples_per_sec=30,
    window_internal_downsampling=4,  # if more than one, downsample INSIDE a window. In index units
    window_sample_length=None,  # same as window_length but in sample index units instead of seconds.
    # will skip window_length value if used.
    window_sample_displacement=4,  # same as window_displacement but in sample index units.
    # will skip window_displacement value is used
):
    """
    Specifies the indices in an input 'array' over which rolling windows are defined.
    The indices can be used later to easily and efficiently create such windows with vanilla numpy slicing
    (leveraging SIMD).
    The resulting windows can have optional downsampling and are defined by their length and displacement.

    Args:
        array (numpy.ndarray): Input array over which rolling windows are to be calculated.
        window_displacement (int, optional): Defines how much each window moves from the next one. Defaults to None.
        window_length (int, optional): Defines the desired window length in seconds. Defaults to 30.
        samples_per_sec (int, optional): Defines the number of samples per second in the array. Defaults to 30.
        window_internal_downsampling (int, optional): If more than one, downsample within window. Defaults to 4.
        window_sample_length (int, optional): Same as window_length but in sample indices instead of seconds.
            Will skip window_length value if used. Defaults to None.
        window_sample_displacement (int, optional): Same as window_displacement but in seconds instead of sample points.
            Will skip window_displacement value if used. Defaults to 4.

    Returns:
        tuple: Tuple containing numpy.ndarray of rolling window indices and numpy.ndarray
               of indices central to each window.
    """

    if window_sample_length is None:
        window_sample_length = round(window_length * samples_per_sec)
    else:
        window_sample_length = round(window_sample_length)
    if window_sample_displacement is None:
        if window_displacement is None:
            raise ValueError("window_displacement cannot be None if window_sample_displacement is None.")
        window_sample_displacement = round(window_displacement * samples_per_sec)
    else:
        window_sample_displacement = round(window_sample_displacement)
    half_window_length = round(window_sample_length / 2)
    windows_indices = []
    indices = []
    for i in range(0, len(array) - window_sample_length, window_sample_displacement):
        window = np.array(range(i, i + window_sample_length, window_internal_downsampling), dtype=int)
        windows_indices.append(window)
        indices.append(i + half_window_length)
    return np.array(windows_indices), np.array(indices)


def sliding_window_percentile(input_array, percentile=10, **kwargs):
    """This function applies sliding window computation on an input data array, computing a user-specified percentile
    within each window.
    It uses the 'rolling_indices' to generate windows in the input data. For each generated window,
    it computes the specified percentile and assigns this value to the representative sample for the window.
    For samples not directly represented by a window, the function interpolates the percentile values.

    Args:
        input_array (numpy.ndarray): The array on which sliding window computation is to be performed.
        percentile (int, optional): The percentile to be computed within each window. Defaults to 10.
        **kwargs: Additional keyword arguments to passed to the 'rolling_indices' function.

    Returns:
        numpy.ndarray : Array filled with the computed percentile values for each window,
            with the same shape as 'input_array'.
            For positions between windows, the percentile values are interpolated."""

    long_windows_indices, downsampled_indices = rolling_indices(input_array, **kwargs)

    input_array_long_windows = input_array[long_windows_indices]

    low_percentiles = np.nanpercentile(input_array_long_windows, percentile, axis=1)

    x_indices = np.arange(len(input_array))
    interped_indices = np.setdiff1d(x_indices[downsampled_indices[0] : downsampled_indices[-1]], downsampled_indices)
    interped_values = np.interp(interped_indices, downsampled_indices, low_percentiles)

    interped_low_percentiles = np.full_like(input_array, np.nan, dtype=float)
    interped_low_percentiles[downsampled_indices] = low_percentiles
    interped_low_percentiles[interped_indices] = interped_values
    return interped_low_percentiles


def autoregress(input_array, lag=1, boxcar_value=3):
    prefilter = boxcar_filtering(input_array, boxcar_value=boxcar_value) / 2
    postfilter = boxcar_filtering(np.roll(input_array, -lag), boxcar_value=boxcar_value) / 2
    autoregressed = prefilter * postfilter
    return autoregressed


def boxcar_filtering(x, boxcar_value=3):
    """Applies boxcar filtering on the input data.

    Args:
        x (np.array): The input data for which the boxcar filtering needs to be performed.
        boxcar_value (int, optional): The width of the boxcar window. Defaults to 3.

    Returns:
        np.array: The output data after applying the boxcar filtering.
    """
    filter_window = boxcar(boxcar_value)
    return filtfilt(filter_window / sum(filter_window), [1.0], x)


def z_score_percentile(input_array, mid_percentile=16, low_percentile=2.3):
    """
    This function performs autoregression on a given data array by applying boxcar filtering first to the array and
    then to a copy of the array rolled by a certain lag. The results of these filterings
    are then multiplied elementwise.
    Need to explain the choice of values for this weird zscoring. Why not using standard zscoring ?

    Args:
        input_array (numpy.ndarray): The array on which to perform autoregression.
        lag (int, optional): The size of the shift applied to the input array for the 'rolled' boxcar filtering.
        Default is 1.
        boxcar_value (int, optional): The width of the boxcar window to be applied. Default is 3.

    Returns:
        numpy.ndarray: The array of the resulting autoregressed values. It has the same shape as the input array.
    """
    local_log = getLogger("zscore_percentile")
    low_p_value = np.nanpercentile(input_array, low_percentile)
    mid_p_value = np.nanpercentile(input_array, mid_percentile)
    sigma = mid_p_value - low_p_value
    mean = low_p_value + (
        2 * sigma
    )  # why this weird thing and not simply np.nanpercentile(input_array, 50) as a median ?
    local_log.debug(f"Percentile 'mean' is : {mean}, real median is : {np.nanpercentile(input_array, 50)}")
    local_log.debug(f"Percentile based 'sigma' is : {sigma}, real std is : {np.nanstd(input_array)}")

    return (input_array - mean) / sigma
