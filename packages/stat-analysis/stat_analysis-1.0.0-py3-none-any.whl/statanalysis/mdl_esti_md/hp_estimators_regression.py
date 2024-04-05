'''
todo
- refactor output (last lines)
- use "alternative" instead of "tail"
- use kwargs format while calling functions
- reorder fcts attributes
- Que signifie le R au carré négatif?: 
    - selon ma def, c'est  entre 0 et 1 à cause d'une somme mais c'est faux ?? [qastack.fr](https://qastack.fr/stats/183265/what-does-negative-r-squared-mean)
'''


from numpy import (abs, array, diag, dot, exp, hstack, log, ndarray, ones,
                   random, sqrt, zeros)
from scipy.linalg import det, inv

from ..hyp_vali_md import check_or_get_alpha_for_hyph_test
from ..utils_md import estimate_std
from .prediction_metrics import PredictionMetrics
from .prediction_results import (RegressionResultData,
                                 compute_linear_regression_results,
                                 compute_logit_regression_results)

SUM = sum
sum_loc = sum
random.seed(233)


def sigmoid(z):
    return 1 / (1 + exp(-z))


def log_loss(yp, y):
    # this is the loss function which we use to minimize the error of our model
    # _f = vectorize(lambda x: min(max(x, 0.005), 1-0.005))
    # yp = _f(y)
    return (-y * log(yp) - (1 - y) * log(1 - yp)).mean()


def log_loss(yp, y):
    assert ((yp < 0)).sum() == 0, "0 to 1 constraint failed"
    assert ((y < 0)).sum() == 0, "0 to 1 constraint failed"
    y[y == 0] = min(min(y[y != 0]), 10**(-12))
    yp[yp == 0] = min(min(yp[yp != 0]), 10**(-12))
    return -(y * log(yp) + (1 - y) * log(1 - yp)).mean()


def log_loss(yp, y, min_tol: float = None):
    assert ((yp < 0) + (yp > 1)).sum() == 0, "0 to 1 constraint failed"
    assert ((y < 0) + (yp > 1)).sum() == 0, "0 to 1 constraint failed"
    if min_tol is not None:
        min_tol = float(min_tol) if min_tol != True else 10**(-12)
        assert 0 < min_tol < 0.1
        if len(yp[yp > 0]):
            yp[yp <= 0] = min(min(yp[yp > 0]), min_tol)
        if len(yp[yp >= 1]):
            yp[yp >= 1] = max(max(yp[yp < 1]), 1 - min_tol)
    return -(y * log(yp) + (1 - y) * log(1 - yp)).mean()


