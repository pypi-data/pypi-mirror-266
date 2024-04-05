'''
les test de valisation (hypothese avant de lancer un autre test) qui dependant de test que j'ai écrits moi-même
Les mettre dans utils prut créer un import circulaire
'''


import warnings

from numpy import array

from ..hyp_testi_md import HP_MEAN_MANY, HP_MEAN_ONE, HPE_FROM_P_VALUE
from ..utils_md import HypothesisValidationData, Tails
from .constraints import (check_equal_var, check_or_get_alpha_for_hyph_test,
                          check_sample_normality, check_zero_to_one_constraint)


def check_residuals_centered(residuals: list, alpha=None):
    """check if a list is centered (if the mean ==0 nuder a significance od 0.05)

    Args:
        residuals (list): list or array-like

    Returns:
        _type_: _description_
    """
    check_zero_to_one_constraint(alpha)
    residuals = array(residuals).flatten()
    data = HP_MEAN_ONE(p0=0,
                       alpha=alpha,
                       sample=residuals,
                       symb=Tails.NEQ_SYMB)
    passed_residu_mean_null_test = not data.reject_null  # H0:p=p0, H1:p!=p0
    return HypothesisValidationData(passed_residu_mean_null_test)


def check_coefficients_non_zero(list_coeffs: list,
                                list_coeff_std: list,
                                nb_obs: int,
                                debug=False,
                                alpha=None):
    """compute non zero tests for each corfficien
    - test 
        - for ech coefficient
            - H0: coeff==0
            - H1: coeff!=0
            - if the test passed (H0 is rejected), the coefficient is away from 0, return = True

    Args:
        list_coeffs (list): lists of values
        list_coeff_std (list): list of std; the two lists should have the same lenght

    Returns:
        - HypothesisValidationData(pass_non_zero_test_bool,pass_non_zero_test)
            - testPassed (bool)
            - obj (list) list of boolean (For each value, True if H0 is reected)
    """
    alpha = check_or_get_alpha_for_hyph_test(alpha)
    list_coeffs = array(list_coeffs).flatten()
    list_coeff_std = array(list_coeff_std).flatten()
    assert len(list_coeffs) == len(list_coeff_std)
    nb_obs = int(nb_obs)
    ddl = nb_obs - 1

    pass_non_zero_test = []
    for coeff_, se_ in zip(list_coeffs, list_coeff_std):
        # test statistic: H0:coeff=0; H1:coeff!=0
        assert isinstance(coeff_, float)
        assert isinstance(se_, float)
        # compute p_value
        data = HPE_FROM_P_VALUE(p_hat=coeff_,
                                p0=0,
                                std_stat_eval=se_,
                                tail=Tails.middle,
                                onetail=True,
                                alpha=alpha,
                                test="t_test",
                                ddl=ddl)
        pass_non_zero_test.append(data.reject_null)
        if debug:
            print(
                f"check_coefficients_non_zero: Z={data.Z} p_val={data.p_value}"
            )

    pass_non_zero_test_bool = not (False in pass_non_zero_test)

    return HypothesisValidationData(pass_non_zero_test_bool,
                                    pass_non_zero_test)


def check_equal_mean(*samples, alpha=None):
    """check if mean if the same accross samples

    Hypothesis
        H0: mean1 = mean2 = mean3 = ....
        H1: one is different

    Hypothesis
        - The samples are independent.
        - Each sample is from a normally distributed population.
        - The population standard deviations of the groups are all equal. This property is known as homoscedasticity.

    Args:
        - *samples (list): one or many lists 

    Fisher test 
        - The F Distribution is also called the Snedecor’s F, Fisher’s F or the Fisher–Snedecor distribution [1](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html) [2](https://blog.minitab.com/fr/comprendre-lanalyse-de-la-variance-anova-et-le-test-f)

    Returns:
        stat: (float) F
        p_value: (float)
    """
    alpha = check_or_get_alpha_for_hyph_test(alpha)
    for elt in samples:
        assert len(elt) > 0

    # check same_variance hypothesis
    # if not check_equal_variance()
    if not check_equal_var(*samples, alpha=alpha).testPassed:
        warnings.warn("data seems to not have equal variance")

    # check normality hypothesis
    for sample in samples:
        if not check_sample_normality(sample, alpha=alpha).testPassed:
            warnings.warn("data seems to not be normal")

    data = HP_MEAN_MANY(samples, alpha=alpha)
    # tail=right donc reject_null => p_value faible => stat grand => F (=MSR/MSE) grand => la variance vient de la diff entre les groupe et non de la variance interne de groupes => les groups sont significativement differents
    equal_mean = not data.reject_null

    return HypothesisValidationData(equal_mean, {
        "Z": data.Z,
        "p_value": data.p_value,
        "reject_null": data.reject_null
    })
