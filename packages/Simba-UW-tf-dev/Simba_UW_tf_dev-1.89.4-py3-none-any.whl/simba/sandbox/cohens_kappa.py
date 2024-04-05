import numpy as np
from numba import njit
from sklearn.metrics import cohen_kappa_score
import time

@njit("(int64[:],int64[:])")
def cohens_kappa(sample_1: np.ndarray, sample_2: np.ndarray):
    """
    Jitted compute Cohen's Kappa coefficient for two binary samples.

    Cohen's Kappa coefficient between classification sand ground truth taking into account agreement between classifications and ground truth occurring by chance.

    :example:
    >>> sample_1 = np.random.randint(0, 2, size=(10000,))
    >>> sample_2 = np.random.randint(0, 2, size=(10000,))
    >>> cohens_kappa(sample_1=sample_1, sample_2=sample_2))
    """
    sample_1 = np.ascontiguousarray(sample_1)
    sample_2 = np.ascontiguousarray(sample_2)
    data = np.hstack((sample_1.reshape(-1, 1), sample_2.reshape(-1, 1)))
    tp = len(np.argwhere((data[:, 0] == 1) & (data[:, 1] == 1)).flatten())
    tn = len(np.argwhere((data[:, 0] == 0) & (data[:, 1] == 0)).flatten())
    fp = len(np.argwhere((data[:, 0] == 1) & (data[:, 1] == 0)).flatten())
    fn = len(np.argwhere((data[:, 0] == 0) & (data[:, 1] == 1)).flatten())
    data = np.array(([tp, fp], [fn, tn]))
    sum0 = data.sum(axis=0)
    sum1 = data.sum(axis=1)
    expected = np.outer(sum0, sum1) / np.sum(sum0)
    w_mat = np.full(shape=(2, 2),fill_value=1)
    w_mat[0, 0] = 0
    w_mat[1, 1] = 0
    return 1 - np.sum(w_mat * data) / np.sum(w_mat * expected)





    # unique_vals = np.unique(data)
    # confusion_matrix = np.zeros((len(unique_vals), len(unique_vals)), dtype=int)
    # for i in range(len(unique_vals)):
    #     for j in range(len(unique_vals)):
    #         confusion_matrix[i, j] = np.sum((data[:, 0] == unique_vals[i]) & (data[:, 1] == unique_vals[j]))
    # n_classes = confusion_matrix.shape[0]

    # # Compute expected proportion of agreement (chance agreement)
    # total_possible_agreements = 0
    # for i in range(data.shape[0]):  # Iterate over rows
    #     for j in range(data.shape[1]):  # Iterate over columns
    #         row_total = np.sum(data[i, :])
    #         col_total = np.sum(data[:, j])
    #         total_possible_agreements += row_total * col_total
    #
    # p_e = total_possible_agreements / (tot_obs * tot_obs)
    # print(p_e)
    # kappa = (p_o - p_e) / (1 - p_e)
    # print(kappa)

# sample_1 = np.random.randint(0, 2, size=(1000000,))
# sample_2 = np.random.randint(0, 2, size=(1000000,))
#
# #sample_1 = np.array([0, 1, 0])
# #sample_2 = np.array([1, 1, 0])
# start = time.time()
# print(cohens_kappa(sample_1=sample_1, sample_2=sample_2))
# print(time.time() - start)
# start = time.time()
# print(cohen_kappa_score(y1=sample_1, y2=sample_2))
# print(time.time() - start)



#confusion_matrix()
