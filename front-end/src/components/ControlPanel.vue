<template>
  <div class="control-panel">
    <h3>FFT Parameters</h3>
    <div class="control-group">
      <label>
        <span class="label-text">Window Size</span>
        <span class="label-value">{{ fftParams.window_size }}</span>
      </label>
      <input type="range" v-model.number="fftParams.window_size" min="256" max="8192" step="256" @input="emitUpdate" />
      <div class="range-labels"><span>256</span><span>8192</span></div>
    </div>
    <div class="control-group">
      <label><span class="label-text">Window Type</span></label>
      <select v-model="fftParams.window_type" @change="emitUpdate">
        <option value="hann">Hann</option>
        <option value="hamming">Hamming</option>
        <option value="blackman">Blackman</option>
        <option value="rectangular">Rectangular</option>
      </select>
    </div>
    <div class="control-group">
      <label><span class="label-text">Filter Type</span></label>
      <select v-model="fftParams.filter_type" @change="handleFilterChange">
        <option :value="undefined">None</option>
        <option value="lowpass">Low Pass</option>
        <option value="highpass">High Pass</option>
        <option value="bandpass">Band Pass</option>
      </select>
    </div>
    <div v-if="fftParams.filter_type" class="control-group">
      <label v-if="fftParams.filter_type === 'bandpass'">
        <span class="label-text">Band Range</span>
        <span class="label-value">{{ filterCutoff[0] }} - {{ filterCutoff[1] }} Hz</span>
      </label>
      <label v-else>
        <span class="label-text">Cutoff Frequency</span>
        <span class="label-value">{{ filterCutoff[0] }} Hz</span>
      </label>
      <input type="range" v-model.number="filterCutoff[0]" min="20" :max="fftParams.sampling_rate / 2" step="10" @input="emitUpdate" />
      <input v-if="fftParams.filter_type === 'bandpass'" type="range" v-model.number="filterCutoff[1]" :min="filterCutoff[0]" :max="fftParams.sampling_rate / 2" step="10" @input="emitUpdate" style="margin-top: 0.75rem" />
    </div>
    <button @click="runFFT" class="btn-analyze" :disabled="!canAnalyze">Run FFT Analysis</button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useFFTStore } from '../stores/fftStore'

const store = useFFTStore()
const fftParams = ref({ ...store.fftParams })
const filterCutoff = ref([1000, 5000])
const emit = defineEmits<{ 'run-fft': [] }>()

const canAnalyze = computed(() => store.hasSignal)

const handleFilterChange = () => {
  if (fftParams.value.filter_type) {
    fftParams.value.filter_cutoff = filterCutoff.value
  } else {
    fftParams.value.filter_cutoff = undefined
  }
  emitUpdate()
}

const emitUpdate = () => {
  if (fftParams.value.filter_type) {
    fftParams.value.filter_cutoff = [...filterCutoff.value]
  }
  store.updateFFTParams(fftParams.value)
}

const runFFT = () => { emit('run-fft') }
</script>

<style scoped>
.control-panel { background: var(--color-bg-secondary); border: 1px solid var(--color-border); border-radius: 4px; padding: 2rem; }
.control-panel h3 { color: var(--color-text); margin-bottom: 2rem; font-size: 1rem; font-weight: 600; letter-spacing: -0.01em; }
.control-group { margin-bottom: 2rem; }
.control-group label { display: flex; justify-content: space-between; align-items: center; color: var(--color-text-secondary); margin-bottom: 0.75rem; font-size: 0.875rem; }
.label-text { font-weight: 500; }
.label-value { color: var(--color-text); font-weight: 600; }
input[type="range"] { width: 100%; height: 2px; background: var(--color-border); border-radius: 1px; outline: none; appearance: none; -webkit-appearance: none; }
input[type="range"]::-webkit-slider-thumb { appearance: none; -webkit-appearance: none; width: 16px; height: 16px; background: var(--color-text); border-radius: 50%; cursor: pointer; transition: transform 0.2s; }
input[type="range"]::-webkit-slider-thumb:hover { transform: scale(1.2); }
input[type="range"]::-moz-range-thumb { width: 16px; height: 16px; background: var(--color-text); border: none; border-radius: 50%; cursor: pointer; transition: transform 0.2s; }
input[type="range"]::-moz-range-thumb:hover { transform: scale(1.2); }
.range-labels { display: flex; justify-content: space-between; color: var(--color-text-tertiary); font-size: 0.75rem; margin-top: 0.5rem; }
select { width: 100%; padding: 0.75rem; background: var(--color-bg); border: 1px solid var(--color-border); border-radius: 4px; color: var(--color-text); font-size: 0.875rem; cursor: pointer; transition: border-color 0.2s; font-family: inherit; }
select:hover { border-color: var(--color-border-secondary); }
select:focus { outline: none; border-color: var(--color-text-tertiary); }
.btn-analyze { width: 100%; padding: 1rem; background: var(--color-primary); color: var(--color-bg); border: none; border-radius: 4px; font-size: 0.9375rem; font-weight: 600; cursor: pointer; transition: all 0.2s; margin-top: 1rem; letter-spacing: -0.01em; }
.btn-analyze:hover:not(:disabled) { background: var(--color-primary-hover); }
.btn-analyze:disabled { opacity: 0.3; cursor: not-allowed; }
</style>
