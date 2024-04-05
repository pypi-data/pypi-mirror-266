'''
todo
- refactor output (last lines)
- use "alternative" instead of "tail"
- use kwargs format while calling functions
- reorder fcts attributes
'''

from math import ceil as math_ceil
from math import sqrt

from ..hyp_vali_md import (check_hyp_min_sample, check_hyp_min_samples,
                           check_or_get_cf_for_conf_inte,
                           check_zero_to_one_constraint)
from ..utils_md import get_t_value, get_z_value


def get_min_sample(moe: float, p=None, method=None, cf: float = None):
    '''
    Get_min_sample:get the minimum of sample_size to use for a 
    - input
        - cf: confidence (or coverage_probability): between 0 and 1
        - moe: margin of error 
        - method (optional): "conservative" (default)
        - p: not used if method=="conservative"
    Hyp
    - better the population follow nornal dist. Or use large sample (>10)
    '''
    method = method or "conservative"
    cf = check_or_get_cf_for_conf_inte(confidence=cf)
    z_value = get_z_value(cf)
    min_sample = (z_value / (2 * moe))**2
    # print("min_sample = ",min_sample)
    return math_ceil(min_sample)


def CIE_ONE_PROPORTION(proportion, n, method, cf: float = None):
    '''
    Get_interval_simple: get a proportion of an attribute value (male gender, ) in a population based on a sample  (no sign pb)
    - cf: confidence_level (or coverage_probability)
    - proportion: measurement 
    - n: number of observations == len(sample)
    - method: "classic" or "conservative"

    Hyp
    - better the population follow nornal dist. Or use large sample (>10)
    '''

    # cdt
    proportion = float(proportion)
    n = int(n)
    method = str(method)
    cf = check_or_get_cf_for_conf_inte(confidence=cf)
    check_zero_to_one_constraint(proportion)
    check_hyp_min_sample(n, proportion)
    if method not in ["classic", "conservative"]:
        raise Exception("pb")

    # parameter
    p = proportion
    # few_value: from normal distribution (0,1)
    z_value = get_z_value(cf)
    print("z_value_ = ", z_value)
    # standard error of the stat
    std_stat_eval = 1 / \
        (2*sqrt(n)) if method == "conservative" else sqrt(p * (1-p)/n)
    # margin of error
    marginOfError = z_value * std_stat_eval
    # interval
    interval = (p - marginOfError, p + marginOfError)

    return p, marginOfError, interval


def CIE_PROPORTION_TWO(p1, p2, n1, n2, cf: float = None):
    '''
    Get_interval_diff: get the diff of mean between 2 population based on a sample from each population (p1-p2) #p1-p2#
    - cf: confidence_level (or coverage_probability)
    - p1: mean of liste1
    - p2: mean of liste2
    - n1: len(liste1)
    - n2: len(liste2)

    Hyp
    - better the populations follow normal dist. Or use large samples (>10)
    '''

    p1 = float(p1)
    p2 = float(p2)
    n1 = int(n1)
    n2 = int(n2)

    # cdt
    cf = check_or_get_cf_for_conf_inte(confidence=cf)
    check_zero_to_one_constraint(p1, p2)
    check_hyp_min_samples(p1, p2, n1, n2)

    # parameter
    p = p1 - p2  # p1-p2#
    # few_value: from normal distribution (0,1)
    z_value = get_z_value(cf)
    # standard error of the stat
    std_stat_eval = sqrt((p1 * (1 - p1) / n1) + (p2 * (1 - p2) / n2))
    # margin of error
    marginOfError = z_value * std_stat_eval
    # interval
    interval = (p - marginOfError, p + marginOfError)

    return p, marginOfError, interval


