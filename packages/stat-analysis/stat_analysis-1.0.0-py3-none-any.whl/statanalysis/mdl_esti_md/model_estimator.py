'''
We know why t-student is useful
what about khi-2 ? we know 
fisher ? yes F

- add a fct to predict 
    - attention to extrapolation (unsern data) vs interpolation
- another for the curve showing the std
    - the interval should be narrower tinyer when X reacg the sample mean
- a good list of intel/reminder about the regression [here - sites.ualberta.ca - pdf](https://sites.ualberta.ca/~lkgray/uploads/7/3/6/2/7362679/slides_-_multiplelinearregressionaic.pdf)
    
'''


from numpy import array, power, random

from ..conf_inte_md import IC_MEAN_ONE
from ..hyp_vali_md import (check_hyp_min_sample,
                           check_or_get_alpha_for_hyph_test,
                           check_sample_normality)
from ..utils_md import clear_list, clear_list_pair, clear_mat_vec, estimate_std
from .hp_estimators_regression import ComputeRegression

sum_loc = sum
random.seed(133)


def ME_Normal_dist(sample: list, alpha=None, debug=False):
    '''
    estimate a normal distribution from a sample

    visualisation: 
    - check if normal: 
        - sns.distplot(data.X)
        - check if qq-plot is linear [en.wikipedia.org](https://en.wikipedia.org/wiki/Q%E2%80%93Q_plot)
            ::from statsmodels.graphics.gofplots import qqplot 
            ::from matplotlib import pyplot
            ::qqplot(sample, line='s')
            ::pyplot.show()

    hypothesis 
    - X = m + N(0,s**2)

    - check normal hypothesis: [machinelearningmastery](https://machinelearningmastery.com/a-gentle-introduction-to-normality-tests-in-python/)

    lenght 
    - you may need data over 1000 samples to get
    '''
    alpha = check_or_get_alpha_for_hyph_test(alpha)
    n = len(sample)
    check_hyp_min_sample(n)
    sample = clear_list(sample)

    # estimate mean
    # m = mean(sample) #estimate of the overall (marginal) mean
    data = IC_MEAN_ONE(confidence=0.95, sample=sample)
    m = data.parameter
    std_estimator = data.marginOfError

    # estimate std
    s = estimate_std(sample)  # e fl-> N(0,s**2)

    # check normality of residuals
    residuals = array(sample) - m
    passNormalitytest = check_sample_normality(residuals,
                                               alpha=alpha,
                                               debug=debug)

    if not passNormalitytest.testPassed:
        print('residuals does not look Gaussian (reject H0)')

    Testresults = {"residuals_normality": passNormalitytest}

    _others = {}
    return m, std_estimator, s, Testresults, _others


def ME_Regression(x: list,
                  y: list,
                  degre: int,
                  logit=False,
                  fit_intercept=True,
                  debug=False,
                  alpha: float = 0.05,
                  nb_iter: int = 100000,
                  learning_rate: float = 0.1):
    '''
    estimate a regression model from two samples

    prediction
    - predict Y conditional on X assuming that Y = pr[0] + pr[1]*X + pr[2]*X^2 + pr[3]*X^3 + N(0,s**2)
    - Y is a dependant variable
    - x, s are independant ones => predictors of the dependant variables
    - If there is a time stamp of measures (or paired data), please add them as independant variables pr[0] + var_exp_1*G + 


    visualisation: 
    - sns.scatterplot(X,Y) 

    hypothesis 
    - Y = pr[0] + pr[1]*X + pr[2]*X^2 + pr[3]*X^3 + err 
    - err ~~> N(0,s**2)
    - variance(error)==s**2 is the same accross the data
    - var(Y/X)==s**2 ; E(Y/X) = pr[0] + pr[1]*X + pr[2]*X^2 + pr[3]*X^3
    - pr[i] cst
    - pr[i] not null => i add a test hypothesis (to reject the null H0:coeff==0 against H1:coeff!=0), not a confidence interval (to check if 0 if not in)


    prediction 
    - each pr[i] have a mean and a std based on normal distribution
    - Y too => 
        - Mean(Y) = y_hat = pr_h[0] + pr_h[1]*X + pr_h[2]*X^2 + pr_[3]*X^3
        - Some model can predict quantile(Y, 95%) but i will just add std(y_hat) later. uuh isn't s ?


    predictors 
    - pr[i], s**2

    lenght 
    - you may need data over 1000 samples to get

    Others 
    D'ont forget about the errors !
    Predictions have certain uncertainty => [ poorer fitted model => larger uncertainty]

    utils
    - [standard error of the intercept - stats.stackexchange](https://stats.stackexchange.com/questions/173271/what-exactly-is-the-standard-error-of-the-intercept-in-multiple-regression-analy)
    '''

    alpha = check_or_get_alpha_for_hyph_test(alpha)
    logit = bool(logit)

    # reshape and remove nan
    x = array(x).flatten()
    y = array(y).flatten()
    x, y = clear_list_pair(x, y)
    # get sizes
    n = len(x)
    degre = int(degre)
    # constraint
    check_hyp_min_sample(n)
    if n != len(y):
        raise Exception("x and y lenght must match")

    # create X
    '''X = zeros((n, degre))
    for i in range(0, degre):
        X[:, i] = power(x, i)'''
    X = array([power(x, i) for i in range(1, degre + 1)]).T
    assert X.shape == (n, degre)
    assert y.shape == (n, )

    cr = ComputeRegression(logit=logit,
                           fit_intercept=fit_intercept,
                           alpha=alpha,
                           debug=debug)
    cr.fit(X, y, nb_iter=nb_iter, learning_rate=learning_rate)
    coeffs, list_coeffs_std, residu_std, Testresults = cr.get_regression_results(
    )

    nb_param = degre
    if fit_intercept:
        nb_param += 1
    assert coeffs.shape == (nb_param, )
    assert list_coeffs_std.shape == (nb_param, )

    _others = {"cr": cr}

    return coeffs, list_coeffs_std, residu_std, Testresults, _others


