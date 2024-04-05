'''
utils 
- Dans un test, H0 est l'hypothese pessimiste 
    - il faudra donc assez d'evidence (p<0.05) afin de la rejeter

todo
- refactor output (last lines)
- use "alternative" instead of "tail"
- use kwargs format while calling functions
- reorder fcts attributes
'''

from ..hyp_vali_md import check_hyp_min_sample, check_hyp_min_samples, check_or_get_alpha_for_hyph_test, check_zero_to_one_constraint
from ..utils_md import Hypothesis_data, Tails, get_p_value, get_p_value_f_test, get_p_value_t_test, get_p_value_z_test
from math import sqrt
from numpy import array, vectorize, random
from numpy.linalg import norm
SUM = sum
random.seed(233)


def HPE_FROM_P_VALUE(tail: str = None,
                     p_value=None,
                     t_stat=None,
                     p_hat=None,
                     p0=None,
                     std_stat_eval=None,
                     alpha=None,
                     test="z_test",
                     ddl=0,
                     onetail=False):
    """_summary_

    Args:
        tail (str, optional): "middle" or "left" or "right"
        p_value (_type_, optional): _description_. Defaults to None.
        t_stat (_type_, optional): _description_. Defaults to None.
        p_hat (_type_, optional): _description_. Defaults to None.
        p0 (_type_, optional): _description_. Defaults to None.
        std_stat_eval (_type_, optional): _description_. Defaults to None.
        alpha (_type_, optional): _description_. Defaults to None.
        test (str, optional): _description_. Defaults to "z_test".
        ddl (int, optional): _description_. Defaults to 0.
        onetail (bool, optional): if tail="middle". return one_tail_cf_p_value instead of the 2tail_2cf_p_value Defaults to False.



    Returns:
        _type_: _description_
    """
    alpha = check_or_get_alpha_for_hyph_test(alpha)
    if int(t_stat != None) + int(p_value != None) + int(p_hat != None) > 1:
        raise Exception("Set only t_stat or set p_value or p_hat")

    elif t_stat == None and p_value == None and p_hat == None and p0 != None and std_stat_eval != None:
        raise Exception(
            "Either set t_stat or set p_value or set p_hat,p0,std_stat_eval")

    # compute Z_test/T_test if not set
    elif p_hat != None:
        if t_stat != None:
            raise Exception("You set p_value while p_hat is already set")
        p_hat = float(p_hat)
        p0 = float(p0)
        std_stat_eval = float(std_stat_eval)
        t_stat = (p_hat - p0) / std_stat_eval
        print("t_stat = ", t_stat)

    # get p_value if not set
    if t_stat != None:
        if p_value != None:
            raise Exception(
                "You set p_value while t_stat is already set or computated")
        tail = Tails.norm_tail(tail)
        p_value = get_p_value(Z=t_stat, ddl=ddl, tail=tail, test=test)
        if tail == Tails.middle and onetail:
            p_value = p_value / 2

    # rejection #we want to be far away from the mean (how p_value= how great is (p_hat - p0) = how far p_hat is from p0 considered as mean)
    reject_null = True if p_value < alpha else False
    # return p_hat, p0, std_stat_eval, t_stat, p_value,reject_null

    data = Hypothesis_data(parameter=p_hat,
                           pnull=p0,
                           std_stat_eval=std_stat_eval,
                           tail=tail,
                           sample_size=None,
                           alpha=alpha,
                           Z=t_stat,
                           p_value=p_value,
                           reject_null=reject_null)

    return data


