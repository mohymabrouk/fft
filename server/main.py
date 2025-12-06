
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse, Response
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import numpy as np
from datetime import datetime
import uuid, os, io
from PIL import Image
try:
    import cv2
    OPENCV_AVAILABLE = True
except Exception:
    OPENCV_AVAILABLE = False

from dsp.fft import rfft_real, rfftfreq, get_window, complex_angle
from dsp.filters import design_lowpass_fir, design_highpass_fir, design_bandpass_fir, apply_fir

APP_VERSION = "1.2.0"

STORAGE_DIR = os.environ.get("STORAGE_DIR", os.path.join(os.path.dirname(__file__), "..", "storage"))
AUDIO_DIR = os.path.join(STORAGE_DIR, "audio")
IMAGE_DIR = os.path.join(STORAGE_DIR, "images")
ANALYSIS_DIR = os.path.join(STORAGE_DIR, "analyses")

for p in [STORAGE_DIR, AUDIO_DIR, IMAGE_DIR, ANALYSIS_DIR]:
    os.makedirs(p, exist_ok=True)

app = FastAPI(
    title="FFT Signal & Image Analyzer API",
    description="Manual FFT, audio processing, and image compression/registration",
    version=APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FFTRequest(BaseModel):
    signal_data: List[float] = Field(..., description="Signal amplitude values")
    sampling_rate: int = Field(44100, description="Sampling rate in Hz")
    window_size: int = Field(2048, ge=256, le=8192, description="FFT window size")
    window_type: str = Field("hann", description="Window function type")
    filter_type: Optional[str] = Field(None, description="Filter type: lowpass, highpass, bandpass")
    filter_cutoff: Optional[List[float]] = Field(None, description="Filter cutoff frequency/frequencies")

class SignalResponse(BaseModel):
    signal_id: str
    time_domain: List[float]
    sampling_rate: int
    duration: float
    num_samples: int
    filename: Optional[str]

class FFTResponse(BaseModel):
    analysis_id: str
    frequencies: List[float]
    magnitudes: List[float]
    phases: List[float]
    window_size: int
    sampling_rate: int

class AnalysisMetadata(BaseModel):
    id: str
    timestamp: str
    filename: Optional[str]
    sampling_rate: int
    duration: float
    window_size: int

class ImageUploadResponse(BaseModel):
    image_id: str
    filename: str
    width: int
    height: int

class ImageCompressRequest(BaseModel):
    image_id: str
    quality: int = Field(75, ge=1, le=95)
    subsampling: int = Field(2, ge=0, le=2)

class ImageRegisterRequest(BaseModel):
    ref_image_id: str
    mov_image_id: str
    max_features: int = 800
    good_match_percent: float = Field(0.15, ge=0.02, le=0.9)

analysis_history: List[Dict[str, Any]] = []
stored_analyses: Dict[str, Dict[str, Any]] = {}
stored_images: Dict[str, Dict[str, Any]] = {}
compressed_cache: Dict[str, Dict[str, Any]] = {}

def _save_wav_int16(path: str, samples: np.ndarray, fs: int):
    import wave
    max_abs = float(np.max(np.abs(samples))) if samples.size else 0.0
    sig = samples.copy().astype(np.float64)
    if max_abs > 1e-12:
        sig = sig / max_abs
    sig_i16 = np.clip(sig * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(fs)
        wf.writeframes(sig_i16.tobytes())

def _read_wav_any(file_bytes: bytes):
    import wave
    with io.BytesIO(file_bytes) as bio:
        with wave.open(bio, 'rb') as wf:
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            fr = wf.getframerate()
            n_frames = wf.getnframes()
            if sampwidth != 2:
                raise HTTPException(status_code=400, detail="Only 16-bit PCM WAV is supported")
            pcm = wf.readframes(n_frames)
    data = np.frombuffer(pcm, dtype=np.int16)
    if n_channels == 2:
        data = data.reshape(-1, 2).mean(axis=1).astype(np.int16)
    x = (data.astype(np.float32) / 32768.0).astype(np.float64)
    return fr, x

@app.get("/")
def read_root():
    return { "message": "FFT Signal & Image Analyzer API", "version": APP_VERSION, "docs": "/docs" }

@app.post("/api/upload", response_model=SignalResponse)
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        signal_id = str(uuid.uuid4())
        filename = file.filename or "upload"
        if filename.lower().endswith('.wav'):
            sampling_rate, data = _read_wav_any(contents)
        elif filename.lower().endswith('.csv'):
            arr = np.loadtxt(io.BytesIO(contents), delimiter=',')
            if arr.ndim == 2 and arr.shape[1] == 2:
                data = arr[:, 1].astype(np.float64)
                dt = float(np.mean(np.diff(arr[:, 0])))
                sampling_rate = int(1.0 / dt) if dt > 0 else 44100
            else:
                data = arr.astype(np.float64); sampling_rate = 44100
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format (use .wav 16-bit or .csv)")
        duration = len(data) / float(sampling_rate)
        stored_analyses[signal_id] = {
            "data": data.tolist(), "sampling_rate": sampling_rate, "filename": filename,
            "timestamp": datetime.utcnow().isoformat()
        }
        wav_path = os.path.join(AUDIO_DIR, f"{signal_id}.wav")
        _save_wav_int16(wav_path, data, sampling_rate)
        return SignalResponse(signal_id=signal_id, time_domain=data.tolist(), sampling_rate=int(sampling_rate),
                              duration=float(duration), num_samples=int(len(data)), filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/api/fft", response_model=FFTResponse)
async def compute_fft(request: FFTRequest):
    try:
        signal_data = np.array(request.signal_data, dtype=np.float64)
        fs = float(request.sampling_rate)
        Nw = int(request.window_size)
        if request.filter_type and request.filter_cutoff:
            if request.filter_type == "lowpass":
                h = design_lowpass_fir(request.filter_cutoff[0], fs, numtaps=201)
            elif request.filter_type == "highpass":
                h = design_highpass_fir(request.filter_cutoff[0], fs, numtaps=201)
            elif request.filter_type == "bandpass" and len(request.filter_cutoff) == 2:
                h = design_bandpass_fir(float(request.filter_cutoff[0]), float(request.filter_cutoff[1]), fs, numtaps=401)
            else:
                h = None
            if h is not None:
                signal_data = apply_fir(signal_data, h)
        w = get_window(request.window_type, Nw)
        if len(signal_data) < Nw:
            pad = np.zeros(Nw, dtype=np.float64)
            pad[: len(signal_data)] = signal_data
            seg = pad * w
        else:
            seg = signal_data[:Nw] * w
        X_pos = rfft_real(seg.tolist())
        magnitudes = [abs(z) for z in X_pos]
        phases = [complex_angle(z) for z in X_pos]
        freqs = rfftfreq(len(seg), 1.0/fs)
        analysis_id = str(uuid.uuid4())
        analysis_metadata = {
            "id": analysis_id, "timestamp": datetime.utcnow().isoformat(),
            "sampling_rate": request.sampling_rate, "window_size": request.window_size,
            "frequencies": list(map(float, freqs)),
            "magnitudes": list(map(float, magnitudes)),
            "phases": list(map(float, phases)),
            "processed_signal": signal_data.tolist(),
            "filter_type": request.filter_type, "filter_cutoff": request.filter_cutoff
        }
        stored_analyses[analysis_id] = analysis_metadata
        analysis_history.append({
            "id": analysis_id, "timestamp": analysis_metadata["timestamp"],
            "sampling_rate": request.sampling_rate, "window_size": request.window_size
        })
        os.makedirs(ANALYSIS_DIR, exist_ok=True)
        with open(os.path.join(ANALYSIS_DIR, f"{analysis_id}.json"), "w", encoding="utf-8") as f:
            import json; json.dump(analysis_metadata, f, ensure_ascii=False, indent=2)
        return FFTResponse(analysis_id=analysis_id, frequencies=analysis_metadata["frequencies"],
                           magnitudes=analysis_metadata["magnitudes"], phases=analysis_metadata["phases"],
                           window_size=request.window_size, sampling_rate=request.sampling_rate)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FFT computation error: {str(e)}")

@app.get("/api/audio/original/{signal_id}")
async def get_original_audio(signal_id: str):
    wav_path = os.path.join(AUDIO_DIR, f"{signal_id}.wav")
    if not os.path.exists(wav_path):
        raise HTTPException(status_code=404, detail="Signal not found")
    return FileResponse(wav_path, media_type="audio/wav", filename=f"original_{signal_id[:8]}.wav")

@app.get("/api/audio/processed/{analysis_id}")
async def get_processed_audio(analysis_id: str):
    if analysis_id not in stored_analyses:
        raise HTTPException(status_code=404, detail=f"Analysis not found: {analysis_id}")
    analysis = stored_analyses[analysis_id]
    if "processed_signal" not in analysis:
        raise HTTPException(status_code=404, detail="Processed signal not found")
    fs = int(analysis["sampling_rate"])
    y = np.array(analysis["processed_signal"], dtype=np.float64)
    wav_path = os.path.join(AUDIO_DIR, f"processed_{analysis_id}.wav")
    _save_wav_int16(wav_path, y, fs)
    return FileResponse(wav_path, media_type="audio/wav", filename=f"processed_{analysis_id[:8]}.wav")

@app.get("/api/history", response_model=List[AnalysisMetadata])
def get_history():
    return analysis_history[-100:]

@app.get("/api/download/{analysis_id}")
async def download_analysis(analysis_id: str, format: str = "csv"):
    if analysis_id not in stored_analyses:
        path = os.path.join(ANALYSIS_DIR, f"{analysis_id}.json")
        if os.path.exists(path):
            import json
            with open(path, "r", encoding="utf-8") as f:
                analysis = json.load(f)
        else:
            raise HTTPException(status_code=404, detail="Analysis not found")
    else:
        analysis = stored_analyses[analysis_id]
    if format == "csv":
        lines = ["Frequency (Hz),Magnitude,Phase"]
        for f0, mag, ph in zip(analysis["frequencies"], analysis["magnitudes"], analysis["phases"]):
            lines.append(f"{f0},{mag},{ph}")
        csv_content = "\\n".join(lines)
        filename = f"fft_analysis_{analysis_id}.csv"
        return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})
    else:
        return JSONResponse(content=analysis)

@app.post("/api/image/upload")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        im = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}")
    image_id = str(uuid.uuid4())
    orig_path = os.path.join(IMAGE_DIR, f"{image_id}_orig.jpg")
    im.save(orig_path, format="JPEG", quality=95, subsampling=0)
    stored_images[image_id] = {
        "id": image_id, "filename": file.filename or "image", "orig_path": orig_path,
        "width": im.width, "height": im.height, "timestamp": datetime.utcnow().isoformat()
    }
    return JSONResponse({"image_id": image_id, "filename": file.filename or "image", "width": im.width, "height": im.height})

