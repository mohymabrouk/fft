
# Manual FFT (Cooley-Tukey) + windows and helpers — NO numpy.fft usage
# Works on Python complex numbers. Uses numpy only for arrays, math for trig.
from __future__ import annotations
import math
from typing import List, Tuple
import numpy as np

def next_pow_two(n: int) -> int:
    '''Return the next power of two >= n.'''
    if n <= 1:
        return 1
    return 1 << (n - 1).bit_length()

def _bit_reverse_indices(n: int) -> List[int]:
    '''Bit-reversal permutation indices for length n (n must be power of two).'''
    bits = n.bit_length() - 1
    rev = [0] * n
    for i in range(n):
        b = '{:0{w}b}'.format(i, w=bits)
        br = int(b[::-1], 2)
        rev[i] = br
    return rev

def fft_iterative(x: List[complex]) -> List[complex]:
    '''Radix-2 Cooley-Tukey FFT (iterative). x length will be padded to power-of-two.'''
    n_orig = len(x)
    n = next_pow_two(n_orig)
    if n != n_orig:
        x = list(x) + [0j] * (n - n_orig)
    else:
        x = list(x)

    # Bit-reversal permutation
    rev = _bit_reverse_indices(n)
    a = [x[rev[i]] for i in range(n)]

    m = 2
    while m <= n:
        half = m // 2
        # principal m-th root of unity: exp(-2πi/m)
        w_m = complex(math.cos(-2*math.pi/m), math.sin(-2*math.pi/m))
        for k in range(0, n, m):
            w = 1+0j
            for j in range(half):
                t = w * a[k + j + half]
                u = a[k + j]
                a[k + j] = u + t
                a[k + j + half] = u - t
                w *= w_m
        m *= 2
    return a

def ifft_iterative(X: List[complex]) -> List[complex]:
    '''Inverse FFT via conjugate trick and scaling.'''
    n = len(X)
    conj = [complex(z.real, -z.imag) for z in X]
    y = fft_iterative(conj)
    inv = [complex(z.real/n, -z.imag/n) for z in y]
    return inv

def rfft_real(x: List[float]) -> List[complex]:
    '''Compute the non-negative frequency half of FFT for real input.'''
    X = fft_iterative([complex(v, 0.0) for v in x])
    n = len(X)
    return X[: n//2 + 1]

def rfftfreq(n: int, d: float) -> List[float]:
    '''Frequencies for rFFT bins: k/(n*d), k=0..n//2'''
    return [(k/(n*d)) for k in range(n//2 + 1)]

# Window functions (closed-form, no external DSP lib)
def window_hann(N: int) -> np.ndarray:
    if N <= 1: 
        return np.ones(N, dtype=np.float64)
    n = np.arange(N, dtype=np.float64)
    return 0.5 - 0.5 * np.cos(2.0 * math.pi * n / (N - 1))

def window_hamming(N: int) -> np.ndarray:
    if N <= 1: 
        return np.ones(N, dtype=np.float64)
    n = np.arange(N, dtype=np.float64)
    alpha = 0.54
    beta = 1.0 - alpha
    return alpha - beta * np.cos(2.0 * math.pi * n / (N - 1))

def window_blackman(N: int) -> np.ndarray:
    if N <= 1: 
        return np.ones(N, dtype=np.float64)
    n = np.arange(N, dtype=np.float64)
    a0, a1, a2 = 0.42, 0.5, 0.08
    return a0 - a1*np.cos(2.0*math.pi*n/(N-1)) + a2*np.cos(4.0*math.pi*n/(N-1))

def get_window(name: str, N: int) -> np.ndarray:
    key = (name or "rectangular").strip().lower()
    if key == "hann":
        return window_hann(N)
    if key == "hamming":
        return window_hamming(N)
    if key == "blackman":
        return window_blackman(N)
    return np.ones(N, dtype=np.float64)

def complex_angle(z: complex) -> float:
    return math.atan2(z.imag, z.real)
