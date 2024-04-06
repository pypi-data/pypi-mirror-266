# -*- coding: utf-8 -*-
"""Provides a set of figures of merit to evaluate the performance of classifiers, directly or as custom metrics."""

from typing import Union, Optional, Callable, Any, Literal, Dict, Tuple

import numpy as np
from scipy import stats
import math


FOM_types = Union[Literal["continous"], Literal["hist"], Literal["hist_norm"]]


def get_predefined_FoMs() -> Dict[FOM_types, Tuple[str, Callable[..., Any]]]:
    """Provides a dictionary containing a tuple to build all supported figures of merit.

    Returns
    -------
    Dict[FOM_types, Tuple[str, Callable[..., Any]]]
        For each FOM, the type (continous, histogram or normalized histogram) is given as the first, a reference to the
        function to calculate the FOM value as the second element
    """
    FoMs = {
        "NonOverlap": ("norm_hist", _NonOverlap_),
        "Separation": ("norm_hist", _Separation_),
        "SoverSqrtSB": ("hist", _SoverSqrtSB_),
        "SoverSqrtB": ("hist", _SoverSqrtB_),
        "SoverSqrtBLastBin": ("hist", _SoverSqrtBLastBin_),
        "SLastBin": ("hist", _SLastBin_),
        "BLastBin": ("hist", _BLastBin_),
        "SignificanceSyst": ("hist", _SignificanceSyst_),
        "SoBSignificanceSyst": ("hist", _SoBSignificanceSyst_),
        "PSignificance30": ("hist", _PSignificance30_),  # not working yet, TODO: fix
        "LogLikelihoodRatio": ("hist", _LogLikelihoodRatio_),
        "LogLikelihoodRatioPValue": ("hist", _LogLikelihoodRatioPValue_),
    }
    return FoMs


def build_FoM(
    name: Optional[str] = None, func: Optional[Tuple[FOM_types, Callable[..., Any]]] = None, **kwargs: Any
) -> Union["FigureOfMerit", "HistFigureOfMerit", "NormHistFigureOfMerit", Callable[..., Literal[1]]]:
    """Builds a figure of merit either from a name (for built-in FOMs) or from a callable.

    Parameters
    ----------
    name : Optional[str]
        Name of a built-in FOM. (Default value = None)
    func : Optional[Tuple[FOM_types, Callable[..., Any]]]
        Tuple of type ('continuous' or 'hist' or 'hist_norm', f) where f is a function with the correct signature
        (depending on which type of FoM). (Default value = None)
    **kwargs : Any
        Additional arguments required by the callable func[1].

    Returns
    -------
    Union["FigureOfMerit", "HistFigureOfMerit", "NormHistFigureOfMerit", Callable[..., Literal[1]]]
        Instance of FigureOfMerit, HistFigureOfMerit or NormHistFigureOfMerit, depending on the type of FOM requested.
        When an unsupported type is requested, a dummy lambda is returned instead.
    """
    if func is None:
        predefined = get_predefined_FoMs()
        if name in predefined.keys():
            func = predefined[name]
    if func[0] == "continous":
        return FigureOfMerit(func[1], **kwargs)
    elif func[0] == "hist":
        return HistFigureOfMerit(func[1], **kwargs)
    elif func[0] == "norm_hist":
        return NormHistFigureOfMerit(func[1], **kwargs)
    else:
        print("WARNING: FoM type {} is not implemented! Returning dummy metric...".format(name))
        return lambda *args, **kwargs: 1.0


