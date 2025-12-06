import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { SignalData, FFTResult, FFTRequest } from '../services/api'

export const useFFTStore = defineStore('fft', () => {
  const currentSignal = ref<SignalData | null>(null)
  const currentFFT = ref<FFTResult | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const fftParams = ref<FFTRequest>({
    signal_data: [], sampling_rate: 44100, window_size: 2048, window_type: 'hann',
    filter_type: undefined, filter_cutoff: undefined
  })

  const hasSignal = computed(() => currentSignal.value !== null)
  const hasFFT = computed(() => currentFFT.value !== null)

  function setSignal(signal: SignalData) { currentSignal.value = signal; fftParams.value.sampling_rate = signal.sampling_rate; currentFFT.value = null }
  function setFFT(fft: FFTResult) { currentFFT.value = fft }
  function updateFFTParams(params: Partial<FFTRequest>) { fftParams.value = { ...fftParams.value, ...params } }
  function setLoading(v: boolean) { isLoading.value = v }
  function setError(e: string | null) { error.value = e }
  function reset() { currentSignal.value = null; currentFFT.value = null; error.value = null }

  return { currentSignal, currentFFT, isLoading, error, fftParams, hasSignal, hasFFT, setSignal, setFFT, updateFFTParams, setLoading, setError, reset }
})
