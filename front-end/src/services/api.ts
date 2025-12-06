import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({ baseURL: API_BASE_URL, headers: { 'Content-Type': 'application/json' } })

export interface SignalData { signal_id: string; time_domain: number[]; sampling_rate: number; duration: number; num_samples: number; filename?: string }
export interface FFTRequest { signal_data: number[]; sampling_rate: number; window_size: number; window_type: string; filter_type?: string; filter_cutoff?: number[] }
export interface FFTResult { analysis_id: string; frequencies: number[]; magnitudes: number[]; phases: number[]; window_size: number; sampling_rate: number }
export interface AnalysisHistory { id: string; timestamp: string; sampling_rate: number; window_size: number }
export interface ImageUpload { image_id: string; filename: string; width: number; height: number }

export const api = {
  async uploadFile(file: File): Promise<SignalData> {
    const formData = new FormData(); formData.append('file', file)
    const { data } = await apiClient.post('/api/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    return data
  },
  async computeFFT(req: FFTRequest): Promise<FFTResult> {
    const { data } = await apiClient.post('/api/fft', req); return data
  },
  async getHistory(): Promise<AnalysisHistory[]> {
    const { data } = await apiClient.get('/api/history'); return data
  },
  async downloadAnalysis(analysisId: string, format: string = 'csv'): Promise<any> {
    const { data } = await apiClient.get(`/api/download/${analysisId}?format=${format}`, { responseType: format === 'csv' ? 'blob' : 'json' })
    return data
  },
  async uploadImage(file: File): Promise<ImageUpload> {
    const formData = new FormData(); formData.append('file', file)
    const { data } = await apiClient.post('/api/image/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    return data
  },
  async compressImage(image_id: string, quality: number, subsampling: number = 2): Promise<any> {
    const { data } = await apiClient.post('/api/image/compress', { image_id, quality, subsampling }); return data
  },
  async features(image_id: string): Promise<any> {
    const { data } = await apiClient.post('/api/image/features', null, { params: { image_id } }); return data
  },
  async register(ref_image_id: string, mov_image_id: string, max_features = 800, good_match_percent = 0.15): Promise<any> {
    const { data } = await apiClient.post('/api/image/register', { ref_image_id, mov_image_id, max_features, good_match_percent }); return data
  },
  async makeMjpeg(image_ids: string[], fps: number = 10): Promise<any> {
    const { data } = await apiClient.post('/api/video/mjpeg', { image_ids, fps })
    return data
  }
}
