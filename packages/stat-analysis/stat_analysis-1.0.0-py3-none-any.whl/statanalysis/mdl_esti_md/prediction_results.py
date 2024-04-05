import warnings
from dataclasses import dataclass, field

from numpy import array, ndarray, sqrt

from ..hyp_vali_md import (check_coefficients_non_zero, check_hyp_min_sample,
                           check_or_get_alpha_for_hyph_test,
                           check_residuals_centered, check_sample_normality)
from ..utils_md import (RegressionFisherTestData, estimate_std,
                        get_p_value_f_test)
from .prediction_metrics import (PredictionMetrics, compute_aic_bic,
                                 compute_kurtosis, compute_skew)


@dataclass
class RegressionResultData:
    y: ndarray
    y_hat: ndarray
    nb_obs: int
    nb_param: int
    alpha: float
    coeffs: ndarray
    list_coeffs_std: ndarray
    residuals: ndarray = field(init=False)
    residu_std: float = field(init=False)

    def __post_init__(self):
        assert self.y.shape == self.y_hat.shape
        assert self.nb_obs == len(self.y)
        assert self.list_coeffs_std.shape == self.coeffs.shape == (
            self.nb_param, )

        self.alpha = check_or_get_alpha_for_hyph_test(self.alpha)
        self.residuals: ndarray = self.y - self.y_hat
        self.residu_std = estimate_std(self.residuals)


def HPE_REGRESSION_FISHER_TEST(y: list,
                               y_hat: list,
                               nb_param: int,
                               alpha: float = None):
    """check if mean is equal accross many samples

    Args 
        y (list): array-like of 1 dim
        y_hat (list): array-like of 1 dim
        nb_param (int): number of parameter in the regression (include the intercept). ex: for 6 independant variables, nb_params=7
        alpha (float, optional): _description_. Defaults to COMMON_ALPHA_FOR_HYPH_TEST.

    Hypothesis
        H0: β1 = β2 = ... = βk-1 = 0; k=nb_params
        H1: βj ≠ 0, for at least one value of j

    Hypothesis
        - each sample is 
            - simple random 
            - normal
            - indepebdant from others
        - same variance 
            - attention: use levene test (plus robuste que fusher ou bartlett face à la non-normalité de la donnée)(https://fr.wikipedia.org/wiki/Test_de_Bartlett)


    Fisher test 
        - The F Distribution is also called the Snedecor’s F, Fisher’s F or the Fisher–Snedecor distribution
        - [f_oneway - docs.scipy.org/doc](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html)
        - [anova and f test - blog.minitab.com](https://blog.minitab.com/fr/comprendre-lanalyse-de-la-variance-anova-et-le-test-f)
        - [f-test-reg - facweb.cs.depaul.edu/sjost](http://facweb.cs.depaul.edu/sjost/csc423/documents/f-test-reg.htm)

    Returns:
        data: (RegressionFisherTestData)
    """

    alpha = check_or_get_alpha_for_hyph_test(alpha)
    y = array(y, dtype=float)
    y_hat = array(y_hat, dtype=float)
    assert y.ndim == 1
    assert y_hat.ndim == 1
    assert len(y) == len(y_hat)
    n = len(y)
    k = int(nb_param)
    assert nb_param < n
    check_hyp_min_sample(n)

    SSR = ((y_hat - y.mean())**2).sum()  # explained by regression
    SSE = ((y - y_hat)**2).sum()  # SE (like MSE) of the model
    SST = SSE + SSR  # total error = ((y - y.mean())**2).sum()

    dfe = n - k  # error in sample # Degrees of Freedom for Error
    dfr = k - 1  # explained by the diff bewtwenn samples # Corrected Degrees of Freedom for Model
    dft = n - 1  # total # Corrected Degrees of Freedom Total

    MSR = SSR / dfr  # variance explained by the regresser # Mean of Squares for Model
    MSE = SSE / dfe  # variance within sample # Mean of Squares for Error
    # total variance = ( E(X**2) - E(X)**2 )/ (n-1) # Mean of Squares for Error
    MST = SST / dft

    # MSM = SSM / DFM

    R_carre = 1 - SSE / SST  # explained/total # 1-R_carre = SSE/SST
    assert R_carre <= 1 and R_carre >= 0
    R_carre_adj = 1 - MSE / MST  # 1-R_carre = MSE/MST
    if R_carre_adj < 0:
        warnings.warn(
            f"R_adj is negative ({round(R_carre_adj,2)}). your model is bad")
    F = MSR / MSE  # (explained variance) / (unexplained variance)
    # plus F est grand, plus la diff des mean s'explique par la difference entre les groupes
    # plus F est petit, plus la diff des mean s'explique par la variabilite naturelle des samples

    print(f" n = {n}  k = {k}")
    print(f"dfr= k-1 ={dfr}  dfe= n-k = {dfe}  dft= n-1 = {dft}")
    print(f"SSR={SSR} SSE={SSE} SST={SST} ")
    print(f"MSR={MSR} MSE={MSE} MST={MST} ")
    print(f"R_carre={R_carre} R_adj={R_carre_adj} F={F} ")

    # On veut F grand donc on prends un right tail =>

    p_value = get_p_value_f_test(Z=F, dfn=dfr, dfd=dfe)

    # rejection #we want to be far away from the mean (how p_value= how great is (p_hat - p0) = how far p_hat is from p0 considered as mean)
    reject_null = True if p_value < alpha else False
    return RegressionFisherTestData(DFE=dfe,
                                    SSE=SSE,
                                    MSE=MSE,
                                    DFR=dfr,
                                    SSR=SSR,
                                    MSR=MSR,
                                    DFT=dft,
                                    SST=SST,
                                    MST=MST,
                                    R_carre=R_carre,
                                    R_carre_adj=R_carre_adj,
                                    F_stat=F,
                                    p_value=p_value,
                                    reject_null=reject_null)


