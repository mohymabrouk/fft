<template>
  <div class="upload-container">
    <div class="drop-zone" :class="{ 'drag-over': isDragging }" @drop.prevent="handleDrop" @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false" @click="triggerFileInput">
      <div class="upload-content">
        <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
        <h3>Upload Signal File</h3>
        <p>Drop your .wav or .csv file here, or click to browse</p>
        <input ref="fileInput" type="file" accept=".wav,.csv" @change="handleFileSelect" style="display: none" />
        <div class="supported-formats">Supported formats: WAV, CSV</div>
      </div>
    </div>

    <div v-if="store.hasSignal" class="signal-info">
      <div class="info-header">Signal Loaded</div>
      <div class="info-grid">
        <div class="info-item"><span class="info-label">Samples</span><span class="info-value">{{ store.currentSignal?.num_samples.toLocaleString() }}</span></div>
        <div class="info-item"><span class="info-label">Duration</span><span class="info-value">{{ store.currentSignal?.duration.toFixed(2) }}s</span></div>
        <div class="info-item"><span class="info-label">Sample Rate</span><span class="info-value">{{ store.currentSignal?.sampling_rate }} Hz</span></div>
      </div>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useFFTStore } from '../stores/fftStore'
import { api } from '../services/api'

const store = useFFTStore()
const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const error = ref<string | null>(null)
const emit = defineEmits<{ uploaded: [] }>()

const triggerFileInput = () => { fileInput.value?.click() }

const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) { await uploadFile(target.files[0]) }
}

const handleDrop = async (event: DragEvent) => {
  isDragging.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    await uploadFile(event.dataTransfer.files[0])
  }
}

const uploadFile = async (file: File) => {
  try {
    error.value = null
    store.setLoading(true)
    const signalData = await api.uploadFile(file)
    store.setSignal(signalData)
    emit('uploaded')
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Error uploading file'
    store.setError(error.value)
  } finally {
    store.setLoading(false)
  }
}
</script>

<style scoped>
.upload-container { max-width: 700px; margin: 0 auto; }
.drop-zone { border: 2px dashed var(--color-border-secondary); border-radius: 4px; padding: 3rem; text-align: center; background: var(--color-bg-secondary); transition: all 0.3s ease; cursor: pointer; }
.drop-zone:hover { border-color: var(--color-text-tertiary); background: var(--color-bg-tertiary); }
.drop-zone.drag-over { border-color: var(--color-text); background: var(--color-border); }
.upload-content { pointer-events: none; }
.upload-icon { width: 48px; height: 48px; color: var(--color-text-tertiary); margin: 0 auto 1.5rem; }
.drop-zone h3 { color: var(--color-text); margin-bottom: 0.5rem; font-size: 1.25rem; font-weight: 600; letter-spacing: -0.02em; }
.drop-zone p { color: var(--color-text-secondary); margin-bottom: 1.5rem; font-size: 0.9375rem; }
.supported-formats { color: var(--color-text-tertiary); font-size: 0.8125rem; margin-top: 1rem; }
.signal-info { margin-top: 2rem; padding: 1.5rem; background: var(--color-bg-secondary); border: 1px solid var(--color-border); border-radius: 4px; }
.info-header { color: var(--color-text); margin-bottom: 1rem; font-size: 0.9375rem; font-weight: 600; letter-spacing: -0.01em; }
.info-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
.info-item { display: flex; flex-direction: column; gap: 0.25rem; }
.info-label { color: var(--color-text-tertiary); font-size: 0.8125rem; text-transform: uppercase; letter-spacing: 0.05em; }
.info-value { color: var(--color-text); font-size: 1rem; font-weight: 500; }
.error-message { margin-top: 1rem; padding: 1rem; background: var(--color-error-bg); border: 1px solid var(--color-error-border); color: var(--color-error-text); border-radius: 4px; font-size: 0.875rem; }
@media (max-width: 768px) { .info-grid { grid-template-columns: 1fr; gap: 1rem; } }
</style>
