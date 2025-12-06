<template>
  <div class="analysis-page">
    <div class="header">
      <h1>Analysis</h1>
      <div class="actions">
        <button @click="exportData('csv')" :disabled="!store.hasFFT" class="btn-export">Export CSV</button>
        <button @click="exportData('json')" :disabled="!store.hasFFT" class="btn-export">Export JSON</button>
      </div>
    </div>

    <div class="analysis-grid">
      <div class="panel-container">
        <SignalPlot v-if="store.currentSignal" :signal-data="fullSignalData" :sampling-rate="store.currentSignal.sampling_rate" />
        <AudioPlayer v-if="store.currentSignal" :audio-url="originalAudioUrl" :download-url="originalAudioUrl" title="Original Signal" />
      </div>
      <div class="panel-container">
        <FFTPlot v-if="store.hasFFT" :frequencies="store.currentFFT!.frequencies" :magnitudes="store.currentFFT!.magnitudes" />
        <div v-else class="placeholder"><p>Run FFT analysis to view frequency spectrum</p></div>
        <AudioPlayer v-if="store.hasFFT" :audio-url="processedAudioUrl" :download-url="processedAudioUrl" title="Processed Signal" />
      </div>
    </div>

    <div class="controls-section">
      <ControlPanel @run-fft="handleRunFFT" />
    </div>

    <div v-if="isProcessing" class="loading-overlay">
      <div class="spinner"></div>
      <p>Computing FFT...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useFFTStore } from '../stores/fftStore'
import { api } from '../services/api'
import SignalPlot from '../components/SignalPlot.vue'
import FFTPlot from '../components/FFTPlot.vue'
import ControlPanel from '../components/ControlPanel.vue'
import AudioPlayer from '../components/AudioPlayer.vue'

const store = useFFTStore()
const isProcessing = ref(false)
const fullSignalData = ref<number[]>([])
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

if (store.currentSignal) { fullSignalData.value = store.currentSignal.time_domain }

const originalAudioUrl = computed(() => {
  if (!store.currentSignal) return null
  return `${API_BASE_URL}/api/audio/original/${store.currentSignal.signal_id}`
})
const processedAudioUrl = computed(() => {
  if (!store.currentFFT) return null
  return `${API_BASE_URL}/api/audio/processed/${store.currentFFT.analysis_id}`
})

const handleRunFFT = async () => {
  if (!store.currentSignal) return
  try {
    isProcessing.value = true
    const signalData = store.currentSignal.time_domain
    const fftRequest = { ...store.fftParams, signal_data: signalData, sampling_rate: store.currentSignal.sampling_rate }
    const result = await api.computeFFT(fftRequest)
    store.setFFT(result)
  } catch (error: any) {
    console.error('FFT computation failed:', error)
    store.setError(error.message)
  } finally {
    isProcessing.value = false
  }
}

const exportData = async (format: string) => {
  if (!store.currentFFT) return
  try {
    const data = await api.downloadAnalysis(store.currentFFT.analysis_id, format)
    if (format === 'csv') {
      const blob = new Blob([data], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url; a.download = `fft_analysis_${store.currentFFT.analysis_id}.csv`; a.click()
    } else {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url; a.download = `fft_analysis_${store.currentFFT.analysis_id}.json`; a.click()
    }
  } catch (error) { console.error('Export failed:', error) }
}
</script>

<style scoped>
.analysis-page { max-width: 1400px; margin: 0 auto; padding: 0 2rem; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--color-border); }
.header h1 { color: var(--color-text); font-size: 2rem; font-weight: 600; letter-spacing: -0.02em; }
.actions { display: flex; gap: 1rem; }
.btn-export { padding: 0.625rem 1.25rem; background: var(--color-primary); color: var(--color-bg); border: none; border-radius: 4px; cursor: pointer; transition: all 0.2s; font-size: 0.875rem; font-weight: 500; letter-spacing: -0.01em; }
.btn-export:hover:not(:disabled) { background: var(--color-primary-hover); }
.btn-export:disabled { opacity: 0.3; cursor: not-allowed; }
.analysis-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2.5rem; }
.panel-container { display: flex; flex-direction: column; gap: 1rem; }
.placeholder { background: var(--color-bg-secondary); border: 1px solid var(--color-border); border-radius: 4px; height: 450px; display: flex; align-items: center; justify-content: center; color: var(--color-text-tertiary); font-size: 0.9375rem; }
.controls-section { max-width: 700px; margin: 0 auto; }
.loading-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.95); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 1000; }
.spinner { width: 40px; height: 40px; border: 2px solid var(--color-border-secondary); border-top-color: var(--color-text); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-overlay p { color: #ffffff; margin-top: 1.5rem; font-size: 0.9375rem; font-weight: 500; }
@media (max-width: 1024px) { .analysis-grid { grid-template-columns: 1fr; } }
</style>
