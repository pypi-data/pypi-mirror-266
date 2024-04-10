import numpy as np
from multiprocessing.shared_memory import SharedMemory
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool
from itertools import product
from functools import partial

# Constants
# Miller index of reflection
H = 0
# Miller index of reflection
K = 4
# Number of unit cells per direction
N = 32
# Defines how many points are needed to describe a single Laue fringe (2 = Nyquist frequency)
oversampling = 3

# Radius of the crystal
R = N/2

# Maximum strain at surface
e0 = 0.01
# Width of the strain profile below the surface
w = 5.

# Generate real and reciprocal space coordinates
n = np.arange(N)
m = np.arange(N)
h = np.arange(H-0.5, H+0.5, 1./(oversampling*N))
k = np.arange(K-0.5, K+0.5, 1./(oversampling*N))


# Displacement of atoms as function of the radius
def delta(radius, crystal_radius, strain_width):
    """Displacement of atoms as function of the radius"""
    return 1 + np.tanh((radius - crystal_radius) / strain_width)



def circ_numpy_2(N, h, k):
    R, C = np.indices((N, N))
    radius = np.sqrt((R - N/2.)**2 + (C - N/2.)**2)
    support = radius**2 <= (N/2)**2
    Delta = delta(radius, N/2, w)
    delta_n = e0 * (n - N/2) * Delta
    delta_n_n = n + delta_n
    delta_m_m = delta_n_n.T

    res = np.zeros((h.size, k.size))
    for hk in product(enumerate(h), enumerate(k)):
        (i_h, v_h), (i_k, v_k) = hk
        res[i_h, i_k] = np.abs(np.sum(
            support * np.exp(2j * np.pi * (v_h*delta_n_n + v_k*delta_m_m))
        ))**2
    return res


def compute_image_part(my_part, N, h, k):
    (start_x, end_x), (start_y, end_y) = my_part

    # Retrieve shared arrays
    my_s_support = SharedMemory(create=False, name="support")
    my_support = np.ndarray((N, N), dtype=np.float64, buffer=my_s_support.buf)

    my_s_delta_n_n = SharedMemory(create=False, name="delta_n_n")
    my_delta_n_n = np.ndarray((N, N), dtype=np.float64, buffer=my_s_delta_n_n.buf)
    my_delta_m_m = my_delta_n_n.T

    my_s_result = SharedMemory(create=False, name="result")
    my_result = np.ndarray((h.size, k.size), dtype=np.float64, buffer=my_s_result.buf)

    # Compute on a partial set of reciprocal coordinates
    for i_h, i_k in product(range(start_y, end_y), range(start_x, end_x)):
        v_h = h[i_h]
        v_k = k[i_k]
        my_result[i_h, i_k] = np.abs(np.sum(my_support * np.exp(2j * np.pi * (v_h*my_delta_n_n + v_k*my_delta_m_m))))**2


def circ_mp(N, h, k):
    R, C = np.indices((N, N))
    radius = np.sqrt((R - N/2.)**2 + (C - N/2.)**2)
    # support = radius**2 <= (N/2)**2
    Delta = delta(radius, N/2, w)
    delta_n = e0 * (n - N/2) * Delta
    # delta_n_n = n + delta_n
    # delta_m_m = delta_n_n.T

    parts_1D = [(0, h.size//2), (h.size//2, h.size)]
    parts = list(product(parts_1D, parts_1D))

    try:
        # Create shared arrays
        s_support = SharedMemory(create=True, size=N*N*np.dtype(np.float64).itemsize, name="support")
        support = np.ndarray((N, N), dtype=np.float64, buffer=s_support.buf)
        support[:] = radius**2 <= (N/2)**2

        s_delta_n_n = SharedMemory(create=True, size=support.nbytes, name="delta_n_n")
        delta_n_n = np.ndarray((N, N), dtype=np.float64, buffer=s_delta_n_n.buf)
        delta_n_n[:] = n + delta_n

        s_result = SharedMemory(
            create=True, size=h.size * k.size * np.dtype(np.float64).itemsize, name="result"
        )
        result = np.ndarray((h.size, k.size), dtype=np.float64, buffer=s_result.buf)
        result[:] = 0.

        # Dispatch computations
        with Pool(4) as p:
            p.map(partial(compute_image_part, N=N, h=h, k=k), parts)

    finally:
        res = result.copy()
        for s_array in [s_support, s_delta_n_n, s_result]:
            s_array.unlink()

    return res







def circ_mt(N, h, k):
    R, C = np.indices((N, N))
    radius = np.sqrt((R - N/2.)**2 + (C - N/2.)**2)
    support = radius**2 <= (N/2)**2
    Delta = delta(radius, N/2, w)
    delta_n = e0 * (n - N/2) * Delta
    delta_n_n = n + delta_n
    delta_m_m = delta_n_n.T

    parts_1D = [(0, h.size//2), (h.size//2, h.size)]
    parts = list(product(parts_1D, parts_1D))

    result = np.zeros((h.size, k.size), dtype=np.float64)

    def compute_image_part(my_part):
        (start_x, end_x), (start_y, end_y) = my_part
        # Compute on a partial set of reciprocal coordinates
        for i_h, i_k in product(range(start_y, end_y), range(start_x, end_x)):
            v_h = h[i_h]
            v_k = k[i_k]
            result[i_h, i_k] = np.abs(np.sum(
                support * np.exp(2j * np.pi * (v_h*delta_n_n + v_k*delta_m_m))
            ))**2

    with ThreadPool(4) as tp:
        tp.map(compute_image_part, parts)


    return result
















from matplotlib.pyplot import subplots
from matplotlib.colors import LogNorm
def display(result):
    "Display the array"
    fig, ax = subplots()
    fig.suptitle("Bragg peak")
    ax.imshow(result.T, extent=(h.min(), h.max(), k.min(), k.max()), norm=LogNorm(), origin = 'lower')
    ax.set_xlabel('H');
    ax.set_ylabel('K')
    ax.set_title("Crystal")



def circ_einsum(N, h, k):
    R, C = np.indices((N, N))
    radius = np.sqrt((R - N/2.)**2 + (C - N/2.)**2)
    support = radius**2 <= (N/2)**2
    Delta = delta(radius, N/2, w)
    delta_n = e0 * (n - N/2) * Delta
    delta_n_n = n + delta_n
    delta_m_m = delta_n_n.T

    tmp1 = np.exp(2j*pi*np.einsum("i,jk", h, delta_n_n))
    tmp2 = np.exp(2j*pi*np.einsum("i,jk", k, delta_m_m))
    res = np.abs(np.einsum("jk,ijk,ljk->il", support, tmp1, tmp2))**2

    return res
