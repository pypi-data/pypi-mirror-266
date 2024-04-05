'''
Some defs
- parameter: A quantifiable characteristic of a population
- confidence interval: range of reasonable values for the parameter

todo
- use kwargs format while calling functions
- reorder fcts attributes
'''

from numpy import mean
from ..hyp_vali_md import check_hyp_min_samples
from .ci_estimators import CIE_MEAN_ONE, CIE_MEAN_TWO, CIE_ONE_PROPORTION, CIE_PROPORTION_TWO
from ..hyp_vali_md import check_hyp_min_sample, check_or_get_cf_for_conf_inte, check_zero_to_one_constraint
from ..utils_md import estimate_std, clear_list, clear_list_pair, Confidence_data


def IC_PROPORTION_ONE(sample_size: int,
                      parameter: float,
                      confidence: float = None,
                      method: str = None):
    '''
    Confidence_interval(ONE PROPORTION):Confidence interval calculus after a statistic test
    - input
        - sample_size: int: sample size (more than 10 to use this method)
        - parameter: float: the measurement on the sample
        - confidence: float: confidence confidence (between O and 1). Greater the confidence, wider the interval
        - method: str: either "classic" (default) or "conservative.

    - Example: 
        - how many men in the entire population with a con ?
        - a form filled by 300 people show that there is only 120 men => p = (120/300); N=300

    - Hypothesis
        - the sample is over 10 for each of the categories in place => we use the "Law of Large Numbers"
        - the sample proportion comes from data that is considered a simple random sample

    - Idea 
        - let P: the real proportion in the population
        - let S: Size of each sample == nb of observations per sample
        - For many samples, we calculate proportions per sample: ex: for N samples of size S => N proportions values
        - (p - P) / ( p*(1-p)/S ) follow a normal distribution

    - Descriptions:
        - For a given polulation and a parameter P to find, If we repeated this study many times, each producing a new sample (of the same size {res.sample_size==S}) from witch a {res.confidence} confidence interval is computed, then {res.confidence} of the resulting confidence intervals would be excpected to contain the true value P 
        - If the entire interval verify a property, then it is reasonable say that the parameter verify that property

    - Result
        - with a {res.confidence} confidence, we estimate that the populztion proportion who are men is between {res.left_tail} and {res.right_tail}
    '''
    p = parameter  # value of the paramater ==sample proportion == statistic == estimate of the population proportion
    N = sample_size  # sample size out of the population
    cf = check_or_get_cf_for_conf_inte(confidence=confidence)

    check_zero_to_one_constraint(p)
    check_hyp_min_sample(N, p)

    method = method or "classic"

    p, marginOfError, interval = CIE_ONE_PROPORTION(cf=cf,
                                                    proportion=p,
                                                    n=N,
                                                    method=method)
    assert p >= interval[0]
    assert p <= interval[1]

    data = Confidence_data(parameter=p,
                           sample_size=N,
                           confidence=cf,
                           marginOfError=marginOfError,
                           interval=interval)

    return data


def IC_MEAN_ONE(sample: list, t_etoile=None, confidence: float = None):
    '''
    Estimate_population_mean(ONE MEAN): We need the spread (std): We will use an estimation

    Data 
        - confidence:..
        - sample: value...

    Method
    - Use t-distribution to calculate few

    Hypothesis
    - Samples follow a normal (or large enough to bypass this assumption) => means of these sample follow a t-dist
    '''
    sample = clear_list(sample)

    cf = check_or_get_cf_for_conf_inte(confidence=confidence)
    mean_dist = float(mean(sample))
    sample_size = len(sample)
    std_sample = estimate_std(sample)

    p, marginOfError, interval = CIE_MEAN_ONE(cf=cf,
                                              n=sample_size,
                                              mean_dist=mean_dist,
                                              std_sample=std_sample,
                                              t_etoile=t_etoile)

    assert p == mean_dist
    assert p >= interval[0]
    assert p <= interval[1]

    data = Confidence_data(parameter=mean_dist,
                           sample_size=sample_size,
                           confidence=cf,
                           marginOfError=marginOfError,
                           interval=interval)

    return data


def IC_PROPORTION_TWO(p1, p2, N1, N2, confidence: float = None):
    '''
    Difference_population_proportion(TWO PROPORTIONS): We have have estimate a parameter p on two populations (1 , 2).How to estimate p1-p2 ? #p1-p2#

    Method
        - create joint confidence interval

    Construction
    - Cmparison 

    Hypotheses
    - two independant random samples
    - large enough sample sizes : 10 per category (ex 10 yes, 10 no)
    '''
    cf = check_or_get_cf_for_conf_inte(confidence=confidence)
    check_zero_to_one_constraint(p1, p2)
    check_hyp_min_samples(p1, p2, N1, N2)

    p, marginOfError, interval = CIE_PROPORTION_TWO(p1=p1,
                                                    p2=p2,
                                                    n1=N1,
                                                    n2=N2,
                                                    cf=cf)  # p1-p2#
    assert p >= interval[0]
    assert p <= interval[1]

    data = Confidence_data(parameter=p,
                           sample_size=(N1, N2),
                           confidence=cf,
                           marginOfError=marginOfError,
                           interval=interval)

    return data


