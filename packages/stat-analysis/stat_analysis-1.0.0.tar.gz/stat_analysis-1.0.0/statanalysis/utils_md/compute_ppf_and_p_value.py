from scipy.stats import f as f_dist
from scipy.stats import norm
from scipy.stats import t as t_dist

from .constants import LIM_MIN_SAMPLE
# utils
from .refactoring import Tails

# quantiles


def get_z_value(cf):
    return norm.ppf(1 - (1 - cf) / 2, loc=0, scale=1)


def get_t_value(cf, ddl):
    return t_dist.ppf(1 - (1 - cf) / 2, df=ddl)


# Fisher dist


def get_f_value(cf, ddl):
    return f_dist.ppf(1 - (1 - cf) / 2, df=ddl)


# p_value => fct de rpartition
def get_p_value_from_tail(prob, tail, debug=False):
    '''
    get p value based on cdf and tail
    If tail=Tails.middle, the distribution is assumed symmetric because we double F(Z)
    if tail
        - right: return P(N > Z) = 1- F(Z) =  1 - prob
        - left: return P(N < Z) = F(Z) = prob
        - middle: return P(N < -|Z|) + P(N > |Z|) => return  2*P(N > |Z|) 
    '''
    tail = Tails.norm_tail(tail)
    if tail == Tails.right:  # Z est à droite. On compte P(N>Z)
        return 1 - prob
    elif tail == Tails.left:  # Z est à gauche. On compte P(N<Z)
        return prob
    elif tail == Tails.middle:  # We take Z>0 so at the right => then double to take into account the left part #double because "normal" and "student" are both symetric!!!!
        '''En supposant la distribution symetrique'''
        if debug:
            print(f"p_val = 2*(1 - prob) = 2*(1 - {prob}) = {2*(1 - prob)}")
        return 2 * (1 - prob)
    else:
        raise Exception("tail not correct. get", tail)


def get_p_value_z_test(Z: float, tail: str, debug=False):
    '''
    get p value based on normal distribution N(0, 1)
    if tail
        - right: return P(N > Z)
        - left: return P(N < Z)
        - middle: return P(N < -|Z|) + P(N > |Z|) => return  2*P(N > |Z|)
    '''
    tail = Tails.norm_tail(tail)
    if tail == Tails.middle:
        Z = abs(Z)
    prob = norm.cdf(Z)
    return get_p_value_from_tail(prob, tail, debug)


def get_p_value_t_test(Z: float, ddl, tail: str, debug: bool = False):
    '''
    get p value based on student distribution T(df=ddl) with ddl degres of freedom
    if tail
        - right: return P(T > Z)
        - left: return P(T < Z)
        - middle: return P(T < -|Z|) + P(T > |Z|) => return  2*P(T > |Z|)
    '''
    # As t_dist is symetric, we dont need to compute each part of the p-value. We double the finding at the right
    '''if tail==Tails.middle:
        Z = abs(Z)
        prob_left, prob_right =  t_dist.cdf(-Z, df=ddl), t_dist.cdf(Z, df=ddl)
        return get_p_value_from_tail(prob_left, Tails.left) + get_p_value_from_tail(prob_right, Tails.right)'''
    tail = Tails.norm_tail(tail)
    if tail == Tails.middle:
        Z = abs(Z)
    prob = t_dist.cdf(Z, df=ddl)
    return get_p_value_from_tail(prob, tail, debug)


def get_p_value_f_test(Z: float, dfn: int, dfd: int, debug: bool = False):
    """get p value based on fisher distribution T(dfn, dfd) with ddl degres of freedom

    Utils
        - [F-distribution - wiki](https://en.wikipedia.org/wiki/F-distribution)
        - tail is right because Fisher is positive

    Args:
        Z (float): _description_
        dfn (int): _description_
        dfd (int): _description_
        debug (bool, optional): _description_. Defaults to False.

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """
    assert Z >= 0, "Z could nor be negative for a fisher distribution"
    tail = Tails.norm_tail("right")
    try:
        dfn = int(dfn)
        dfd = int(dfd)
    except ValueError:
        raise Exception(
            f"degre of freedom dfn and dfd should be integers. Got instead {dfd} and {dfn}"
        )

    prob = f_dist.cdf(Z, dfn, dfd)
    return get_p_value_from_tail(prob, tail, debug)


def get_p_value(Z: float, tail: str, test: str, ddl: int = None, debug=False):
    '''
    get p value based on 
        - (if test=="t_test") student distribution T(df=ddl) with ddl degres of freedom
        - (if test=="z_test") normal distribution N(0, 1)
        - (if test=="f_test") normal distribution F(ddl[0], ddl[1])

    if tail
        - right: return P(T > Z)
        - left: return P(T < Z)
        - middle: return P(T < -|Z|) + P(T > |Z|) => return  2*P(T > |Z|)
    '''
    tail = Tails.norm_tail(tail)
    if test == "z_test":
        return get_p_value_z_test(Z=Z, tail=tail, debug=debug)
    elif test == "f_test":
        assert len(ddl) == 2
        return get_p_value_f_test(Z=Z, dfn=ddl[0], dfd=ddl[1], debug=debug)
    elif test == "t_test":
        assert ddl > LIM_MIN_SAMPLE, f"your ddl ={ddl} is too low. Is it because you have a few sample size ?"
        return get_p_value_t_test(Z=Z, tail=tail, ddl=ddl, debug=debug)
    else:
        raise Exception(
            "test value is wrong. Especting either 'z_test' or 't_test' ")
