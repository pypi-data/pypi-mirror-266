'''
utils 
    - Dans un test, H0 est l'hypothese pessimiste 
        - il faudra donc assez d'evidence (p<0.05) afin de la rejeter
        - on a alors mis une borne max faible sur l'erreur de type 1 (rejeter H0 alors qu'il est vrai)

Some defs
    - parameter: A quantifiable characteristic of a population (baseline)
    - alpha: level of significance = type1_error = proba(reject_null;when null is True)

todo
- docstrings for the fcts here

todo
- use kwargs format while calling functions
- reorder fcts attributes

note 
- mean_two_paired(Sample1, Sample2) <==> mean_one(Sample1 - Sample2)
'''


from numpy import mean
from .hp_estimators import HPE_MEAN_MANY, HPE_MEAN_ONE, HPE_MEAN_TWO_NOTPAIRED, HPE_MEAN_TWO_PAIRED, HPE_PROPORTION_ONE, HPE_PROPORTION_TW0
from ..hyp_vali_md import check_hyp_min_sample, check_hyp_min_samples, check_zero_to_one_constraint
from ..utils_md import estimate_std, clear_list, clear_list_pair, Hypothesis_data, Tails


def HP_PROPORTION_ONE(sample_size: int,
                      parameter: float,
                      p0: float,
                      alpha: float,
                      symb=Tails.SUP_SYMB):
    '''
    ONE PROPORTION:alpha calculus after a statistic test
    - input
        - sample_size: int: sample size (more than 10 to use this method)
        - parameter: float: the measurement on the sample
        - alpha: float: alpha alpha (between O and 1). Greater the alpha, wider the interval
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
        - For a given polulation and a parameter P to find, If we repeated this study many times, each producing a new sample (of the same size {res.sample_size==S}) from witch a {res.alpha} alpha is computed, then {res.alpha} of the resulting alphas would be excpected to contain the true value P 
        - If the entire interval verify a property, then it is reasonable say that the parameter verify that property

    - Result
        - with a {res.alpha} alpha, we estimate that the populztion proportion who are men is between {res.left_tail} and {res.right_tail}
    '''
    p = parameter  # value of the paramater ==sample proportion == statistic == estimate of the population proportion
    N = sample_size  # sample size out of the population
    alpha = alpha  # between 0 and 1

    check_zero_to_one_constraint(p, alpha)
    check_hyp_min_sample(N, p)

    tail = Tails.get_tail_from_symb(symb)

    p_hat, p0, std_stat_eval, Z, p_value, reject_null = HPE_PROPORTION_ONE(
        alpha=alpha, p0=p0, proportion=p, n=N, tail=tail)
    assert p_value >= 0
    assert p_value <= 1

    data = Hypothesis_data(parameter=p_hat,
                           pnull=p0,
                           std_stat_eval=std_stat_eval,
                           tail=tail,
                           sample_size=N,
                           alpha=alpha,
                           Z=Z,
                           p_value=p_value,
                           reject_null=reject_null)

    return data


def HP_MEAN_ONE(p0: float, alpha: float, sample: list, symb=Tails.SUP_SYMB):
    '''
    ONE MEAN: We need the spread (std): We will use an estimation

    Data 
        - alpha:..
        - sample: value...

    Method
    - Use t-distribution to calculate few

    Hypothesis
    - Samples follow a normal (or large enough to bypass this assumption) => means of these sample follow a t-dist
    '''
    check_zero_to_one_constraint(alpha)
    sample = clear_list(sample)

    alpha = alpha
    mean_dist = float(mean(sample))
    sample_size = len(sample)
    std_sample = estimate_std(sample)

    tail = Tails.get_tail_from_symb(symb)

    p_hat, p0, std_stat_eval, Z, p_value, reject_null = HPE_MEAN_ONE(
        alpha=alpha,
        p0=p0,
        mean_dist=mean_dist,
        n=sample_size,
        std_sample=std_sample,
        tail=tail)
    assert p_value >= 0
    assert p_value <= 1

    data = Hypothesis_data(parameter=p_hat,
                           pnull=p0,
                           std_stat_eval=std_stat_eval,
                           tail=tail,
                           sample_size=sample_size,
                           alpha=alpha,
                           Z=Z,
                           p_value=p_value,
                           reject_null=reject_null)

    return data


def HP_PROPORTION_TWO(alpha, p1, p2, N1, N2, symb=Tails.NEQ_SYMB, evcpp=False):
    '''
    TWO PROPORTIONS: We have have estimate a parameter p on two populations (1 , 2).How to estimate p1-p2 ? #p1-p2#

    Method
        - create joint alpha
        - evcpp: bool(defult=False) (True -> Estimate of the variance of the combined population proportion)


    Construction
    - Cmparison 

    Hypotheses
    - two independant random samples
    - large enough sample sizes : 10 per category (ex 10 yes, 10 no)
    '''
    alpha = alpha
    check_zero_to_one_constraint(alpha, p1, p2)
    check_hyp_min_samples(p1, p2, N1, N2)

    tail = Tails.get_tail_from_symb(symb)

    p_hat, p0, std_stat_eval, Z, p_value, reject_null = HPE_PROPORTION_TW0(
        alpha=alpha, p1=p1, p2=p2, n1=N1, n2=N2, tail=tail, evcpp=evcpp)
    assert p_value >= 0
    assert p_value <= 1

    data = Hypothesis_data(parameter=p_hat,
                           pnull=p0,
                           std_stat_eval=std_stat_eval,
                           tail=tail,
                           sample_size=(N1, N2),
                           alpha=alpha,
                           Z=Z,
                           p_value=p_value,
                           reject_null=reject_null)

    return data


