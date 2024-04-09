from .calculations import estimate_slow_trend, neuropil_factor_ARDSIP
import numpy as np


def slow_trend(F, **kwargs):
    """_summary_

    Args:
        F (_type_): _description_

    Returns:
        _type_: _description_
    """
    slow_F = estimate_slow_trend(F, **kwargs)
    return F - slow_F


def neuropil(
    F,
    Fneu,
    neuropil_correction_factor=None,
    factor_to_use="neuropil_factor_constrained",
    **kwargs,
):
    """Performs correction of F with neuropil signal Fneu with a substraction factor neuropil_correction_factor.
    (Fcorr = F - (Fneu * neuropil_correction_factor) )
    If no neuropil correction factor is supplied, it is determined from F and Fneu with the ARDSIP algorithm.

    Args:
        F (array_like): Raw neuron's fluoresence
        Fneu (array_like): Raw neuron's neuropil (neighbouring region excluding other neurons) fluoresence
        neuropil_correction_factor (float, optional): _description_. Defaults to None.
        factor_to_use (str, optional): _description_. Defaults to "neuropil_factor_constrained".

    Returns:
        array_like: Corrected fluorescence
    """
    stats = {}
    if neuropil_correction_factor is None:
        stats = neuropil_factor_ARDSIP(F, Fneu, **kwargs)
        neuropil_correction_factor = stats[factor_to_use]
    F = np.asarray(F, dtype=np.float64)
    Fneu = np.array(Fneu, dtype=np.float64)
    Fcorr = F - (Fneu * neuropil_correction_factor)
    return Fcorr, stats