@app.get("/api/image/view/{image_id}")
async def view_image(image_id: str):
    meta = stored_images.get(image_id)
    if not meta: raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(meta["orig_path"], media_type="image/jpeg", filename=os.path.basename(meta["orig_path"]))

@app.post("/api/image/compress")
async def compress_image(payload: dict):
    image_id = payload.get("image_id"); quality = int(payload.get("quality", 75)); subsampling = int(payload.get("subsampling", 2))
    meta = stored_images.get(image_id)
    if not meta: raise HTTPException(status_code=404, detail="Image not found")
    im = Image.open(meta["orig_path"]).convert("RGB")
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=quality, subsampling=subsampling, optimize=True)
    buf.seek(0)
    comp_id = f"{image_id}_q{quality}_s{subsampling}"
    comp_path = os.path.join(IMAGE_DIR, f"{comp_id}.jpg")
    with open(comp_path, "wb") as f: f.write(buf.getvalue())
    compressed_cache[comp_id] = { "image_id": image_id, "path": comp_path, "size_bytes": os.path.getsize(comp_path), "quality": quality, "subsampling": subsampling }
    return JSONResponse({ "compressed_id": comp_id, "url": f"/api/image/get/{comp_id}", "size_bytes": compressed_cache[comp_id]["size_bytes"], "width": meta["width"], "height": meta["height"] })