def HP_MEAN_TWO_PAIR(alpha, sample1, sample2, symb=Tails.NEQ_SYMB):
    '''
    TWO MEANS FOR PAIRED DATA: We have have estimate a parameter p on two populations (1 , 2).How to estimate p1-p2 ? #p1-p2#


    What is paired data: 
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
    - estimate_population_mean(alpha, sample1 - sample2)

    Data 
        - alpha:..
        - Sample1: list: values...
        - Sample2: list: (same len) values...


    Method
    - Use t-distribution to calculate few
    - create joint alpha

    Hypothesis
    - a random sample of identical twin sets
    - Samples follow a normal (or large enough to bypass this assumption: (ex 20 twins)) => means of these sample follow a t-dist

    - description
    - With {alpha} alpha, the population mean difference of the (second_team - first_team) attribute is estimated to be between {data.interval[0]} and {dat.interval[1]}
    - if all values are above 0, cool there is a significativity
    '''

    sample1, sample2 = clear_list_pair(sample1, sample2)

    N = len(sample1)
    if N != len(sample2):
        raise Exception('two samples from the same size')

    alpha = alpha

    check_zero_to_one_constraint(alpha)
    check_hyp_min_sample(N)

    Sample_diff = sample1 - sample2  # p1-p2#

    diff_mean = Sample_diff.mean()
    std_sample = estimate_std(Sample_diff)

    tail = Tails.get_tail_from_symb(symb)

    p_hat, p0, std_stat_eval, Z, p_value, reject_null = HPE_MEAN_TWO_PAIRED(
        alpha=alpha,
        mean_diff_sample=diff_mean,
        n=N,
        std_diff_sample=std_sample,
        tail=tail)
    assert p_value >= 0
    assert p_value <= 1

    data = Hypothesis_data(parameter=p_hat,
                           pnull=p0,
                           std_stat_eval=std_stat_eval,
                           tail=tail,
                           sample_size=N,
                           alpha=alpha,
                           Z=Z,
                           p_value=p_value,
                           reject_null=reject_null)

    return data


def HP_MEAN_TWO_NOTPAIR(alpha,
                        sample1,
                        sample2,
                        symb=Tails.NEQ_SYMB,
                        pool=False):
    '''
    TWO MEANS FOR PAIRED DATA: We have have estimate a parameter p on two populations (1 , 2).How to check p1-p2 != 0? #p1-p2#

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

    Data 
        - alpha:..
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
    - create joint alpha

    Hypothesis
    - a random sample
    - Samples follow a normal (or large enough to bypass this assumption: 10 per category) => means of these sample follow a t-dist

    - description
    - With {alpha} alpha, the population mean difference of the (second_team - first_team) attribute is estimated to be between {data.interval[0]} and {dat.interval[1]}
    - if all values are above 0, cool there is a significativity
    '''
    sample1 = clear_list(sample1)
    sample2 = clear_list(sample2)
    N1 = len(sample1)
    N2 = len(sample2)

    alpha = alpha
    check_zero_to_one_constraint(alpha)
    check_hyp_min_sample(N1)
    check_hyp_min_sample(N2)

    diff_mean = sample1.mean() - sample2.mean()  # p1-p2#
    std_sample1 = estimate_std(sample1)
    std_sample2 = estimate_std(sample2)

    tail = Tails.get_tail_from_symb(symb)

    p_hat, p0, std_stat_eval, Z, p_value, reject_null = HPE_MEAN_TWO_NOTPAIRED(
        alpha=alpha,
        diff_mean=diff_mean,
        N1=N1,
        N2=N2,
        std_sample_1=std_sample1,
        std_sample_2=std_sample2,
        pool=pool,
        tail=tail)
    assert p_value >= 0
    assert p_value <= 1

    data = Hypothesis_data(parameter=p_hat,
                           pnull=p0,
                           std_stat_eval=std_stat_eval,
                           tail=tail,
                           sample_size=(N1, N2),
                           alpha=alpha,
                           Z=Z,
                           p_value=p_value,
                           reject_null=reject_null)

    return data


def HP_MEAN_MANY(*samples):

    for elt in samples:
        assert len(elt) > 0
    tail = "right"
    alpha = 0.05
    p_hat, p0, std_stat_eval, Z, p_value, reject_null = HPE_MEAN_MANY(samples)
    assert p_value >= 0
    assert p_value <= 1

    sample_size = [len(sample) for sample in samples]
    data = Hypothesis_data(parameter=p_hat,
                           pnull=p0,
                           std_stat_eval=std_stat_eval,
                           tail=tail,
                           sample_size=sample_size,
                           alpha=alpha,
                           Z=Z,
                           p_value=p_value,
                           reject_null=reject_null)

    return data


if __name__ == "__main__":
    pass
else:
    print = lambda *args: ""