def HPE_PROPORTION_ONE(alpha, p0, proportion, n, tail=Tails.right):
    '''
    check a proportion of an attribute value (male gender, ) in a population based on a sample  (no sign pb) using a Z-statistic
    - alpha: p_value_max: significance level
    - p0: proportion under the null
    - proportion: measurement 
    - n: number of observations == len(sample)
    - tail: 
        - right: check if p>p0
        - left: check if p<p0
        - middle: ckeck id p==p0
    Hyp
    - simple random sample
    - large sample (np>10)

    Hypotheses
    - H0: proportion = p0
    - H1: 
        - tail==right => proportion > p0
        - tail==left => proportion < p0
        - tail==middle => proportion != p0

    Detail
    - use a normal distribion (Z-statistic)

    Result (ex:tail=right)
    - if reject==True
        - There is sufficient evidence to conclude that the population proportion of {....} is greater than p0
    '''
    # cdt
    proportion = float(proportion)
    p0 = float(p0)
    n = int(n)
    alpha = check_or_get_alpha_for_hyph_test(alpha)
    check_zero_to_one_constraint(proportion, p0)
    check_hyp_min_sample(n, proportion)

    # parameter
    p_hat = proportion

    # calculate the Z-statistic:
    # standard error of the estimate
    # scipy.stats.stats.proportions_ztest utilise p_hat ici au lieu de p0 => mais les result ts ne varient pas trop
    # the null standard error #la proportion suit une loi de bernouli => on passe à plusieurs samples
    std_stat_eval = sqrt(p0 * (1 - p0) / n)
    # compute Z corresponding to normal distribtion
    # "assume" that th eproportion folow a normal for many samples
    Z = (p_hat - p0) / std_stat_eval
    print("Z = ", Z)

    # compute p_value
    p_value = get_p_value_z_test(Z, tail=tail)

    # rejection #we want to be far away from the mean (how p_value= how great is (p_hat - p0) = how far p_hat is from p0 considered as mean)
    reject_null = True if p_value < alpha else False
    return p_hat, p0, std_stat_eval, Z, p_value, reject_null


def HPE_PROPORTION_TW0(alpha, p1, p2, n1, n2, tail=Tails.middle, evcpp=False):
    '''
    check the diff of proportion between 2 population based on a sample from each population (p1-p2) #p1-p2# using a Z-statistic (always used for difference of estimates).
    there is also fisher and chi-square
    - alpha: level of significance
    - p1: proportion of liste1
    - p2: proportion of liste2
    - n1: len(liste1)
    - n2: len(liste2)
    - evcpp: bool(defult=False) (True -> Estimate of the variance of the combined population proportion)

    Hyp
    - two independant samples
    - two random samples
    - large enough data

    Hypotheses
    - H0: proportion = p0
    - H1: proportion !=p0

    Detail
    - use a normal distribion (Z-statistic)
    '''

    # cdt
    p1 = float(p1)
    p2 = float(p2)
    n2 = int(n2)
    n1 = int(n1)
    alpha = check_or_get_alpha_for_hyph_test(alpha)

    # cdt
    check_zero_to_one_constraint(p1, p2)
    check_hyp_min_samples(p1, p2, n1, n2)

    # parameter
    p_hat = abs(p1 - p2)  # estimator
    p0 = 0

    # calculate the Z-statistic:
    # standard error of the estimate
    # the null standard error #la proportion suit une loi de bernouli => on passe à plusieurs samples
    if evcpp:
        # estimation de sqrt(p_hat*(1-p_hat)*(1/n1 + 1/n2))
        # Estimate of the combined population proportion
        phat2 = (p1 * n1 + p2 * n2) / (n1 + n2)
        # Estimate of the variance of the combined population proportion
        va = phat2 * (1 - phat2)
        # Estimate of the standard error of the combined population proportion
        std_stat_eval = sqrt(va * (1 / n1 + 1 / n2))
    else:
        std_stat_eval = sqrt((p1 * (1 - p1) / n1) + (p2 * (1 - p2) / n2))

        # compute Z corresponding to normal distribtion
    # "assume" that th eproportion folow a normal for many samples
    Z = (p_hat - p0) / std_stat_eval
    print(f"Z = ({p_hat - p0})/{std_stat_eval} = ", Z)
    # Z = abs(Z) #to use tail=right it is now a H1:p>p0 problem

    # compute p_value
    tail = Tails.norm_tail(tail)
    tail = Tails.norm_tail(tail)
    p_value = get_p_value_z_test(Z, tail=tail, debug=True)

    # rejection (we want to be far away from the mean to reject the null)
    # use alpha or alpha/2 ??
    reject_null = True if p_value < alpha else False
    return p_hat, p0, std_stat_eval, Z, p_value, reject_null


