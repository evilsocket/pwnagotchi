import numpy as np


def normalize(v, min_v, max_v):
    return (v - min_v) / (max_v - min_v)


def as_batches(x, y, batch_size, shuffle=True):
    x_size = len(x)
    assert x_size == len(y)

    indices = np.random.permutation(x_size) if shuffle else None

    for offset in range(0, x_size - batch_size + 1, batch_size):
        excerpt = indices[offset:offset + batch_size] if shuffle else slice(offset, offset + batch_size)
        yield x[excerpt], y[excerpt]