def ME_multiple_regression(X: list,
                           y: list,
                           logit=False,
                           fit_intercept=True,
                           debug=False,
                           alpha: float = 0.05,
                           nb_iter: int = 100000,
                           learning_rate: float = 0.1):
    """_summary_

    Args:
        X (list): _description_
        y (list): _description_
        debug (bool, optional): _description_. Defaults to False.
        alpha (_type_, optional): _description_. Defaults to COMMON_ALPHA_FOR_HYPH_TEST.

    estimate a regression model from two samples

    prediction
    - predict Y conditional on X, B, G, ... assuming that Y = pr[0] + pr[1]*X + pr[2]*B + pr[3]*G + N(0,s**2)
    - Y is a dependant variable
    - x, B, G, ...., s are independant ones => predictors of the dependant variables
    - If there is a time stamp of measures (or paired data), please add them as independant variables pr[0] + pr[4]*T1 +pr[5]*T2 + 
        => The correlation of the repeated measures needs to be taken into account, and time since administration needs to be added to the model as an independent variable.

    Questions of interest  
    - Are you interested in establishing a relationship?
    - Are you interested in which predictors are driving that relationship?

    visualisation: 
    - sns.scatterplot(X[i],y) for i in range(len(X)) 
    - check for Form_linear_or_not;Direction_pos_or_neg;Strengh_of_the_colinearity;Outliers

    hypothesis 
    - Y = pr[0] + pr[1]*X + pr[2]*B + pr[3]*G + err
    - err ~~> N(0,s**2)
    - variance(error)==s**2 is the same accross the data
    - var(Y/X)==s**2 ; E(Y/X) = pr[0] + pr[1]*X + pr[2]*B + pr[3]*G
    - pr[i] cst
    - pr[i] not null => i add a test hypothesis (to reject the null H0:coeff==0 against H1:coeff!=0), not a confidence interval (to check if 0 if not in)
    - non Collinearity a.k.a Multicollinearity
        - a correlation with be computed
        - Anyway, i does not change the predictive power not the efficieency of the model 
        - Too, i guess aic selection remove one right ?
        - But data about coefficients are not good because there is repetition
        - Regression Trees = can handle correlated data well

    prediction 
    - each pr[i] have a mean and a std based on normal distribution
    - Y too => 
        - Mean(Y) = y_hat = pr_h[0] + pr_h[1]*X + pr_h[2]*B + pr_h[3]*G
        - Some model can predict quantile(Y, 95%) but i will just add std(y_hat) later. uuh isn't s ?


    predictors 
    - pr[i], s**2

    lenght 
    - you may need data over 1000 samples to get

    Others 
    D'ont forget about the errors !
    Predictions have certain uncertainty => [ poorer fitted model => larger uncertainty]

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """
    alpha = check_or_get_alpha_for_hyph_test(alpha)
    fit_intercept = bool(fit_intercept)
    logit = bool(logit)

    # reshape and remove nan
    X = array(X)
    y = array(y)
    assert X.ndim == 2
    assert y.ndim == 1
    assert y.shape == (X.shape[0], ), "x and y lenght must match"

    X, y = clear_mat_vec(X, y)

    # constraint
    check_hyp_min_sample(X.shape[0])

    cr = ComputeRegression(logit=logit,
                           fit_intercept=fit_intercept,
                           alpha=alpha,
                           debug=debug)
    cr.fit(X, y, nb_iter=nb_iter, learning_rate=learning_rate)
    coeffs, list_coeffs_std, residu_std, Testresults = cr.get_regression_results(
    )
    nb_param = X.shape[1]  # without slope
    if fit_intercept:
        nb_param = nb_param + 1
    assert coeffs.shape == (nb_param, )
    assert list_coeffs_std.shape == (nb_param, )

    _others = {"cr": cr}

    return coeffs, list_coeffs_std, residu_std, Testresults, _others


def ME_logistic_regression(X: list, y: list, debug=False, alpha=None):
    pass


if __name__ == "__main__":
    pass
else:
    pass  # print = lambda *args: ""