def HPE_MEAN_ONE(alpha, p0, mean_dist, n, std_sample, tail=Tails.right):
    '''
    get the mean of a population from a sample  (no sign pb) using using a T-statistic (always T for mean!! unless youre comparing a sample vs a population of known std)
    - alpha: 
    - n: number of observations == len(sample)
    - mean_dist: the mean measured on the sample = mean(sample)
    - std_sample: std of the sample  ==std(sample). You should use a real estimate (ffod=n-1)

    Hyp
    - simple random sample
    - better the population follow nornal dist. Or use large sample (>10)
        - Alternative to normality: Wilcoxon Signed Rank Test

    Theo
    - read [here](https://en.wikipedia.org/wiki/Student's_t-distribution#How_Student's_distribution_arises_from_sampling)
    '''

    # ctd
    alpha = check_or_get_alpha_for_hyph_test(alpha)
    check_hyp_min_sample(n)

    mean_dist = float(mean_dist)
    std_sample = float(std_sample)
    n = int(n)

    # parameter
    p_hat = mean_dist

    # calculate the Z-statistic:
    # standard error of the estimate
    # à cause du la loi des samples de N qui suivent une t à (n-1) ddl non?
    std_stat_eval = std_sample / sqrt(n)
    # compute Z corresponding to normal distribtion
    # "assume" that th eproportion folow a normal for many samples
    Z = (p_hat - p0) / std_stat_eval
    print("Z = ", Z)

    # compute p_value
    p_value = get_p_value_t_test(Z, ddl=n - 1, tail=tail)

    # rejection #we want to be far away from the mean (how p_value= how great is (p_hat - p0) = how far p_hat is from p0 considered as mean)
    reject_null = True if p_value < alpha else False
    return p_hat, p0, std_stat_eval, Z, p_value, reject_null


def HPE_MEAN_TWO_PAIRED(alpha,
                        mean_diff_sample,
                        n,
                        std_diff_sample,
                        tail=Tails.middle):
    '''
    get the difference of mean between two list paired (no sign pb) using a T-statistic (always T for mean!! unless youre comparing a sample vs a population of known std)
    - alpha: 
    - mean_diff_sample: the mean measured on the sample = mean(sample)
    - n: number of observations == len(sample) == n1 == n2
    - std_diff_sample: std of the sample  ==std(sample). You should use a real estimate (ffod=n-1)
    - tail: default=Tails.middle to test the equality (mean_diff=0). But we can also to mean_diff>0 (right) or mean_diff<0 (left)

    Hyp
    - simple random sample
    - better when the diff of the samples (sample1 - sample2) follow nornal dist. Or use large sample (>10)
    - std_diff_sample is a good data based estimated [use (n-1) instead of n]. example: np.std(sample1 - sample2, ddof=1) is better than ddof=0 (default)

    Hypothesis
    - H0: p1 - p2 = 0
    - H1: 
        - H1: p1 - p2 != 0 for(tail=middle) 
        - H1: p1 - p2 > 0 for(tail=right) 
        - H1: p1 - p2 < 0 for(tail=left) 
    '''
    alpha = check_or_get_alpha_for_hyph_test(alpha)
    p0 = 0
    return HPE_MEAN_ONE(alpha,
                        p0,
                        mean_diff_sample,
                        n,
                        std_diff_sample,
                        tail=tail)


def HPE_MEAN_TWO_NOTPAIRED(alpha,
                           diff_mean,
                           N1,
                           N2,
                           std_sample_1,
                           std_sample_2,
                           pool=False,
                           tail=Tails.middle):
    '''
    check the diff in mean of two populations(taking their samples) (sign(diff_mean) => no sign pb)
    - alpha: 
    - N1: number of observations == len(sample1)
    - N2: number of observations == len(sample2)
    - mean_dist: the mean measured on the sample = mean(sample)
    - std_sample_1: std of the sample  ==std(sample1)
    - std_sample_2: std of the sample  ==std(sample2)
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
    - for pool=True, variances must be the same
        - to test that, you can 
            - use levene test [plus robuste que fusher ou bartlett face à la non-normalité de la donnée](https://fr.wikipedia.org/wiki/Test_de_Bartlett)
                ::H0: Variances are equals; H1: there are not
                ::scipy.stats.levene(liste1,liste2, center='mean')
                ::solution = "no equality" if p-value<0.05 else "equality"
            - or check if IQR are the same
                - IQR = quantile(75%) - quantile(25%)

    Theo
    - read [here](https://en.wikipedia.org/wiki/Student's_t-distribution#How_Student's_distribution_arises_from_sampling)
    '''

    # ctd
    alpha = check_or_get_alpha_for_hyph_test(alpha)
    check_hyp_min_sample(N1)
    check_hyp_min_sample(N2)

    diff_mean = float(diff_mean)
    std_sample_1 = float(std_sample_1)
    std_sample_2 = float(std_sample_2)
    N1 = int(N1)
    N2 = int(N2)

    # parameter
    p_hat = diff_mean
    p0 = 0
    # few value: from t distribution with ddl = fct(pool)
    ddl = min(N1, N2) - 1 if not pool else N1 + N2 - 2

    # calculate the Z-statistic:
    # standard error of the stat
    if not pool:
        # or std_sample*sqrt( 1/N1 + 1/N2) with std_sample==std_sample_1==std_sample_2
        std_stat_eval = sqrt((std_sample_1**2) / N1 + (std_sample_2**2) / N2)
    else:
        std_stat_eval = sqrt(
            ((N1 - 1) * (std_sample_1**2) + (N2 - 1) *
             (std_sample_2**2)) / (N1 + N2 - 2)) * sqrt(1 / N1 + 1 / N2)

        # compute Z corresponding to normal distribtion
    # "assume" that th eproportion folow a normal for many samples
    Z = (p_hat - p0) / std_stat_eval
    print("Z = ", Z)

    # compute p_value
    p_value = get_p_value_t_test(Z, ddl=ddl, tail=tail)

    # rejection #we want to be far away from the mean (how p_value= how great is (p_hat - p0) = how far p_hat is from p0 considered as mean)
    reject_null = True if p_value < alpha else False
    return p_hat, p0, std_stat_eval, Z, p_value, reject_null


