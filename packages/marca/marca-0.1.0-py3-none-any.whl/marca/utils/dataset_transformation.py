import numpy as np


def transform_to_sequential(x, y):
    """
    Transform the data to a sequential representation
    :param x:
    :return:
    """
    data_transformed = np.hstack((x, y.reshape(-1, 1))).astype(int)

    acc = 0
    len_ant = 0
    reverser = {}
    for c in range(data_transformed.shape[1]):
        acc += len_ant
        values = np.unique(data_transformed[:, c])
        reverser.update(dict(zip([x for x in values + acc], tuple(zip([c] * len(values), values)))))
        len_ant = len(values)
        data_transformed[:, c] = data_transformed[:, c] + acc

    return data_transformed


def transform_to_sparse_data(data):
    sparse_data = np.zeros(shape=(len(data), len(np.unique(data))), dtype=np.bool_)

    for idx, d in enumerate(data):
        sparse_data[idx, d] = True

    return sparse_data