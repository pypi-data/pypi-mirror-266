import math
import warnings

from numpy import abs, array, log, sqrt

from ..utils_md import estimate_std


def compute_skew(arr):
    """_summary_

    Args:
        y (_type_): _description_

    Utils
    - [skewness and kurtosis - spcforexcel.com](https://www.spcforexcel.com/knowledge/basic-statistics/are-skewness-and-kurtosis-useful-statistics)
    - [skewness - thoughtco.com](https://www.thoughtco.com/what-is-skewness-in-statistics-3126242)

    Returns:
        _type_: _description_
    """
    arr = array(arr).flatten()
    n = arr.size
    const = n * sqrt(n - 1) / (n - 2)
    y_m = arr.mean()
    num = ((arr - y_m)**3).sum()
    den = (((arr - y_m)**2).sum())**(3 / 2)
    return const * num / den


def compute_kurtosis(arr, residuals=None):
    """_summary_

    Args:
        y (list|array-like): _description_

    Utils
    - [kurtosis and skewness - spcforexcel.com](https://www.spcforexcel.com/knowledge/basic-statistics/are-skewness-and-kurtosis-useful-statistics)

    Returns:
        _type_: _description_
    """
    arr = array(arr).flatten()
    n = arr.size
    const = (n - 1) * n * (n + 1) / ((n - 2) * (n - 3))
    y_m = arr.mean()
    num = ((arr - y_m)**4).sum()
    den = (((arr - y_m)**2).sum())**(4 / 2)
    assert num.shape == ()
    assert den.shape == ()
    assert y_m.shape == ()
    const2 = 3 * ((n - 1)**2) / ((n - 2) * (n - 3))
    return (const * num / den) - const2


def compute_aic_bic(dfr: int, n: int, llh: float, method: str = "basic"):
    """_summary_

    Utils
        - It adds a penalty that increases the error when including additional terms. The lower the AIC, the better the model.
        - [aic and bic in python - medium.com/analytics-vidhya](https://medium.com/analytics-vidhya/probabilistic-model-selection-with-aic-bic-in-python-f8471d6add32)

    Args:
        dfr (int): nb_predictors(not including the intercept)
        dfe (int): nb of observations
        llh (float): log likelihood

    Question
        what about mixed models ?

    Returns:
        float: aicself, y_true, y_pred
    """
    K = dfr  # number of independent variables to build model==nb_predictors(not including the intercept)
    m1, m2 = 2, log(n)
    aic = m1 * K - 2 * llh
    bic = m2 * K - 2 * llh

    if method == "basic":
        return aic + m1, bic + m2
    elif method == "log":
        return aic, bic
    elif method == "correct":
        return aic + 2 * K * (K + 1) / (n - 1 - K), bic


