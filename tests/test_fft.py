
import math
import numpy as np
from server.dsp.fft import fft_iterative, ifft_iterative, rfft_real, rfftfreq

def test_fft_ifft_roundtrip():
    fs = 8000
    t = np.arange(0, 0.01, 1/fs)
    x = np.sin(2*math.pi*1000*t) + 0.5*np.sin(2*math.pi*2000*t)
    X = fft_iterative([complex(v, 0) for v in x.tolist()])
    x_rec = ifft_iterative(X)
    x_rec = np.array([z.real for z in x_rec[:len(x)]], dtype=np.float64)
    x_norm = x / (np.max(np.abs(x)) + 1e-12)
    x_rec_norm = x_rec / (np.max(np.abs(x_rec)) + 1e-12)
    err = np.max(np.abs(x_norm - x_rec_norm))
    assert err < 1e-6

def test_rfft_detects_peak_freq():
    fs = 16000
    f0 = 1500
    N = 4096
    t = np.arange(N)/fs
    x = np.sin(2*math.pi*f0*t)
    X = rfft_real(x.tolist())
    mags = np.array([abs(z) for z in X])
    freqs = np.array(rfftfreq(len(x), 1/fs))
    k = int(np.argmax(mags))
    f_peak = freqs[k]
    assert abs(f_peak - f0) <= fs/N