def HPE_MEAN_MANY(*samples, alpha=None):
    """check if mean is equal accross many samples

    Hypothesis
    H0: mean1 = mean2 = mean3 = ....
    H1: one is different

    Hypothesis
    - each sample is 
        - simple random 
        - normal
        - indepebdant from others
    - same variance 
        - if added, the "same variance test" should use levene test but apparently, use levene test [plus robuste que fusher ou bartlett face à la non-normalité de la donnée](https://fr.wikipedia.org/wiki/Test_de_Bartlett)


    Fisher test 
        - The F Distribution is also called the Snedecor’s F, Fisher’s F or the Fisher–Snedecor distribution [1](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html) [2](https://blog.minitab.com/fr/comprendre-lanalyse-de-la-variance-anova-et-le-test-f)

    Returns:
        stat: (float) F
        p_value: (float)
    """
    alpha = check_or_get_alpha_for_hyph_test(alpha)
    for elt in samples:
        assert len(elt) > 0

    samples = array(samples, dtype=object)
    k = len(samples)  # the number of groups

    sum_loc_ = vectorize(SUM)
    list_Ti = sum_loc_(samples)  # list of Ti
    assert list_Ti.shape == (k, )
    G = SUM(list_Ti)
    assert array(G).shape == ()

    len_loc_ = vectorize(len)
    list_ni = len_loc_(samples)
    assert list_ni.shape == (k, )
    n = SUM(list_ni)  # the total number of subjects in the experiment
    print(f"n={n} k={k}")
    assert array(n).shape == ()

    norm_loc_ = vectorize(norm)
    list_norm = norm_loc_(samples)
    assert list_norm.shape == (k, )

    # S_carre = sum_i( sum_j(samples[i][j]**2) / len(sample[i]) ) #[pour chaque grp, [je fais la somme des carre; je divise par le nb_elt], je somme tout] => somme_on_groups(E(X**2))
    S_carre = sum(list_Ti**2 / list_ni)
    # variance btw groups
    # y_hat-y_mean# S_carre - sum_i_j(samples[i][j])**2 / sum_i(len(samples[i])) #G est la somme de toutes les observations #n est le nombre total d'observations ==> somme_on_groups(E(X**2)/len_grp) - E(X)**2 /len_total
    SSR = S_carre - G**2 / n
    # var within group
    # y-y_hat# sum_i_j(sample[i][j]**2) - S_carre ==> E(X**2) - somme_on_groups(E(X**2)/len_grp)
    SSE = sum(list_norm**2) - S_carre

    assert SSR.shape == ()
    assert SSE.shape == ()

    dfe = n - k  # error in sample
    dfr = k - 1  # explained by the diff bewtwenn samples

    # variance between samples #the mean square due to dependant_var = fct(groups) (between groups)
    MSR = SSR / dfr
    # variance within sample #is the mean square due to error (within groups, residual mean square)
    MSE = SSE / dfe
    F = MSR / MSE

    # plus F est grand, plus la diff des mean s'explique par la difference entre les groupes
    # plus F est petit, plus la diff des mean s'explique par la variabilite naturelle des samples

    # On veut F grand donc on prends un right tail =>

    p_value = get_p_value_f_test(Z=F, dfn=dfr, dfd=dfe)

    # rejection #we want to be far away from the mean (how p_value= how great is (p_hat - p0) = how far p_hat is from p0 considered as mean)
    reject_null = True if p_value < alpha else False
    return F, 0, 1, F, p_value, reject_null


if __name__ == "__main__":
    pass
else:
    print = lambda *args: ""