class FigureOfMerit:
    """Wrapper around a callable to allow providing constant arguments."""

    def __init__(self, func: Callable[..., Any], **kwargs: Any) -> None:
        """Constructs a FigureOfMerit object.

        Parameters
        ----------
        func : Callable[..., Any]
            Callable to calculate the value of the figure of merit. Has to accept three numpy arrays (target labels,
            corresponding predictions and optional weights) and can have additional keyword arguments.
        **kwargs : Any
            Additional keyword arguments for func.

        Returns
        -------
        None
            _description_
        """
        self.func = func
        self.kwargs = kwargs

    def __call__(self, y_true: np.ndarray, y_pred: np.ndarray, sample_weight: Optional[np.ndarray] = None) -> Any:
        """Gives arrays of target labels, predictions, sample weight and possible kwargs to self.func and returns the result.

        Parameters
        ----------
        y_true : np.ndarray
            Array of target labels.
        y_pred : np.ndarray
            Array of predictions corresponding to the target labels.
        sample_weight : Optional[np.ndarray]
            Array of sample weights for each entry in y_true and y_pred. (Default value = None)

        Returns
        -------
        Any
            Return value of the figure of merit calculated by self.func.
        """
        return self.func(y_true, y_pred, sample_weight=sample_weight, **self.kwargs)