@app.get("/api/image/get/{comp_id}")
async def get_compressed(comp_id: str):
    meta = compressed_cache.get(comp_id)
    if not meta:
        path = os.path.join(IMAGE_DIR, f"{comp_id}.jpg")
        if not os.path.exists(path): raise HTTPException(status_code=404, detail="Compressed image not found")
        return FileResponse(path, media_type="image/jpeg")
    return FileResponse(meta["path"], media_type="image/jpeg")

@app.post("/api/image/features")
async def image_features(image_id: str):
    meta = stored_images.get(image_id)
    if not meta: raise HTTPException(status_code=404, detail="Image not found")
    if not OPENCV_AVAILABLE: raise HTTPException(status_code=503, detail="OpenCV is not installed on the server")
    img = cv2.imread(meta["orig_path"], cv2.IMREAD_COLOR)
    if img is None: raise HTTPException(status_code=400, detail="Failed to open image")
    orb = cv2.ORB_create(nfeatures=800)
    kps, des = orb.detectAndCompute(img, None)
    out = cv2.drawKeypoints(img, kps, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    out_path = os.path.join(IMAGE_DIR, f"{image_id}_features.jpg")
    cv2.imwrite(out_path, out)
    pts = [{"x": float(k.pt[0]), "y": float(k.pt[1])} for k in kps]
    return JSONResponse({"keypoints": pts, "count": len(pts), "overlay_url": f"/api/image/overlay/{image_id}"})

@app.get("/api/image/overlay/{image_id}")
async def image_overlay(image_id: str):
    path = os.path.join(IMAGE_DIR, f"{image_id}_features.jpg")
    if not os.path.exists(path): raise HTTPException(status_code=404, detail="No overlay for this image")
    return FileResponse(path, media_type="image/jpeg")

@app.post("/api/image/register")
async def image_register(payload: dict):
    if not OPENCV_AVAILABLE: raise HTTPException(status_code=503, detail="OpenCV is not installed on the server")
    ref_image_id = payload.get("ref_image_id"); mov_image_id = payload.get("mov_image_id")
    max_features = int(payload.get("max_features", 800))
    good_match_percent = float(payload.get("good_match_percent", 0.15))
    m_ref = stored_images.get(ref_image_id); m_mov = stored_images.get(mov_image_id)
    if not m_ref or not m_mov: raise HTTPException(status_code=404, detail="One of the images was not found")
    img1 = cv2.imread(m_ref["orig_path"], cv2.IMREAD_COLOR)
    img2 = cv2.imread(m_mov["orig_path"], cv2.IMREAD_COLOR)
    if img1 is None or img2 is None: raise HTTPException(status_code=400, detail="Failed to open images")
    orb = cv2.ORB_create(nfeatures=max_features)
    k1, d1 = orb.detectAndCompute(img1, None); k2, d2 = orb.detectAndCompute(img2, None)
    if d1 is None or d2 is None: raise HTTPException(status_code=400, detail="Could not compute descriptors")
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    matches = matcher.match(d1, d2); matches = sorted(matches, key=lambda m: m.distance)
    num_good = max(4, int(len(matches) * good_match_percent)); matches = matches[:num_good]
    import numpy as np
    pts1 = np.float32([k1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    pts2 = np.float32([k2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    H, mask = cv2.findHomography(pts2, pts1, cv2.RANSAC)
    if H is None: raise HTTPException(status_code=400, detail="Homography estimation failed")
    h, w = img1.shape[:2]
    aligned = cv2.warpPerspective(img2, H, (w, h))
    out_id = f"{mov_image_id}_aligned_to_{ref_image_id}"
    out_path = os.path.join(IMAGE_DIR, f"{out_id}.jpg"); cv2.imwrite(out_path, aligned)
    return JSONResponse({"registered_id": out_id, "url": f"/api/image/aligned/{out_id}"})

@app.get("/api/image/aligned/{out_id}")
async def get_aligned(out_id: str):
    path = os.path.join(IMAGE_DIR, f"{out_id}.jpg")
    if not os.path.exists(path): raise HTTPException(status_code=404, detail="Aligned image not found")
    return FileResponse(path, media_type="image/jpeg")


@app.post("/api/video/mjpeg")
async def video_mjpeg(payload: dict):

    try:
        import cv2, numpy as np, os, uuid
    except Exception:
        raise HTTPException(status_code=503, detail="OpenCV is not installed on the server")
    image_ids = payload.get("image_ids") or []
    fps = float(payload.get("fps", 10))
    if len(image_ids) < 2: raise HTTPException(status_code=400, detail="Provide at least two images")
    frames = []
    for iid in image_ids:
        meta = stored_images.get(iid)
        if not meta: raise HTTPException(status_code=404, detail=f"Image not found: {iid}")
        img = cv2.imread(meta["orig_path"], cv2.IMREAD_COLOR)
        if img is None: raise HTTPException(status_code=400, detail=f"Could not read image: {iid}")
        frames.append(img)
    h, w = frames[0].shape[:2]
    out_id = f"vid_{uuid.uuid4().hex[:8]}"
    out_path = os.path.join(IMAGE_DIR, f"{out_id}.avi")
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    vw = cv2.VideoWriter(out_path, fourcc, fps, (w, h))
    for fr in frames:
        if fr.shape[:2] != (h, w):
            fr = cv2.resize(fr, (w, h))
        vw.write(fr)
    vw.release()
    return JSONResponse({ "video_id": out_id, "url": f"/api/video/get/{out_id}", "codec": "MJPG", "fps": fps, "ext": ".avi" })

@app.get("/api/video/get/{vid_id}")
async def get_video(vid_id: str):
    path = os.path.join(IMAGE_DIR, f"{vid_id}.avi")
    if not os.path.exists(path): raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(path, media_type="video/avi", filename=f"{vid_id}.avi")

@app.get("/api/info")
def get_api_info():
    return {
        "server": "FFT & Image Analyzer API", "version": APP_VERSION,
        "supported_formats": [".wav (16-bit PCM)", ".csv", ".jpg", ".png"],
        "max_window_size": 8192, "min_window_size": 256,
        "supported_filters": ["lowpass", "highpass", "bandpass"],
        "window_types": ["hann", "hamming", "blackman", "rectangular"],
        "opencv_available": OPENCV_AVAILABLE
    }

@app.post("/api/mic/record")
async def handle_microphone_recording(file: UploadFile = File(...)):
    return await upload_file(file)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
