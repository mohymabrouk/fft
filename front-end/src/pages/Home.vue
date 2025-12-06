<template>
  <div class="home-page">
    <div class="hero">
      <h1>FFT Signal Analyzer</h1>
      <p>Professional frequency-domain analysis for audio and signal processing</p>
    </div>
    <UploadArea @uploaded="handleUpload" />
    <div v-if="store.currentSignal" class="preview-section">
      <SignalPlot :signal-data="store.currentSignal.time_domain" :sampling-rate="store.currentSignal.sampling_rate" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useFFTStore } from '../stores/fftStore'
import UploadArea from '../components/UploadArea.vue'
import SignalPlot from '../components/SignalPlot.vue'

const router = useRouter()
const store = useFFTStore()

const handleUpload = () => { router.push('/analysis') }
</script>

<style scoped>
.home-page { max-width: 1200px; margin: 0 auto; padding: 0 2rem; }
.hero { text-align: center; margin-bottom: 4rem; padding: 3rem 0; }
.hero h1 { font-size: 3rem; font-weight: 700; color: var(--color-text); margin-bottom: 1rem; letter-spacing: -0.03em; }
.hero p { color: var(--color-text-secondary); font-size: 1.125rem; font-weight: 400; letter-spacing: -0.01em; }
.preview-section { margin-top: 3rem; }
@media (max-width: 768px) { .hero h1 { font-size: 2rem; } .hero p { font-size: 1rem; } }
</style>
