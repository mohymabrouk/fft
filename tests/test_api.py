
import io, math
import numpy as np
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)

def _sine_wav_bytes(freq=440, fs=8000, dur=0.5):
    import wave
    t = np.arange(int(fs*dur))/fs
    x = 0.8*np.sin(2*math.pi*freq*t)
    x_i16 = np.clip(x*32767, -32768, 32767).astype(np.int16)
    bio = io.BytesIO()
    with wave.open(bio, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(fs)
        wf.writeframes(x_i16.tobytes())
    bio.seek(0); return bio

def test_upload_and_fft():
    bio = _sine_wav_bytes()
    files = {"file": ("test.wav", bio, "audio/wav")}
    r = client.post("/api/upload", files=files)
    assert r.status_code == 200
    sig = r.json(); assert "signal_id" in sig

    payload = {
        "signal_data": sig["time_domain"],
        "sampling_rate": sig["sampling_rate"],
        "window_size": 2048,
        "window_type": "hann",
        "filter_type": None,
        "filter_cutoff": None
    }
    r2 = client.post("/api/fft", json=payload)
    assert r2.status_code == 200
    out = r2.json()
    assert "frequencies" in out and len(out["frequencies"]) == 1025