class PredictionMetrics:

    def __init__(self, y_true: list, y_pred_proba: list, binary: bool) -> None:
        self.y_true = y_true
        self.y_pred = y_pred_proba
        assert self.y_true.ndim == 1
        assert self.y_pred.ndim == 1
        assert self.y_true.shape == self.y_pred.shape
        self.binary = bool(binary)
        if binary:
            assert ((self.y_pred < 0) +
                    (self.y_pred > 1)).sum() == 0, "0 to 1 constraint failed"
            assert ((self.y_true < 0) +
                    (self.y_true > 1)).sum() == 0, "0 to 1 constraint failed"
            self.y_true_bin = (self.y_true > 0.5).astype('int')
            self.y_pred_bin = (self.y_pred > 0.5).astype('int')
            if len(set(self.y_true_bin)) != 2:
                warnings.warn(f"found {set(self.y_true_bin)} in y_true_bin")
            if len(set(self.y_pred_bin)) != 2:
                warnings.warn(f"found {set(self.y_pred_bin)} in y_pred_bin")
            assert len(
                set(self.y_pred)
            ) > 2, f"found len(set(y_pred_proba)) = {len(set(self.y_pred))}. y_pred_proba = {set(self.y_pred)} may be the predictions. Please send y_pred_proba as probabilities (continuous values between 0 and 1"
            self.confusion_matrix = None

    def compute_mae(self):
        y = array(self.y_true)
        y_pred = array(self.y_pred)
        assert y.shape == y_pred.shape
        return abs(y - y_pred).mean()

    def compute_log_likelihood(self,
                               std_eval: float = None,
                               debug=False,
                               min_tol: float = True):
        """_summary_

        Args:
            std_eval (float, optional): (ignored if self.binary=True). Defaults to None.
            debug (bool, optional): _description_. Defaults to False.
            min_tol (float, optional): (ignored if self.binary=False). Defaults to None.

        Returns:
            _type_: _description_
        """
        if self.binary:
            return self._log_likelihood_logit(min_tol=min_tol)
        else:
            if std_eval is None:
                std_eval = estimate_std(self.y_true - self.y_pred)
            return self._log_likelihood_lin_reg(std_eval=std_eval, debug=debug)

    def _log_likelihood_lin_reg(self, std_eval: float, debug=False):
        """_summary_

        Args:
            y (list): _description_
            self.y_pred (list): _description_
            std_eval (float): _description_
            debug (bool, optional): _description_. Defaults to False.
        Utils
            - [mle regression - cs.princeton.edu - pdf](https://www.cs.princeton.edu/courses/archive/fall18/cos324/files/mle-regression.pdf)
        Returns:
            log_likelihood: _description_
        """
        assert self.binary == False
        y = self.y_true
        y_pred = self.y_pred
        y = array(y, dtype=float)
        y_pred = array(y_pred, dtype=float)
        sigma = float(std_eval)
        assert y.ndim == 1
        assert y_pred.ndim == 1
        assert len(y) == len(y_pred)
        n = len(y)
        sigma_carre = sigma**2
        CST = math.log(2 * math.pi * sigma_carre)
        SST = ((y - y_pred)**2).sum()
        log_likelihood = -(n / 2) * CST - SST / (2 * sigma_carre)
        return log_likelihood

    def log_loss_flat(self, min_tol: float = None):
        assert self.binary == True
        y = self.y_true
        yp = self.y_pred
        assert ((yp < 0) + (yp > 1)).sum() == 0, "0 to 1 constraint failed"
        assert ((y < 0) + (yp > 1)).sum() == 0, "0 to 1 constraint failed"
        yp1 = yp.copy()
        yp2 = yp.copy()
        if min_tol is not None:
            min_tol = float(min_tol) if min_tol != True else 10**(
                -12)  # si c'est plus petit, ce sera trop petit pour log
            assert 0 < min_tol < 0.1
            yp1[yp <= 0] = min(min(yp[yp > 0]), min_tol) if len(
                yp[yp > 0]) else min_tol
            yp2[yp >= 1] = max(max(yp[yp < 1]), 1 -
                               min_tol) if len(yp[yp < 1]) else 1 - min_tol
        return (y * log(yp1) + (1 - y) * log(1 - yp2))

    def _log_likelihood_logit(self, min_tol: float = True):
        return self.log_loss_flat(min_tol=min_tol).sum()

    def log_loss(self, min_tol: float = True):
        return -self.log_loss_flat(min_tol=min_tol).mean()

    def get_confusion_matrix(self):
        assert self.binary == True
        if self.confusion_matrix is not None:
            return self.confusion_matrix
        _pred_neg = self.y_pred_bin[self.y_true_bin == 0]
        _pred_pos = self.y_pred_bin[self.y_true_bin == 1]
        tn, fp, fn, tp = (_pred_neg == 0).sum(), (_pred_pos == 0).sum(), (
            _pred_neg == 1).sum(), (_pred_pos == 1).sum()
        self.confusion_matrix = [[tn, fp], [fn, tp]]
        return self.confusion_matrix

    def get_binary_accuracy(self):
        assert self.binary == True
        # return abs(self.y_true_bin==self.y_pred_bin).sum()/len(self.y_true_bin)
        (tn, fp), (fn, tp) = self.get_confusion_matrix()
        return (tp + tn) / (tp + tn + fp + fn)

    def get_precision_score(self):
        assert self.binary == True
        (tn, fp), (fn, tp) = self.get_confusion_matrix()
        return tp / (tp + fp)

    def get_recall_score(self):
        assert self.binary == True
        (tn, fp), (fn, tp) = self.get_confusion_matrix()
        return tp / (tp + fn)

    def get_f1_score(self):
        assert self.binary == True
        prec = self.get_precision_score()
        rec = self.get_recall_score()
        return 2 * (prec * rec) / (prec + rec)

    def get_binary_regression_res(self):
        assert self.binary == True
        dd = {}
        dd["acc"] = self.get_binary_accuracy()
        dd["rec"] = self.get_recall_score()
        dd["prec"] = self.get_precision_score()
        dd["conf"] = self.get_confusion_matrix()
        dd["log-likelihood"] = self.compute_log_likelihood()
        dd["log-loss"] = self.log_loss()
        return dd
