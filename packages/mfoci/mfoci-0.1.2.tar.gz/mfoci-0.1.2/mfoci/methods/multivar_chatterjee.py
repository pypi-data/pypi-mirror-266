import numpy as np
import pandas as pd
from scipy import stats


def nearest_neighbor_indices(data):
    """
    Find the index of the nearest neighbor for each row in the given 2D
    array using the euclidean metric.

    Parameters
    ----------
    data : array-like, shape (n_samples, n_features)

    Returns
    -------
    nearest_indices : array, shape (n_samples,)
        The index of the nearest neighbor for each row.
    """
    # Compute pairwise Euclidean distances between all rows
    distances = np.sqrt(((data[:, None] - data) ** 2).sum(axis=2))

    # Exclude self-distances (diagonal elements)
    np.fill_diagonal(distances, np.inf)

    # Find the index of the nearest neighbor for each row
    return np.argmin(distances, axis=1)


def xi_q_n_calculate(xvec, yvec):
    """
    Calculate the T^q value for given multivariate x and multivariate y.
    Implements the formula at the bottom of slide 21 in Jonathan's presentation.
    """
    xvec.reset_index(drop=True, inplace=True)
    yvec.reset_index(drop=True, inplace=True)
    q = yvec.shape[1]

    t_noms = []
    t_dens = []
    for i in range(q):
        y = yvec.iloc[:, i].values
        prev_y = yvec.iloc[:, :i]
        x = pd.concat([xvec, prev_y], axis=1).values
        t_nom = t_y_fat_x(x, y)
        if pd.isna(t_nom):
            pass
        t_noms.append(t_nom)
        if i == 0:
            t_den = 0
        else:
            t_den = t_y_fat_x(prev_y.values, y)
        if pd.isna(t_den):
            pass
        t_dens.append(t_den)
    t = 1 - (q - sum(t_noms)) / (q - sum(t_dens))
    return t


def t_y_fat_x(xvec, y):
    """
    Calculate the T^q value for given multivariate x and univariate y.
    Implements the formula at the bottom of slide 17 in Jonathan's presentation.
    """
    n = len(y)
    yrank = stats.rankdata(y, method="ordinal") - 1
    l_k = n - yrank
    nn = nearest_neighbor_indices(xvec)
    nom_prods = np.zeros(len(yrank))
    den_prods = np.zeros(len(yrank))
    for i in range(len(yrank)):
        nom_prods[i] = n * min(yrank[i], yrank[nn[i]]) - l_k[i] ** 2
        den_prods[i] = l_k[i] * (n - l_k[i])
    nom = sum(nom_prods)
    den = sum(den_prods)
    if pd.isna(den) or pd.isna(nom):
        return np.nan
    return nom / den
