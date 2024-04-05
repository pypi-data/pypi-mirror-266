
from numpy import array
from scipy.stats import anderson, levene, normaltest, shapiro

from ..utils_md import (COMMON_ALPHA_FOR_HYPH_TEST,
                        COMMON_COVERAGE_PROBABILITY_FOR_CONF_INT,
                        LIM_MIN_SAMPLE, HypothesisValidationData)


def check_zero_to_one_constraint(*args):
    for arg in args:
        arg = float(arg)
        if arg < 0 or arg > 1:
            raise Exception(f"zero_to_one_constraint failed. get arg = {arg}")


def check_or_get_alpha_for_hyph_test(alpha=None):
    if alpha:
        alpha = float(alpha)
    else:
        alpha = COMMON_ALPHA_FOR_HYPH_TEST
    check_zero_to_one_constraint(alpha)
    return alpha


def check_or_get_cf_for_conf_inte(confidence=None):
    if confidence:
        confidence = float(confidence)
    else:
        confidence = COMMON_COVERAGE_PROBABILITY_FOR_CONF_INT
    check_zero_to_one_constraint(confidence)
    return confidence


def check_hyp_min_sample(n: int, p: int = None):
    n = int(n)

    def exc(st, nb):
        return Exception(
            f"pb: {st} should be at least {LIM_MIN_SAMPLE}. Instead, found {nb}\nNote that there are several ways to bypass this"
        )

    if p == None:
        if n < LIM_MIN_SAMPLE:
            raise exc("n", n)
    if p != None:
        p = int(p)
        if n * p < LIM_MIN_SAMPLE:
            exc("n*p", n * p)
        if n * (1 - p) < LIM_MIN_SAMPLE:
            exc("n*(1-p)", n * (1 - p))


def check_hyp_min_samples(p1: float,
                          p2: float,
                          n1: int,
                          n2: int,
                          overall=False):
    if overall:
        p1 = p2 = (p1 + p2) / (n1 + n2)
    check_hyp_min_sample(n1, p1)
    check_hyp_min_sample(n2, p2)


def check_sample_normality(residuals: list, debug=False, alpha=None):
    """check if residuals is like a normal distribution
    - test_implemented


    Args:
        residuals (list): list of float or array-like (will be flatten)
        debug (bool, optional): _description_. Defaults to False.

    Returns:
        bool: if all tests passed
    """
    alpha = check_or_get_alpha_for_hyph_test(alpha)
    residuals = array(residuals).flatten()
    # check normality of residuals
    # if True, Sample looks Gaussian (fail to reject H0)'
    passNormalitytest = True

    stat1, p_1 = normaltest(residuals)
    cdt = p_1 > alpha
    passNormalitytest = cdt and passNormalitytest
    if debug:
        printf("normal:", cdt)

    stat2, p_2 = shapiro(residuals)
    cdt = p_2 > alpha
    passNormalitytest = cdt and passNormalitytest
    if debug:
        printf("shapiro:", cdt)

    result = anderson(residuals)
    cdt = result.statistic < min(result.significance_level)
    passNormalitytest = cdt and passNormalitytest
    if debug:
        printf("anderson:", cdt)

    return HypothesisValidationData(passNormalitytest)


def check_equal_var(*samples, alpha=COMMON_ALPHA_FOR_HYPH_TEST):
    """_summary_

    Args:
        alpha (_type_, optional): _description_. Defaults to COMMON_ALPHA_FOR_HYPH_TEST.
    Utils 
    - use levene test [plus robuste que fisher ou bartlett face à la non-normalité de la donnée](https://fr.wikipedia.org/wiki/Test_de_Bartlett)

    Returns:
        _type_: _description_
    """
    # if not check_equal_variance()
    # H0: variances are all the same
    stat, p = levene(*samples, proportiontocut=alpha)
    cdt = p > alpha  # but I want i test to state H0: one is different
    pass_equal_var_test = cdt
    return HypothesisValidationData(pass_equal_var_test)


if __name__ == "__main__":
    pass
else:
    printf = print
    print = lambda *args: ""
