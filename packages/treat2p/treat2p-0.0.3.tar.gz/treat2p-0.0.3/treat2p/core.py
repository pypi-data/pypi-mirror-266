import os
from logging import getLogger
from tqdm import tqdm
from joblib import parallel_backend, delayed, Parallel
from .utils import ParameterRegistrator, tqdm_joblib
from .corrections import neuropil, slow_trend
from .normalisation import center_normalize, delta_over_F
import numpy as np


def run_treat2p(
    suite2p_results_path, *, plane=0, chan=1, rootnames={}, extension="npy", backend="loky", n_jobs=6, **kwargs
):
    """Applies parallel processing to run a pipeline of modifications on Suite2p output files.
    Copies fluorescence, neuropil, and other data into corresponding arrays, applies necessary corrections
    and saves them back into Suite2p.

    Args:
        # IO parameters :
            suite2p_results_path (_type_): Path to the output files from Suite2p.
            plane (int, optional):  The plane number to process. Defaults to 0.
            chan (int, optional): The channel number to process. One based (as is suite2p) set to 2 for channel n°2.
                Defaults to 1.
            rootnames (dict, optional): Root names of the numpy file if need to change.
              Example to change the Fneu file lookup : set rootnames = {"Fneu": "arbitrary_file_name"}.
              You can set multiple of them at once in the same dict. Defaults to {}.
            extension (str, optional): File extension for intput/output files. Defaults to "npy".

        # Performance parameters
            backend (str, optional): The processing backend to use. Defaults to "loky".
            n_jobs (int, optional): Number of processors used. set to 1 for no parallel processing.

        # Pipeline modules selection parameters
            neuropil_correction_factor (NoneType or float, optional) : if not None, set it's value to the neuropil
                correction and skip neuropil_factor_ARDSIP estimation. Must be between 0 and 1.
                A reasonable "good" value is usually 0.7 or 0.5. Defaults to None
            do_slow_trend_correction (bool, optional) : Wether or not to do the slow trend neuropil correction.
            Defaults to True

        # Arguments to neuropil_factor_ARDSIP :
            max_iterations (int, optional): The maximum number of iterations to perform. Default is 10.
            long_window_length (int, optional): The length of the long sliding window. Default is 30.
            short_window_length (int, optional): The length of the short sliding window. Default is 3.
            baseline_percentile (float, optional): The percentile of the baseline fluorescence. Default is 10.
            convergence_criteria (float, optional): The criteria for convergence. Default is 0.025.
            autoregressed_activity_threshold (float, optional): The threshold for determining if there is activity in
            the cell based on autoregression. Default is 0.5.
            initial_neuropil_factor (float, optional): The initial neuropil factor. Default is 0.5.
            downsampling (float, optional): How much downsampled is the original aray when computing baseline. 1 means
            no downsampling, 4 means 1 smple out of 4 is used.
                Higher values speedup the computation at fidelity cost. Default is 4.
            zscoring_mid_percentile (float, optional): Upper percentile used for zscoring. Default is 16.
            zscoring_low_percentile (float, optional): Lower percentile used for zscoring. Default is 2.3.
                Both of zscoring_mid_percentile and zscoring_low_percentile refer to z_score_from_percentile arguments.
                See that function for more details.

        # Arguments to estimate_slow_trend :
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
    """

    def make_file_path(_type, channel_dependant=True):
        if _type in rootnames.keys():
            rootname = rootnames[_type]
        else:
            rootname = _type
        chan_supp = f"_chan{chan}" if chan > 1 and channel_dependant else ""
        file_path = os.path.join(suite2p_results_path, f"plane{plane}", f"{rootname}{chan_supp}.{extension}")
        return file_path

    local_log = getLogger("treat2p")

    F_file = make_file_path("F")
    Fneu_file = make_file_path("Fneu")

    stat_file = make_file_path("stat", channel_dependant=False)
    ops_file = make_file_path("ops", channel_dependant=False)

    Fs = np.load(F_file, allow_pickle=True)
    Fneus = np.load(Fneu_file, allow_pickle=True)

    original_stats = np.load(stat_file, allow_pickle=True)
    original_ops = np.load(ops_file, allow_pickle=True).item()

    local_log.info(f"Found F, Fneu, stats and ops files at the specified root : {suite2p_results_path}")

    local_log.info(f"Running the signal treatment pipeline over {Fs.shape[0]} rois on {n_jobs} processors. Hold tight.")
    with parallel_backend(backend, n_jobs=n_jobs), tqdm_joblib(tqdm(desc="Treating ROIS signal", total=Fs.shape[0])):
        results = Parallel()(delayed(pipeline)(F, Fneu, **kwargs) for F, Fneu in zip(Fs, Fneus))

    local_log.info("Processing finished. About to save the output")

    # save outputs to suite2p results folder
    outputs, corr_stats, final_ops = (
        [item[0] for item in results],
        [item[1] for item in results],
        [item[2] for item in results],
    )
    reformated_outputs = {}
    for name in outputs[0].keys():
        file_name = make_file_path(name)
        reformated_outputs[name] = np.array([output[name] for output in outputs], dtype=np.float32)
        np.save(file_name, reformated_outputs[name], allow_pickle=True)  # save Fcorr, Fnorm etc...

    for roi_nb in range(original_stats.shape[0]):
        original_stats[roi_nb].update(corr_stats[roi_nb])
    np.save(stat_file, original_stats, allow_pickle=True)  # save new stats with treat2p field
    final_ops = {"treat2p": final_ops[0]}
    original_ops.update(final_ops)
    np.save(ops_file, np.array(original_ops), allow_pickle=True)  # save new ops with treat2p field

    return reformated_outputs, original_stats, original_ops


