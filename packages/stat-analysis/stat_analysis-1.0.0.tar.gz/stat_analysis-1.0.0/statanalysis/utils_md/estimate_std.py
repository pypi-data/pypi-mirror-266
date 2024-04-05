from numpy import isnan, mean, sqrt, std
from numpy.linalg import norm


def estimate_std(sample):
    '''
    Instead of std, he divide by (n-1) correspondng to the std estimator used in t-test
    '''
    if isnan(sample).any():
        raise Exception(
            "encounter nan value when trying std estimation. You should hendle this properly to avoid difference of size in operations"
        )
    return std(sample, ddof=1)


def compute_slope_std(X, y, y_hat, debug=False, skipcst=True):
    # if skipcst: X = X[:,1:]

    n, nb_param = X.shape
    assert y.shape == (n, )
    assert y_hat.shape == (n, )

    X_mean = mean(X, axis=0, keepdims=True)
    assert X_mean.shape == (1, nb_param)
    assert X.shape == (n, nb_param)
    X_err = norm(X - X_mean, axis=0, keepdims=True)**2
    assert X_err.shape == (1, nb_param)

    assert y.shape == (n, )
    assert y_hat.shape == (n, )
    Y_err = norm(y - y_hat)
    if debug:
        print("X_err", X_err)
    # m = n-2 if n>2 else n
    # list of standard errors of the coefficients
    list_coeffs_std = sqrt(Y_err / X_err) / sqrt(n - 2)
    if debug:
        print("list_coeffs_std: ", list_coeffs_std)
    assert list_coeffs_std.shape == (1, nb_param)

    list_coeffs_std = list_coeffs_std.flatten()
    # list_coeffs_std[0] = 0

    return list_coeffs_std
