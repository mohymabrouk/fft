
from __future__ import annotations
import math
import numpy as np

def _sinc(x: float) -> float:
    if abs(x) < 1e-8:
        return 1.0
    return math.sin(math.pi*x)/(math.pi*x)

def _hann(N: int) -> np.ndarray:
    if N <= 1: 
        return np.ones(N, dtype=np.float64)
    n = np.arange(N, dtype=np.float64)
    return 0.5 - 0.5*np.cos(2.0*math.pi*n/(N-1))

def design_lowpass_fir(cutoff_hz: float, fs: float, numtaps: int = 101) -> np.ndarray:
    if cutoff_hz <= 0:
        h = np.zeros(numtaps, dtype=np.float64); h[numtaps//2] = 0.0; return h
    if cutoff_hz >= fs/2.0:
        h = np.zeros(numtaps, dtype=np.float64); h[numtaps//2] = 1.0; return h
    fc = cutoff_hz / fs
    M = numtaps - 1
    n = np.arange(numtaps) - M/2.0
    h = 2.0*fc * np.array([_sinc(2.0*fc*ni) for ni in n], dtype=np.float64)
    w = _hann(numtaps)
    h = h * w
    h = h / np.sum(h)
    return h

def design_highpass_fir(cutoff_hz: float, fs: float, numtaps: int = 101) -> np.ndarray:
    lp = design_lowpass_fir(cutoff_hz, fs, numtaps=numtaps)
    hp = -lp
    hp[numtaps//2] += 1.0
    return hp

def design_bandpass_fir(low_hz: float, high_hz: float, fs: float, numtaps: int = 101) -> np.ndarray:
    if low_hz >= high_hz:
        raise ValueError("low_hz must be < high_hz")
    lp_high = design_lowpass_fir(high_hz, fs, numtaps=numtaps)
    lp_low  = design_lowpass_fir(low_hz,  fs, numtaps=numtaps)
    bp = lp_high - lp_low
    s = np.sum(bp)
    if abs(s) > 1e-8:
        bp = bp / s
    return bp

def apply_fir(x: np.ndarray, h: np.ndarray) -> np.ndarray:
    y = np.convolve(x, h, mode="same")
    return y.astype(np.float64, copy=False)