def CIE_MEAN_ONE(n, mean_dist, std_sample, t_etoile=None, cf: float = None):
    '''
    Get_interval_mean:get the mean of a population from a sample  (no sign pb)
    - cf: confidence level (or coverage_probability)
    - n: number of observations == len(sample)
    - mean_dist: the mean measured on the sample = mean(sample)
    - std_sample: std of the sample  ==std(sample)
    - t_etoile: if set, cf is ignored.

    Hyp
    - better the population follow nornal dist. Or use large sample (>10)
        - Alternative to normality: Wilcoxon Signed Rank Test

    Theo
    - reade [here](https://en.wikipedia.org/wiki/Student's_t-distribution#How_Student's_distribution_arises_from_sampling)
    '''

    # ctd
    if t_etoile == None:
        cf = check_or_get_cf_for_conf_inte(confidence=cf)
    else:
        t_etoile = float(t_etoile)
    check_hyp_min_sample(n)

    mean_dist = float(mean_dist)
    std_sample = float(std_sample)
    n = int(n)

    # parameter
    p = mean_dist
    # few value: from t distribution à (n-1) degre of freedom
    #
    if t_etoile == None:
        few = get_t_value(cf, n - 1)
    else:
        few = t_etoile

    # standard error of the stat
    std_stat_eval = std_sample / sqrt(n)
    # margin of error
    marginOfError = float(few * std_stat_eval)
    print(f"few={few} moe={marginOfError} ={std_sample} / sqrt({n})")
    # interval
    interval = (float(p - marginOfError), float(p + marginOfError))

    return p, marginOfError, interval


def CIE_MEAN_TWO(N1,
                 N2,
                 diff_mean,
                 std_sample_1,
                 std_sample_2,
                 t_etoile=None,
                 pool=False,
                 cf: float = None):
    '''
    Get_interval_diff_mean: get  the diff in mean of two populations(taking their samples) (sign(diff_mean) => no sign pb)
    - cf: confidence level (or coverage_probability)
    - N1: number of observations == len(sample1)
    - N2: number of observations == len(sample2)
    - mean_dist: the mean measured on the sample = mean(sample)
    - std_sample_1: std of the sample  ==std(sample1)
    - std_sample_2: std of the sample  ==std(sample2)
    - t_etoile: if set, cf is ignored.
    - pool: default False
        - True 
            - if we assume that our populations variance are equal
            - we use a t-distribution of (N1+N2-1) ddl
        - False 
            - if we assume that our populations variance are not equal
            - we use a t-distribution of min(N1, N2)-1 ddl

    Hyp
    - both the population follow normal dist. Or use large sample (>10)
    - the populations are independant from each other 
    - use simple random samples
    - for pool=True, variances are assume to be the same
        - to test that, you can 
            - use levene test [plus robuste que fusher ou bartlett face à la non-normalité de la donnée](https://fr.wikipedia.org/wiki/Test_de_Bartlett)
                - H0: Variances are equals; H1: there are not

                ```python
                scipy.stats.levene(liste1,liste2, center='mean')
                solution = "no equality" if p-value<0.05 else "equality"
                ```

            - or check if IQR are the same
                - IQR = quantile(75%) - quantile(25%)

    Eqvl
    - scipy.stats.ttest_ind(liste1,liste2, equal_var = False | True)


    Eqvl_pointWise estimation
    - Assume diff_mean = 82
    - Result: diff_mean in CI = [77.33, 87.63]
    - If we test H0:p=80 vs H1:p>80, we would fail to reject the null because H1 is not valide here
    - As sa matter of fact, there is some value in CI below 80 witch if not compatible with H1 => the test doest give enough evidence to reject H0

    Theo
    - read [here](https://en.wikipedia.org/wiki/Student's_t-distribution#How_Student's_distribution_arises_from_sampling)
    '''

    # ctd
    if t_etoile == None:
        cf = check_or_get_cf_for_conf_inte(confidence=cf)
    check_hyp_min_sample(N1)
    check_hyp_min_sample(N2)

    diff_mean = float(diff_mean)
    std_sample_1 = float(std_sample_1)
    std_sample_2 = float(std_sample_2)
    N1 = int(N1)
    N2 = int(N2)

    # parameter
    p = diff_mean
    # few value: from t distribution with ddl = fct(pool)
    ddl = min(N1, N2) - 1 if not pool else N1 + N2 - 2
    if t_etoile == None:
        # min(,) for a convervative approach => max of variance
        few = get_t_value(cf, ddl)
    else:
        few = t_etoile

    # standard error of the stat
    if not pool:
        std_stat_eval = sqrt((std_sample_1**2) / N1 + (std_sample_2**2) / N2)
    else:
        std_stat_eval = sqrt(
            ((N1 - 1) * (std_sample_1**2) + (N2 - 1) *
             (std_sample_2**2)) / (N1 + N2 - 2)) * sqrt(1 / N1 + 1 / N2)
    # margin of error
    # print(f"few={few} std={std_stat_eval}")
    marginOfError = float(few * std_stat_eval)
    # interval
    interval = (float(p - marginOfError), float(p + marginOfError))

    return p, marginOfError, interval


if __name__ == "__main__":
    pass
else:
    print = lambda *args: ""