def compute_linear_regression_results(crd: RegressionResultData,
                                      debug: bool = False):

    debug = bool(debug)
    alpha = crd.alpha

    nb_obs = crd.nb_obs
    nb_param = crd.nb_param

    y = crd.y
    y_hat = crd.y_hat

    residuals = crd.residuals
    residu_std = crd.residu_std

    coeffs = crd.coeffs
    list_coeffs_std = crd.list_coeffs_std

    Testresults = {}

    # test normality of the residuals
    passNormalitytest = check_sample_normality(residuals, alpha=alpha)
    if not passNormalitytest.testPassed:
        if debug:
            print('residuals does not look Gaussian (reject H0)')
    Testresults["residuals_normality"] = passNormalitytest

    # test if mean != 0 for the residuals
    passed_residu_mean_null_test = check_residuals_centered(residuals,
                                                            alpha=alpha)
    if not passed_residu_mean_null_test.testPassed:
        if debug:
            print('residialss does not look centered')
    Testresults["residu_mean_null"] = passed_residu_mean_null_test

    # check if coefficients != 0
    pass_non_zero_test = check_coefficients_non_zero(
        list_coeffs=coeffs,
        list_coeff_std=list_coeffs_std,
        nb_obs=nb_obs,
        alpha=alpha,
        debug=debug)
    if not passNormalitytest.testPassed:
        if debug:
            print('residuals does not look Gaussian (reject H0)')
    Testresults["coeff_non_zero"] = pass_non_zero_test

    # fisher test
    data = HPE_REGRESSION_FISHER_TEST(y=y,
                                      y_hat=y_hat,
                                      nb_param=nb_param,
                                      alpha=alpha)
    DFE, DFR = data.DFE, data.DFR
    SSE, MSE, SSR, MSR, SST, MST = data.SSE, data.MSE, data.SSR, data.MSR, data.SST, data.MST
    R_carre, R_carre_adj, F_stat, p_value = data.R_carre, data.R_carre_adj, data.F_stat, data.p_value
    pass_fisher_test = data.reject_null

    Testresults["significance"] = {
        "R_carre": R_carre,
        "R_carre_adj": R_carre_adj,
        "MSE": MSE,
        "DFE": DFE,
        "MSR": MSR,
        "DFR": DFR,
        "SSE": SSE,
        "SSR": SSR
    }
    Testresults["fisher_test"] = {
        "test_passed": pass_fisher_test,
        "F_stat": F_stat,
        "p_value": p_value
    }

    _metric = PredictionMetrics(y_true=y, y_pred_proba=y_hat, binary=False)

    Testresults["metrics"] = {}
    log_likelihood = _metric.compute_log_likelihood(std_eval=residu_std)
    Testresults["metrics"]["log-likelihood"] = log_likelihood

    aic, bic = compute_aic_bic(dfr=DFR,
                               n=nb_obs,
                               llh=log_likelihood,
                               method="basic")
    Testresults["metrics"]["AIC"] = aic
    Testresults["metrics"]["BIC"] = bic

    # mse, rmse, mae
    Testresults["metrics"]["MSE"] = MSE
    MAE = _metric.compute_mae()
    Testresults["metrics"]["MAE"] = MAE
    RMSE = sqrt(MSE)
    Testresults["metrics"]["RMSE"] = RMSE

    # skew, kurtosis
    Testresults["metrics"]["skew"] = compute_skew(residuals)
    Testresults["metrics"]["kurtosis"] = compute_kurtosis(residuals)

    return Testresults


def compute_logit_regression_results(crd: RegressionResultData,
                                     debug: bool = False):
    """_summary_

    Args:
        crd (RegressionResultData): _description_
        debug (bool, optional): _description_. Defaults to False.
    Info 
    - [understand rs outputs - stats.stackexchange.com](https://stats.stackexchange.com/questions/86351/interpretation-of-rs-output-for-binomial-regression)
    - [pseudo-rcarre - stats.stackexchange.com](https://stats.stackexchange.com/questions/3559/which-pseudo-r2-measure-is-the-one-to-report-for-logistic-regression-cox-s)
    Returns:
        _type_: _description_
    """

    debug = bool(debug)
    alpha = crd.alpha

    nb_obs = crd.nb_obs
    nb_param = crd.nb_param

    y = crd.y
    y_hat = crd.y_hat

    residuals = crd.residuals
    residu_std = crd.residu_std

    coeffs = crd.coeffs
    list_coeffs_std = crd.list_coeffs_std

    Testresults = {}

    # check if coefficients != 0
    pass_non_zero_test = check_coefficients_non_zero(
        list_coeffs=coeffs,
        list_coeff_std=list_coeffs_std,
        nb_obs=nb_obs,
        alpha=alpha,
        debug=debug)
    Testresults["coeff_non_zero"] = pass_non_zero_test

    _metric = PredictionMetrics(y_true=y, y_pred_proba=y_hat, binary=True)

    Testresults["metrics"] = {}
    log_likelihood = _metric.compute_log_likelihood(std_eval=residu_std)
    Testresults["metrics"]["log-likelihood"] = log_likelihood
    Testresults["metrics"]["log-loss"] = _metric.log_loss()

    Testresults["metrics"]["confusion"] = _metric.get_confusion_matrix()
    Testresults["metrics"]["accuracy"] = _metric.get_binary_accuracy()
    Testresults["metrics"]["precision"] = _metric.get_precision_score()
    Testresults["metrics"]["recall"] = _metric.get_recall_score()
    Testresults["metrics"]["f1"] = _metric.get_f1_score()
    # Testresults["roc"] =

    return Testresults
