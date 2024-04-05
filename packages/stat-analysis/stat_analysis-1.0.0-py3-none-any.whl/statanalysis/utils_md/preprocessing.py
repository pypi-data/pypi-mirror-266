from typing import Tuple

from numpy import array, hstack, isnan, ndarray, newaxis


def clear_list(L: list) -> ndarray:
    """remove nan from a list

    Args:
        L (list): a 1-dim array (n,). Anyway, data will be flatten

    What about he handle missing values properly !!
        - weight shit 
        - Anyway, it would be good to know how missing values removal the distribution of L

    Returns:
        1-dim array: array of shape (n,)

    Examples
    --------
    >>> A = np.array([
            [1,3],
            [4,3],
            [5,3],
            [7,np.nan]
            ])
    >>> y = np.array([6,np.nan,3,2])
    >>> A1 = clear_list(A)
    >>> y1 = clear_list(y)
    >>> print("A1: ",A1)
    A1:  array([1, 3, 4, 3, 5, 3])
    >>> print("y: ",y1)
    y:  array([6. 3. 2.])
    """
    L = array(L).flatten()
    L = L[~isnan(L)]
    return L


def clear_list_pair(L1, L2) -> Tuple[ndarray, ndarray]:
    """remove nan values (remove observation data containing nan value in L1 or L2) from 2 lists

    Args:
       L1 (list): a 1-dim array (n,). Anyway, data will be flatten
       L2 (list): a 1-dim array (n,). Anyway, data will be flatten

    What about he handle missing values properly !!
        - weight shit 
        - Anyway, it would be good to know how missing values removal the distribution of L

    Raises:
        L1 and L2 have different size: lists must be of the same size

    Returns:
        1-dim array: L1 of shape(n,)
        1-dim array: L2 of shape(n,)

    Examples
    --------
    >>> y1 = np.array([4, 8,np.nan,2])
    >>> y2 = np.array([6,np.nan,36,9])
    >>> y1,y2 = clear_list_pair(y1, y2)
    >>> print("y1: ",y1)
    y1:  array([4, 2])
    >>> print("y2: ",y2)
    y2:  array([6. 9.])
    """
    L1 = array(L1).flatten()
    L2 = array(L2).flatten()
    if len(L1) != len(L2):
        raise Exception("lists must be of the same size")

    mask = ~(isnan(L1) | isnan(L2))
    L1 = L1[mask]
    L2 = L2[mask]

    if len(L1) != len(L2):
        raise Exception("internal pb")

    return L1, L2


def clear_mat_vec(A, y) -> Tuple[ndarray, ndarray]:
    """Remove nan values (remove observation data containing nan value in X or y) from a matric and a corresponding vector


    Parameters
    ----------
    A : 2-dimensional array (n,p)
    y: 1-dimensional array (n,)

    Others
    ----------
    What about he handle missing values properly !!
        - weight shit 
        - Anyway, it would be good to know how missing values removal the distribution of L

    Raises
    ---------
        L1 and L2 have different size: lists must be of the same size

    Returns
    -----------
        1-dim array: L1 of shape(n,)
        1-dim array: L2 of shape(n,)

    Examples
    --------
    >>> A = np.array([
            [1,3],
            [4,3],
            [5,3],
            [7,np.nan]
            ])
    >>> y = np.array([6,np.nan,3,2])
    >>> A1,y1 = clear_mat_vec(A,y)
    >>> print("A1: ",A1)
    A1:  [[1. 3.]
         [5. 3.]]
    >>> print("y: ",y1)
    y:  [6. 3.]
    """
    A = array(A)
    y = array(y)
    assert A.ndim == 2, "ndim1"
    assert y.ndim == 1, "ndim2"
    assert A.shape[0] == y.shape[0], "eeee"

    y1 = y[:, newaxis]
    M = hstack((A, y1))

    mask = ~isnan(M).any(axis=1)
    M = M[mask]

    A1 = M[:, :-1]
    y1 = M[:, -1]

    assert A1.ndim == 2, "internal error 1"
    assert y1.ndim == 1, "internal error 2"
    assert A1.shape[0] == y1.shape[0], "internal error 3"
    assert A1.shape[1] == A.shape[1], "internal error 3"
    return A1, y1