class ComputeRegression:

    def __init__(self,
                 logit=False,
                 fit_intercept=True,
                 alpha=None,
                 debug=False) -> None:
        self.fit_intercept = bool(fit_intercept)
        self.alpha = check_or_get_alpha_for_hyph_test(alpha)
        self.debug = bool(debug)
        self.logit = bool(logit)
        self.W = None

    def _add_intercept(self, X):
        assert X.ndim == 2
        return X if not self.fit_intercept else hstack((ones(
            (X.shape[0], 1)), X))

    def _set_X_y(self, X, y):
        # verifications
        X = array(X)
        y = array(y)
        assert X.ndim == 2
        n, nb_param = X.shape
        assert y.shape == (n, )

        if self.logit:
            assert set(y) == {0,
                              1}, f"found set(y)=={set(y)} instead od {[0,1]}"

        # add slope to X
        X = self._add_intercept(X)
        if self.fit_intercept:
            nb_param = nb_param + 1
        assert X.shape == (n, nb_param)

        # set data
        self.X = X
        self.y = y
        self.nb_param = nb_param
        self.nb_obs = n

    def _sigmoid(self, z):
        return 1 / (1 + exp(-z))

    def _pred_target(self, X):
        """apply sigmoid and return proba

        Args:
            X (_type_): _description_

        Returns:
            _type_: _description_
        """
        assert X.shape[1] == self.X.shape[1]
        y_pred = dot(X, self.W)
        if self.logit:
            y_pred = self._sigmoid(y_pred)
        return y_pred

    def count_nan_and_inf(self, arr):
        import numpy as np
        return (arr == np.inf).sum() + (arr == np.nan).sum()

    def _estimate_log_reg_coeff_std(self):
        """_summary_

        Info 
        - cool: [web.stanford.edu](https://web.stanford.edu/class/archive/stats/stats200/stats200.1172/Lecture26.pdf)
        - another(not used): [stats.stackexchange.com](https://stats.stackexchange.com/questions/60723/bias-of-maximum-likelihood-estimators-for-logistic-regression)

        Returns:
            _type_: _description_
        """
        # compute #
        assert self.count_nan_and_inf(self.W) == 0
        assert self.count_nan_and_inf(self.X) == 0
        temp = self.X @ self.W
        assert self.count_nan_and_inf(temp) == 0, "temp1 contains inf or nan."
        temp = exp(temp)
        assert temp.shape == (self.nb_obs, )
        assert self.count_nan_and_inf(
            temp) == 0, "temp2 contains inf or nan. please add a normalisation"
        WT = temp / (1 + temp)**2
        assert WT.shape == (self.nb_obs, )
        assert self.count_nan_and_inf(WT) == 0, "WT contains inf or nan."
        WT = diag(WT)
        assert WT.shape == (self.nb_obs, self.nb_obs)
        b1 = self.X.T @ WT @ self.X
        assert b1.shape == (
            self.nb_param, self.nb_param
        ), f"found {b1.shape} instead of {(self.nb_param, self.nb_param)}"
        assert self.count_nan_and_inf(b1) == 0, "b1 contains inf or nan."
        b1 = inv(b1)
        return sqrt(diag(b1))

    def _estimate_logit_reg_coeffs(self,
                                   num_iterations: int = None,
                                   learning_rate: float = None,
                                   verbose: bool = True):
        """
        some documentation: 
        - [implementation - github.com/susanli2016 - ipynb](https://github.com/susanli2016/Machine-Learning-with-Python/blob/master/Logistic%20Regression%20in%20Python%20-%20Step%20by%20Step.ipynb)
        - [implementation - github.com/aihubprojects - ipynb](https://github.com/aihubprojects/Logistic-Regression-From-Scratch-Python/blob/master/LogisticRegressionImplementation.ipynb)
        - [MLE - arunaddagatla.medium.com](https://arunaddagatla.medium.com/maximum-likelihood-estimation-in-logistic-regression-f86ff1627b67)
        - [R2 interpretation - stats.stackexchange.com](https://stats.stackexchange.com/questions/82105/mcfaddens-pseudo-r2-interpretation)
        - [biais in logistic regression - stats.stackexchange](https://stats.stackexchange.com/questions/113766/omitted-variable-bias-in-logistic-regression-vs-omitted-variable-bias-in-ordina)
        """
        if learning_rate is None:
            learning_rate = 0.01
        if num_iterations is None:
            num_iterations = 100
        num_iterations = int(num_iterations)
        learning_rate = float(learning_rate)
        assert 0 < learning_rate < 1
        assert 1 < num_iterations

        assert len(set(self.y)) == 2
        assert set(self.y) == {0, 1}
        # weights initialization of our Normal Vector, initially we set it to 0, then we learn it eventually
        self.W = zeros(self.X.shape[1])
        yp = self._pred_target(self.X)
        # this for loop runs for the number of iterations provided
        _list_fct = {
            "loss": PredictionMetrics.log_loss,
            "acc": PredictionMetrics.get_binary_accuracy,
            "f1": PredictionMetrics.get_f1_score,
            "prec": PredictionMetrics.get_precision_score,
            "rec": PredictionMetrics.get_recall_score
        }
        self.hist = {_mt: [] for _mt in _list_fct}
        for i in range(num_iterations):
            # gradient
            grad = dot(
                self.X.T, (yp - self.y)
            ) / self.y.size  # https://arunaddagatla.medium.com/maximum-likelihood-estimation-in-logistic-regression-f86ff1627b67
            # optimize
            self.W -= learning_rate * grad
            # prediction
            yp = self._pred_target(self.X)
            # loss
            # loss = log_loss(yp, self.y, min_tol=True)
            pm = PredictionMetrics(y_true=self.y, y_pred_proba=yp, binary=True)
            for _mt in _list_fct:
                self.hist[_mt].append(_list_fct[_mt](pm))
            if (verbose == True and i % 10000 == 0):
                _str = " ".join([
                    f"{_mt}: {round(self.hist[_mt][-1],5)}"
                    for _mt in _list_fct
                ])
                print(f'{round(100*i/num_iterations)}% {_str} \t')

        list_coeffs_std = self._estimate_log_reg_coeff_std()

        return list_coeffs_std, self.W

    def _estimate_lin_reg_coeffs(self):
        # estimate coefficients
        b1 = dot(self.X.T, self.X)
        assert b1.shape == (self.nb_param, self.nb_param)
        if det(b1) == 0:
            raise Exception("det==0")
        b1 = inv(b1)
        b2 = dot(self.X.T, self.y)
        self.W = dot(b1, b2)
        assert self.W.shape == (self.nb_param, )

        # compute residuals
        y_hat = self._pred_target(self.X)  # y = y_hat + e
        residuals = self.y - y_hat
        assert residuals.shape == (self.nb_obs, )

        # compute standard error of the estimators
        # estimate standard deviation of the residual
        residu_std = estimate_std(residuals)  # e fl-> N(0,s**2)
        # estimate standard deviation of the coefficients
        # matrice de variance-covariance #les rzcine carre les elt diagonaux donnent les std
        list_coeffs_std = residu_std * sqrt(diag(b1))
        assert list_coeffs_std.shape == (self.nb_param, )
        return list_coeffs_std, self.W

    def _set_coeffs_(self, W, list_coeffs_std):
        # verifications
        assert W.shape == (self.nb_param, )
        assert list_coeffs_std.shape == (self.nb_param, )

        # set data
        self.list_coeffs_std = list_coeffs_std
        self.W = W

    def _estimate_coeffs(self,
                         nb_iter: float = None,
                         learning_rate: float = None):

        list_coeffs_std, W = self._estimate_logit_reg_coeffs(
            num_iterations=nb_iter, learning_rate=learning_rate
        ) if self.logit else self._estimate_lin_reg_coeffs()

        self._set_coeffs_(W, list_coeffs_std)

    def _compute_test_results(self):
        # compute target
        y_hat = self._pred_target(self.X)
        # if self.logit: y_hat = (y_hat>0.5).astype('int')
        # assert set(y_hat)=={0,1}, f"found set(y_hat)={set(y_hat)}. maybe there are not enough iterations"
        # store necessery
        self.regression_result_data = RegressionResultData(
            y=self.y,
            y_hat=y_hat,
            nb_obs=self.nb_obs,
            nb_param=self.nb_param,
            alpha=self.alpha,
            coeffs=self.W,
            list_coeffs_std=self.list_coeffs_std)
        # compute tests
        self.Testresults = compute_logit_regression_results(
            crd=self.regression_result_data, debug=self.debug
        ) if self.logit else compute_linear_regression_results(
            crd=self.regression_result_data, debug=self.debug)

    def fit(self, X, y, nb_iter: float = None, learning_rate: float = None):
        """_summary_

        Args:
            X (2-dim array): list of columns (including slope) (n,nb_params)
            y (1-dim array): observations (n,)
            alpha (_type_, optional): _description_. Defaults to None.
            debug (bool, optional): _description_. Defaults to False.

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """

        self._set_X_y(X=X, y=y)

        self._estimate_coeffs(nb_iter=nb_iter, learning_rate=learning_rate)

        self._compute_test_results()

    def get_regression_results(self):
        crd: RegressionResultData = self.regression_result_data
        return crd.coeffs, crd.list_coeffs_std, crd.residu_std, self.Testresults

    def predict_proba(self, X_test: ndarray):
        assert X_test.ndim == 2
        X_test = self._add_intercept(X_test)
        assert X_test.shape[
            1] == self.nb_param, f"X_test.shape[1]:{X_test.shape[1]} vs nb_param:{self.nb_param}"
        return self._pred_target(X=X_test)

    def predict(self, X_test: ndarray, lim=0.5):
        lim = float(lim)
        assert 0 < lim < 1
        y_pred = self.predict_proba(X_test=X_test)
        return (y_pred > lim).astype('int')

    '''def predict(self, X_test:ndarray, lim=0.5):
        lim = float(lim)
        assert 0<lim<1
        y_pred = self.predict_proba(X_test=X_test)
        return (y_pred>lim).astype('int')
    '''


if __name__ == "__main__":
    pass
else:
    pass  # print = lambda *args: ""