def IC_MEAN_TWO_PAIR(sample1,
                     sample2,
                     t_etoile=None,
                     confidence: float = None):
    '''
    Difference_population_means_for_paired_data(TWO MEANS FOR PAIRED DATA): We have have estimate a parameter p on two populations (1 , 2).How to estimate p1-p2 ? #p1-p2#


    What is paired data ?

        - measurements took on individuals (people, home, any object)
        - technicality: 
            - When in a dataset (len = n) there is a row  df.a witch values only repeat twice (=> df.a.nunique = n/2) 
            - we can do a plot(x=feature1, y=feature2)
        - examples
            - Each home need canibet quote from two suppliers => we want to know if there is an average difference in nb_quotes from between twese two suppliers
            - In a blind taste test to compare two new juice flavors, grape and apple, consumers were given a sample of each flavor and the results will be used to estimate the percentage of all such consumers who prefer the grape flavor to the apple flavor.
        - Construction
            - It is like, 
                - checking if a feature magnitude change when going from a category to another, each pair split the two cztegories
                - Example_contexte
                    - having a dataframe df, with 3 col [name, score, equipe, role] 
                        - equipe: "1" or "2"
                        - role: df.role.nunique = 11 => len(df)==22
                    - Now there is a battle: For a "same role" fight", which team is the best?
                - Example_question
                    - if education level are generally equal -> mean difference is 0
                        - Is there a mean difference between the education level of twins
                        - if education levels are unequel -> mean difference is not 0
                    - So, Look for 0 in the ranfe of reaonable values

    We need the spread (std): We will use an estimation

    Equivl
    - IC_MEAN_ONE(confidence, sample1 - sample2)

    Data 
        - confidence:..
        - Sample1: list: values...
        - Sample2: list: (same len) values...


    Method
    - Use t-distribution to calculate few
    - create joint confidence interval

    Hypothesis
    - a random sample of identical twin sets
    - Samples follow a normal (or large enough to bypass this assumption: (ex 20 twins)) => means of these sample follow a t-dist

    Notes
    - With {cf} confidence, the population mean difference of the (second_team - first_team) attribute is estimated to be between {data.interval[0]} and {dat.interval[1]}
    - if all values are above 0, cool there is a significativity
    '''

    sample1, sample2 = clear_list_pair(sample1, sample2)

    N = len(sample1)
    if N != len(sample2):
        raise Exception('two samples from the same size')

    cf = check_or_get_cf_for_conf_inte(confidence=confidence)
    check_hyp_min_sample(N)

    Sample_diff = sample1 - sample2  # p1-p2#

    diff_mean = Sample_diff.mean()
    std_sample = estimate_std(Sample_diff)
    # std_sample = sqrt(estimate_std(sample1)**2 +estimate_std(sample2)**2  ) #wrong!!!
    if t_etoile:
        p, marginOfError, interval = CIE_MEAN_ONE(n=N,
                                                  mean_dist=diff_mean,
                                                  std_sample=std_sample,
                                                  t_etoile=t_etoile,
                                                  cf=cf)
    else:
        p, marginOfError, interval = CIE_MEAN_ONE(n=N,
                                                  mean_dist=diff_mean,
                                                  std_sample=std_sample,
                                                  cf=cf)
    assert p >= interval[0]
    assert p <= interval[1]

    data = Confidence_data(parameter=p,
                           sample_size=N,
                           confidence=cf,
                           marginOfError=marginOfError,
                           interval=interval)

    return data


def IC_MEAN_TWO_NOTPAIR(sample1,
                        sample2,
                        pool=False,
                        confidence: float = None):
    '''
    Difference_population_means_for_nonpaired_data(TWO MEANS FOR PAIRED DATA): We have have estimate a parameter p on two populations (1 , 2).How to estimate p1-p2 ? #p1-p2#

    Construction
    - It is like, 
        - checking if a feature magnitude change when going from a category to another
        - Example_contexte
            - having a dataframe df, with 3 col [name, score, equipe, role] 
                - equipe: "1" or "2"
                - role: df.role.nunique = 11 => len(df)==22
            - Now there is a battle: For a "same role" fight", which team is the best?
        - Example_question
            - if education level are generally equal -> mean difference is 0
                - Is there a mean difference between the education level based on gender
                - if education levels are unequel -> mean difference is not 0
            - So, Look for 0 in the ranfe of reaonable values

    We need the spread (std): We will use an estimation

    Args 
        - confidence:..
        - Sample1: list: values...
        - Sample2: list: (same len) values...
        - pool: default False
            - True 
                - if we assume that our populations variance are equal
                - we use a t-distribution of (N1+N2-1) ddl
            - False 
                - if we assume that our populations variance are not equal
                - we use a t-distribution of min(N1, N2)-1 ddl

    Method
    - Use t-distribution to calculate few
    - create joint confidence interval

    Hypothesis
    - a random sample
    - Samples follow a normal (or large enough to bypass this assumption: 10 per category) => means of these sample follow a t-dist

    Notes
    - With {cf} confidence, the population mean difference of the (second_team - first_team) attribute is estimated to be between {data.interval[0]} and {dat.interval[1]}
    - if all values are above 0, cool there is a significativity
    '''
    sample1 = clear_list(sample1)
    sample2 = clear_list(sample2)
    N1 = len(sample1)
    N2 = len(sample2)

    cf = check_or_get_cf_for_conf_inte(confidence=confidence)
    check_hyp_min_sample(N1)
    check_hyp_min_sample(N2)

    diff_mean = sample1.mean() - sample2.mean()  # p1-p2#
    std_sample1 = estimate_std(sample1)
    std_sample2 = estimate_std(sample2)

    p, marginOfError, interval = CIE_MEAN_TWO(N1=N1,
                                              N2=N2,
                                              diff_mean=diff_mean,
                                              std_sample_1=std_sample1,
                                              std_sample_2=std_sample2,
                                              pool=pool,
                                              cf=cf)
    assert p >= interval[0]
    assert p <= interval[1]

    data = Confidence_data(parameter=p,
                           sample_size=(N1, N2),
                           confidence=cf,
                           marginOfError=marginOfError,
                           interval=interval)

    return data


if __name__ == "__main__":
    pass
else:
    print = lambda *args: ""