def pipeline(
    F,
    Fneu,
    do_slow_trend_correction=True,
    do_delta_f=True,
    do_normalization=True,
    normalization_percentile=None,
    neuropil_correction_factor=None,
    F0_index=5,
    F0_span=30,
    # if not None, set it's value to the neuropil correction and skip neuropil_factor_ARDSIP estimation.
    # Must be between 0 and 1.
    # A reasonable "good" value is usually 0.7 or .5
    **kwargs,
):
    """
    Corrects the signals of ROIs by performing slow trend correction and neuropil correction using the specified mode.

    Args:
        F (numpy.ndarray): The array of fluorescence intensity for the cell.
        F_Neu (numpy.ndarray): The array of fluorescence intensity for the neuropil.
        neuropil_correction_factor (NoneType or float) : if not None, set it's value to the neuropil correction and skip
             neuropil_factor_ARDSIP estimation. Must be between 0 and 1.
            A reasonable "good" value is usually 0.7 or .5
        do_slow_trend_correction (bool) : Wether or not to do the slow trend neuropil correction.
        # Arguments to neuropil_factor_ARDSIP :
            max_iterations (int, optional): The maximum number of iterations to perform. Default is 10.
            long_window_length (int, optional): The length of the long sliding window. Default is 30.
            short_window_length (int, optional): The length of the short sliding window. Default is 3.
            baseline_percentile (float, optional): The percentile of the baseline fluorescence. Default is 10.
            convergence_criteria (float, optional): The criteria for convergence. Default is 0.025.
            autoregressed_activity_threshold (float, optional): The threshold for determining if there is activity in
                the cell based on autoregression. Default is 0.5.
            initial_neuropil_factor (float, optional): The initial neuropil factor. Default is 0.5.
            downsampling (float, optional): How much downsampled is the original aray when computing baseline.
                1 means no downsampling, 4 means 1 smple out of 4 is used.
                Higher values speedup the computation at fidelity cost. Default is 4.
            zscoring_mid_percentile (float, optional): Upper percentile used for zscoring. Default is 16.
            zscoring_low_percentile (float, optional): Lower percentile used for zscoring. Default is 2.3.
                Both of zscoring_mid_percentile and zscoring_low_percentile refer to z_score_from_percentile arguments.
                See that function for more details.

        # Arguments to estimate_slow_trend :
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
        List of numpy arrays containing the corrected signal data for each ROI in the DataFrame.
    """
    new_stats = {}
    outputs = {}
    with ParameterRegistrator("treat2p") as ops:
        Fcorrected, stats = neuropil(F, Fneu, neuropil_correction_factor=neuropil_correction_factor, **kwargs)
        new_stats.update(stats)

        if do_slow_trend_correction:
            Fcorrected = slow_trend(Fcorrected, **kwargs)

        outputs["F_corrected"] = Fcorrected

        if do_delta_f:
            outputs["F_var"] = delta_over_F(Fcorrected, F0_index=F0_index, F0_span=F0_span)

        if do_normalization:
            outputs["F_norm"] = center_normalize(Fcorrected, percentile=normalization_percentile)

    return outputs, new_stats, ops