class HistFigureOfMerit(FigureOfMerit):
    """Subclass of FigureOfMerit that builds histograms of signal and background predictions for histogram FOMs.

    Only applicable to binary classification, i.e. only two classes (signal and background, corresponding to target
    labels 1 and 0, respectively). The total sum of weights for each class is scaled to the expected number of events.
    A binning optimization is performed when minimal number of signal, background or total events per bin are given.
    """

    def __init__(
        self,
        func: Callable[..., Any],
        exp_sig: Union[float, int],
        exp_bkg: Union[float, int],
        N_bins: int = 100,
        min_events_per_bin: Union[float, int] = 10.0,
        min_s_per_bin: Union[float, int] = 0,
        min_b_per_bin: Union[float, int] = 1.0,
        **kwargs: Any
    ) -> None:
        """Constructs a HistFigureOfMerit object.

        Parameters
        ----------
        func : Callable[..., Any]
            Callable to calculate the value of the figure of merit. Has to accept three numpy arrays (signal and
            background histograms and array of bin edges) and can have additional keyword arguments.
        exp_sig : Union[float, int]
            Number of expected signal events. The weights of signal events are scaled to sum to this number.
        exp_bkg : Union[float, int]
            Number of expected background events. The weights of background events are scaled to sum to this number.
        N_bins : int
            Number of bins of the histogram. If a binning optimization of performed, the initial histograms before
            starting to merge has N_bins bins. (Default value = 100)
        min_events_per_bin : Union[float, int]
            The minimum number of events per bin. During the binning optimization, bins are merged until at least this
            many events are contained in each bin. (Default value = 10.)
        min_s_per_bin : Union[float, int]
            The minimum number of signal events per bin. During the binning optimization, bins are merged until at least
            this many signal events are contained in each bin. (Default value = 0)
        min_b_per_bin : Union[float, int]
            The minimum number of background events per bin. During the binning optimization, bins are merged until at
            least this many background events are contained in each bin. Since many FOMs divide by the number of
            background events, this usually should not be set to zero to ensure numerical stability. (Default value = 1.)
        **kwargs : Any
            Additional keyword arguments of the func.
        """
        super(HistFigureOfMerit, self).__init__(func, **kwargs)
        self.exp_sig = exp_sig
        self.exp_bkg = exp_bkg
        self.N_bins = N_bins
        self.min_events_per_bin = min_events_per_bin
        self.min_s_per_bin = min_s_per_bin
        self.min_b_per_bin = min_b_per_bin

    def __call__(self, y_true: np.ndarray, y_pred: np.ndarray, sample_weight: Optional[np.ndarray] = None) -> Any:
        """Calls the preprocess function to build the histograms, gives them to self.func and returns the result.

        Parameters
        ----------
        y_true : np.ndarray
            Array of target labels.
        y_pred : np.ndarray
            Array of predictions corresponding to the target labels.
        sample_weight : Optional[np.ndarray]
            Array of sample weights for each entry in y_true and y_pred. (Default value = None)

        Returns
        -------
        Any
            Value of the figure of merit calculated by self.func.
        """
        s, b, bins = self.preprocess(y_true, y_pred, sample_weight=sample_weight)
        return self.func(s, b, bins, **self.kwargs)

    def preprocess(
        self, y_true: np.ndarray, y_pred: np.ndarray, sample_weight: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Build the histograms of signal and background events from the target labels and predictions.

        Each event is weighted according to the array of sample weights (if provided), each class is scaled to the
        expected number of events (self.exp_sig and self.exp_bkg). If at least one of the minimum number of signal,
        background or total events are not zero, a binning optimization is performed. Starting from the rightmost bin,
        neighboring bins are merged until the provided conditions are satisfied.

        Parameters
        ----------
        y_true : np.ndarray
            Array of target labels.
        y_pred : np.ndarray
            Array of predictions corresponding to the target labels.
        sample_weight : Optional[np.ndarray]
            Array of sample weights for each entry in y_true and y_pred. (Default value = None)

        Returns
        -------
        Tuple[np.ndarray, np.ndarray, np.ndarray]
            Scaled, binning optimized histograms of signal and background events and corresponding array of bin edges.
        """
        # reshape the input
        y_true = np.reshape(y_true, y_true.shape[0])
        y_pred = np.reshape(y_pred, y_pred.shape[0])

        # first get the DNN predictions for signal and background
        pred_sig = y_pred[y_true == 1]
        pred_bkg = y_pred[y_true == 0]

        # get the arrays of signal and background weights
        if sample_weight is not None:
            signal_weight = sample_weight[y_true == 1]
            background_weight = sample_weight[y_true == 0]
        else:
            signal_weight = np.ones((y_true[y_true == 1].shape[0],))
            background_weight = np.ones((y_true[y_true == 0].shape[0],))

        # sum up the signal and background weights and add them to the total weights
        total_sum_weights_sig = np.sum(signal_weight)
        total_sum_weights_bkg = np.sum(background_weight)

        # fill the histograms
        s, bins = np.histogram(pred_sig, bins=self.N_bins, weights=signal_weight, range=(0.0, 1.0))
        b, _ = np.histogram(pred_bkg, bins=self.N_bins, weights=background_weight, range=(0.0, 1.0))

        # normalize the histograms to the correct number of events
        s = self.exp_sig / total_sum_weights_sig * s
        b = self.exp_bkg / total_sum_weights_bkg * b

        # perform binning optimization when necessary
        if not (self.min_events_per_bin == 0 and self.min_s_per_bin == 0 and self.min_b_per_bin == 0):
            # go backwards through s and b arrays to create new list for each with potentially fewer bins,
            # so that s+b >= min_events_per_bin, s >= min_s_per_bin and b >= min_b_per_bin in each bin; merge
            # bins when condition is not fulfilled
            bins_opt = [bins[-1]]
            s_opt = [0.0]
            b_opt = [0.0]
            for i in range(s.shape[0] - 1, -1, -1):
                # for last bin (when going from right to left), we always want to add the bin edge and add the events to the bin
                if i == 0:
                    bins_opt.append(bins[i])
                    s_opt[-1] += s[i]
                    b_opt[-1] += b[i]
                # create new bin when previous bin is sufficiently filled
                elif (
                    s_opt[-1] >= self.min_s_per_bin
                    and b_opt[-1] >= self.min_b_per_bin
                    and s_opt[-1] + b_opt[-1] >= self.min_events_per_bin
                ):
                    bins_opt.append(bins[i])
                    s_opt.append(s[i])
                    b_opt.append(b[i])
                # when bin is not yet sufficiently filled, add events to bin without creating new one
                else:
                    s_opt[-1] += s[i]
                    b_opt[-1] += b[i]

            # reverse order back to normal and convert to arrays
            bins_opt.reverse()
            s_opt.reverse()
            b_opt.reverse()
            bins = np.array(bins_opt)
            s = np.array(s_opt)
            b = np.array(b_opt)

        return s, b, bins


class NormHistFigureOfMerit(FigureOfMerit):
    """Subclass of FigureOfMerit that builds normalized histograms of signal and background predictions for histogram FOMs.

    Only applicable to binary classification, i.e. only two classes (signal and background, corresponding to target
    labels 1 and 0, respectively). The total sum of weights for each class is scaled one. A binning optimization is
    performed when minimal number of (normalized) signal, background or total events per bin are given.
    """

    def __init__(
        self,
        func: Callable[..., Any],
        N_bins: int = 100,
        min_events_per_bin: Union[float, int] = 0.0,
        min_s_per_bin: Union[float, int] = 0,
        min_b_per_bin: Union[float, int] = 0.0,
        **kwargs: Any
    ) -> None:
        """_summary_.

        Parameters
        ----------
        func : Callable[..., Any]
            Callable to calculate the value of the figure of merit. Has to accept three numpy arrays (signal and
            background histograms and array of bin edges) and can have additional keyword arguments.
        N_bins : int
            Number of bins of the histogram. If a binning optimization of performed, the initial histograms before
            starting to merge has N_bins bins. (Default value = 100)
        min_events_per_bin : Union[float, int]
            The minimum number of events per bin. During the binning optimization, bins are merged until at least this
            many events are contained in each bin. (Default value = 0.0.)
        min_s_per_bin : Union[float, int]
            The minimum number of signal events per bin. During the binning optimization, bins are merged until at least
            this many signal events are contained in each bin. (Default value = 0)
        min_b_per_bin : Union[float, int]
            The minimum number of background events per bin. During the binning optimization, bins are merged until at
            least this many background events are contained in each bin. Since many FOMs divide by the number of
            background events, this usually should not be set to zero to ensure numerical stability. (Default value = 0.0)
        **kwargs : Any
            Additional keyword arguments of the func.

        Returns
        -------
        None
            _description_
        """
        super(NormHistFigureOfMerit, self).__init__(func, **kwargs)
        self.N_bins = N_bins
        self.min_events_per_bin = min_events_per_bin
        self.min_s_per_bin = min_s_per_bin
        self.min_b_per_bin = min_b_per_bin

    def __call__(self, y_true: np.ndarray, y_pred: np.ndarray, sample_weight: Optional[np.ndarray] = None) -> Any:
        """Calls the preprocess function to build the histograms, gives them to self.func and returns the result.

        Parameters
        ----------
        y_true : np.ndarray
            Array of target labels.
        y_pred : np.ndarray
            Array of predictions corresponding to the target labels.
        sample_weight : Optional[np.ndarray]
            Array of sample weights for each entry in y_true and y_pred. (Default value = None)

        Returns
        -------
        Any
            Value of the figure of merit calculated by self.func.
        """
        s, b, bins = self.preprocess(y_true, y_pred, sample_weight=sample_weight)
        return self.func(s, b, bins, **self.kwargs)

    def preprocess(
        self, y_true: np.ndarray, y_pred: np.ndarray, sample_weight: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Build the histograms of signal and background events from the target labels and predictions.

        Each event is weighted according to the array of sample weights (if provided), each class is normalized to a sum
        of one. If at least one of the minimum (normalized) number of signal, background or total events are not zero, a
        binning optimization is performed. Starting from the rightmost bin, neighboring bins are merged until the
        provided conditions are satisfied.

        Parameters
        ----------
        y_true : np.ndarray
            Array of target labels.
        y_pred : np.ndarray
            Array of predictions corresponding to the target labels.
        sample_weight : Optional[np.ndarray]
            Array of sample weights for each entry in y_true and y_pred. (Default value = None)

        Returns
        -------
        Tuple[np.ndarray, np.ndarray, np.ndarray]
            Normalized, binning optimized histograms of signal and background events and corresponding array of bin edges.
        """
        # reshape the input
        y_true = np.reshape(y_true, y_true.shape[0])
        y_pred = np.reshape(y_pred, y_pred.shape[0])

        # first get the DNN predictions for signal and background
        pred_sig = y_pred[y_true == 1]
        pred_bkg = y_pred[y_true == 0]

        # get the arrays of signal and background weights
        if sample_weight is not None:
            signal_weight = sample_weight[y_true == 1]
            background_weight = sample_weight[y_true == 0]
        else:
            signal_weight = np.ones((y_true[y_true == 1].shape[0],))
            background_weight = np.ones((y_true[y_true == 0].shape[0],))

        # fill the histograms
        s, bins = np.histogram(pred_sig, bins=self.N_bins, weights=signal_weight, range=(0.0, 1.0), density=True)
        b, _ = np.histogram(pred_bkg, bins=self.N_bins, weights=background_weight, range=(0.0, 1.0), density=True)

        # with density=True, the integral over the histogram is normalized to 1, not the sum --> multiply with bin width, then sum == 1
        s *= 1 / self.N_bins
        b *= 1 / self.N_bins

        # perform binning optimization when necessary
        if not (self.min_events_per_bin == 0 and self.min_s_per_bin == 0 and self.min_b_per_bin == 0):
            # go backwards through s and b arrays to create new list for each with potentially fewer bins,
            # so that s+b >= min_events_per_bin, s >= min_s_per_bin and b >= min_b_per_bin in each bin; merge
            # bins when condition is not fulfilled
            bins_opt = [bins[-1]]
            s_opt = [0.0]
            b_opt = [0.0]
            for i in range(s.shape[0] - 1, -1, -1):
                # for last bin (when going from right to left), we always want to add the bin edge and add the events to the bin
                if i == 0:
                    bins_opt.append(bins[i])
                    s_opt[-1] += s[i]
                    b_opt[-1] += b[i]
                # create new bin when previous bin is sufficiently filled
                elif (
                    s_opt[-1] >= self.min_s_per_bin
                    and b_opt[-1] >= self.min_b_per_bin
                    and s_opt[-1] + b_opt[-1] >= self.min_events_per_bin
                ):
                    bins_opt.append(bins[i])
                    s_opt.append(s[i])
                    b_opt.append(b[i])
                # when bin is not yet sufficiently filled, add events to bin without creating new one
                else:
                    s_opt[-1] += s[i]
                    b_opt[-1] += b[i]

            # reverse order back to normal and convert to arrays
            bins_opt.reverse()
            s_opt.reverse()
            b_opt.reverse()
            bins = np.array(bins_opt)
            s = np.array(s_opt)
            b = np.array(b_opt)

        return s, b, bins


def _Chi2Test_(s: np.ndarray, b: np.ndarray, bins: np.ndarray) -> float:
    """Not implemented yet.

    Parameters
    ----------
    s : np.ndarray
        _description_
    b : np.ndarray
        _description_
    bins : np.ndarray
        _description_

    Returns
    -------
    float
        _description_
    """
    raise NotImplementedError


def _NonOverlap_(s: np.ndarray, b: np.ndarray, bins: np.ndarray) -> float:
    """Figure of merit to evaluate the difference between two normalized histograms.

    Defined as 1 - Overlap. The Overlap takes the minimum of s and b in each bin, and calculates the sum of these
    minima. Large values of NO indicate large disagreement, 0 corresponds to identical distributions.

    Parameters
    ----------
    s : np.ndarray
        Normalized 1D histogram of signal events.
    b : np.ndarray
        Normalized 1D histogram of background events.
    bins : np.ndarray
        Unused.

    Returns
    -------
    float
        Value of the Non-Overlap.
    """
    overlap = np.sum(np.abs(np.minimum(s, b)))
    return 1 - overlap


def _Separation_(s: np.ndarray, b: np.ndarray, bins: np.ndarray) -> float:
    """Figure of merit to evaluate the difference between two normalized histograms.

    Calculates the squared difference between s and b, normalized to s+b, in each bin and returns 0.5 * the sum of these
    differences.

    Parameters
    ----------
    s : np.ndarray
        Normalized 1D histogram of signal events.
    b : np.ndarray
        Normalized 1D histogram of background events.
    bins : np.ndarray
        Unused.

    Returns
    -------
    float
        Value of the Separation.
    """
    separation = np.sum((s - b) ** 2 / (np.maximum(1e-7, s + b)))
    return 0.5 * separation


def _SoverSqrtSB_(s: np.ndarray, b: np.ndarray, bins: np.ndarray) -> float:
    """Approximation of the significance, assuming only statistical uncertainties.

    For each bin edge i, the sum of the signal and background events, S and B, for all bins j > i is calculated. The
    maximum value of S / sqrt(S + B) for all tried bin edges is returned.

    Parameters
    ----------
    s : np.ndarray
        1D Histogram of signal events.
    b : np.ndarray
        1D Histogram of background events.
    bins : np.ndarray
        Unused.

    Returns
    -------
    float
        Value of the approximated stat.-only significance.
    """
    s_sum = np.abs(np.array([np.sum(s[i:]) for i in range(s.shape[0])]))
    b_sum = np.abs(np.array([np.sum(b[i:]) for i in range(s.shape[0])]))

    return np.max(s_sum / np.sqrt(np.maximum(1e-7, s_sum + b_sum)))


def _SoverSqrtB_(s: np.ndarray, b: np.ndarray, bins: np.ndarray) -> float:
    """Approximation of the discovery significance, assuming only statistical uncertainties.

    For each bin edge i, the sum of the signal and background events, S and B, for all bins j > i is calculated. The
    maximum value of S / sqrt(B) for all tried bin edges is returned.

    Parameters
    ----------
    s : np.ndarray
        1D Histogram of signal events.
    b : np.ndarray
        1D Histogram of background events.
    bins : np.ndarray
        Unused.

    Returns
    -------
    float
        Value of the approximated stat.-only discovery significance.
    """
    s_sum = np.abs(np.array([np.sum(s[i:]) for i in range(s.shape[0])]))
    b_sum = np.abs(np.array([np.sum(b[i:]) for i in range(s.shape[0])]))

    return np.max(s_sum / np.sqrt(np.maximum(1e-7, b_sum)))


def _SoverSqrtBLastBin_(s: np.ndarray, b: np.ndarray, bins: np.ndarray) -> float:
    """Ratio of S over sqrt(B) in the rightmost bin of the given histograms.

    Parameters
    ----------
    s : np.ndarray
        1D Histogram of signal events.
    b : np.ndarray
        1D Histogram of background events.
    bins : np.ndarray
        Unused.

    Returns
    -------
    float
        S / sqrt(B) for the rightmost bin of the histograms s and b
    """
    return np.abs(s[-1] / np.sqrt(np.maximum(1e-7, b[-1])))


def _SLastBin_(s: np.ndarray, b: np.ndarray, bins: np.ndarray) -> float:
    """Number of signal events in the rightmost bin of the given signal histogram.

    Parameters
    ----------
    s : np.ndarray
        1D Histogram of signal events.
    b : np.ndarray
        Unused
    bins : np.ndarray
        Unused.

    Returns
    -------
    float
        Value of the rightmost bin of the histogram s
    """
    return np.abs(s[-1])


def _BLastBin_(s: np.ndarray, b: np.ndarray, bins: np.ndarray) -> float:
    """Number of background events in the rightmost bin of the given background histogram.

    Parameters
    ----------
    s : np.ndarray
        Unused.
    b : np.ndarray
        1D Histogram of background events.
    bins : np.ndarray
        Unused.

    Returns
    -------
    float
        Value of the rightmost bin of the histogram b
    """
    return np.abs(b[-1])


def _SignificanceSyst_(s: np.ndarray, b: np.ndarray, bins: np.ndarray, syst: float = 0.3) -> float:
    """Approximation of the significance, including systematic uncertainties for the background contribution.

    For each bin edge i, the sum of the signal and background events, S and B, for all bins j > i is calculated. The
    maximum value of S / sqrt(S + B + (syst * B)^2) for all tried bin edges is returned.

    Parameters
    ----------
    s : np.ndarray
        1D Histogram of signal events.
    b : np.ndarray
        1D Histogram of background events.
    bins : np.ndarray
        Unused.
    syst : float
        Controls the assumed systematic uncertainties, e.g. 0.3 corresponds to 30% systematic uncertainty on the
        background. (Default value = 0.3)

    Returns
    -------
    float
        Value of the approximated significance.
    """
    s_sum = np.abs(np.array([np.sum(s[i:]) for i in range(s.shape[0])]))
    b_sum = np.abs(np.array([np.sum(b[i:]) for i in range(s.shape[0])]))

    return np.max(s_sum / np.sqrt(np.maximum(1e-7, s_sum + b_sum + (syst * b_sum) ** 2)))


def _SoBSignificanceSyst_(s: np.ndarray, b: np.ndarray, bins: np.ndarray, syst: float = 0.3) -> float:
    """Approximation of the discovery significance, including systematic uncertainties for the background contribution.

    For each bin edge i, the sum of the signal and background events, S and B, for all bins j > i is calculated. The
    maximum value of S / sqrt(B + (syst * B)^2) for all tried bin edges is returned.

    Parameters
    ----------
    s : np.ndarray
        1D Histogram of signal events.
    b : np.ndarray
        1D Histogram of background events.
    bins : np.ndarray
        Unused.
    syst : float
        Controls the assumed systematic uncertainties, e.g. 0.3 corresponds to 30% systematic uncertainty on the
        background. (Default value = 0.3)

    Returns
    -------
    float
        Value of the approximated discovery significance.
    """
    s_sum = np.abs(np.array([np.sum(s[i:]) for i in range(s.shape[0])]))
    b_sum = np.abs(np.array([np.sum(b[i:]) for i in range(s.shape[0])]))

    return np.max(s_sum / np.sqrt(np.maximum(1e-7, b_sum + (syst * b_sum) ** 2)))


def _PSignificance30_(s: np.ndarray, b: np.ndarray, bins: np.ndarray) -> float:
    """_summary_.

    Parameters
    ----------
    s : np.ndarray
        _description_
    b : np.ndarray
        _description_
    bins : np.ndarray
        _description_

    Returns
    -------
    float
        _description_
    """
    raise NotImplementedError

    # Approximation of exp. significance
    # including a 30% systematic on background
    # Z = S / sqrt(B + (0.3*B)^2)
    # Equation 26
    Nbins = s.GetNbinsX() + 2
    s_bins = [s.GetBinContent(i) for i in range(Nbins)]
    b_bins = [b.GetBinContent(i) for i in range(Nbins)]
    bestSoverSqrtSB = 0

    def Sigma(N, B, dB):
        """_summary_.

        Parameters
        ----------
        N : _type_
            _description_
        B : _type_
            _description_
        dB : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        # from: ATL-COM-GEN-2018-026
        b_hh = 0.5 * (B - dB * dB) + math.sqrt(0.25 * (B - dB * dB) * (B - dB * dB) + N * dB * dB)
        if b_hh < 0:
            print("b_hh = " + str(b_hh))
            return 0
        elif N < 0:
            print("N = " + str(N))
            return 0
        q0 = 2 * (N * (math.log(N) - 1 - math.log(b_hh)) + b_hh) + ((B - b_hh) * (B - b_hh) / dB / dB)
        Z = math.sqrt(abs(q0))
        if q0 < 0:
            Z *= -1
        return Z

    for i in range(Nbins):
        # allow values larger than i:
        bSum_left = abs(sum(b_bins[i:]))
        sSum_left = abs(sum(s_bins[i:]))

        # Changed von 0.3 to 0.3*bSum_left
        if (bSum_left) > 0:
            SoverSqrtSB = Sigma(sSum_left + bSum_left, bSum_left, 0.3 * bSum_left)
            if SoverSqrtSB > bestSoverSqrtSB:
                bestSoverSqrtSB = SoverSqrtSB

        # allow values smaller than i:
        bSum_right = abs(sum(b_bins[:i]))
        sSum_right = abs(sum(s_bins[:i]))

        # Changed von 0.3 to 0.3*bSum_right
        if (bSum_right) > 0:
            SoverSqrtSB = Sigma(sSum_right + bSum_right, bSum_right, 0.3 * bSum_right)
            if SoverSqrtSB > bestSoverSqrtSB:
                bestSoverSqrtSB = SoverSqrtSB

    return bestSoverSqrtSB


def _SumS_(s: np.ndarray, b: np.ndarray, bins: np.ndarray) -> float:
    """Total number of events in the signal histogram (e.g. for debugging).

    Parameters
    ----------
    s : np.ndarray
        1D Histogram of signal events.
    b : np.ndarray
        Unused.
    bins : np.ndarray
        Unused.

    Returns
    -------
    float
        Integral over the signal histogram s.
    """
    return np.sum(s)


def _SumB_(s: np.ndarray, b: np.ndarray, bins: np.ndarray) -> float:
    """Total number of events in the background histogram (e.g. for debugging).

    Parameters
    ----------
    s : np.ndarray
        Unused.
    b : np.ndarray
        1D Histogram of background events.
    bins : np.ndarray
        Unused.

    Returns
    -------
    float
        Integral over the signal histogram s.
    """
    return np.sum(b)


def _LogLikelihoodRatio_(s: np.ndarray, b: np.ndarray, bins: np.ndarray) -> float:
    """The value of -2 * ln(L(mu = 0) / L(hat(mu) = 1)), i.e. the Asimov log-likelihood ratio (only stat. uncertainties).

    Assuming a Poissonian distribution for the number of events in each bin, the Asimov log-likelihood ratio simplifies
    to -2 * sum_{i=1}^N [(S_i + B_i) * ln(B_i / (S_i + B_i)) + S_i].

    Parameters
    ----------
    s : np.ndarray
        1D Histogram of signal events.
    b : np.ndarray
        1D Histogram of background events.
    bins : np.ndarray
        Unused.

    Returns
    -------
    float
        The value of the stat.-only Asimov log-likelihood ratio.
    """
    l_ratio = -2 * np.sum((s + b) * np.log((b + 1e-8) / (s + b + 1e-8)) + s)
    return l_ratio


def _LogLikelihoodRatioPValue_(s: np.ndarray, b: np.ndarray, bins: np.ndarray) -> float:
    """The p-value derived from the stat.-only Asimov log-likelihood ratio.

    According to Wilks' theorem, under certain conditions, the log-likelihood ratio follows a Chi-squared distribution.
    As only a single free parameter exists in this case (signal strength mu), the p-value is derived from a 1D
    Chi2-distribution.

    Parameters
    ----------
    s : np.ndarray
        1D Histogram of signal events.
    b : np.ndarray
        1D Histogram of background events.
    bins : np.ndarray
        Unused.

    Returns
    -------
    float
        The p-value for the stat.-only Asimov log-likelihood ratio, assuming a 1D Chi-squared distribution.
    """
    l_ratio = _LogLikelihoodRatio_(s, b, bins)
    p_value = 1 - stats.chi2.cdf(l_ratio, 1)

    return p_value
