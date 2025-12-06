<template>
  <div class="about-page">
    <div class="header">
      <h1>About FFT</h1>
      <p>Fast Fourier Transform (FFT) converts a signal from time to frequency domain, revealing the frequencies composing it.</p>
    </div>

    <div class="content-grid">
      <div class="card">
        <h3>Principle</h3>
        <p>The Discrete Fourier Transform (DFT) of N samples decomposes the signal into N complex sinusoids. FFT is an O(N log N) algorithm that computes the same result much faster than the naive O(N²) approach.</p>
        <ul class="bullets">
          <li><b>Windowing</b> reduces spectral leakage; common windows: Hann, Hamming, Blackman.</li>
          <li><b>Resolution</b> depends on sampling rate and window size: Δf = fs / N.</li>
          <li><b>rFFT</b> exploits real-valued input to return non-negative frequencies only.</li>
        </ul>
      </div>
      <div class="card">
        <h3>Demo (synthetic)</h3>
        <div id="demoPlot" class="plot"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Plotly from 'plotly.js-dist-min'
import { onMounted } from 'vue'
import { useThemeStore } from '../stores/themeStore'

const theme = useThemeStore()

onMounted(() => {
  const fs = 22050
  const N = 1024
  const t = Array.from({ length: N }, (_, i) => i / fs)
  const x = t.map((ti) => Math.sin(2*Math.PI*440*ti) + 0.5*Math.sin(2*Math.PI*1000*ti))

  const re = new Array(N).fill(0)
  const im = new Array(N).fill(0)
  for (let k = 0; k < N; k++) {
    let sumRe = 0, sumIm = 0
    for (let n = 0; n < N; n++) {
      const phi = -2*Math.PI*k*n/N
      sumRe += x[n] * Math.cos(phi)
      sumIm += x[n] * Math.sin(phi)
    }
    re[k] = sumRe; im[k] = sumIm
  }
  const mags = re.map((r, k) => Math.sqrt(r*r + im[k]*im[k]))
  const freqs = re.slice(0, Math.floor(N/2)+1).map((_, k) => k * fs / N)
  const half = mags.slice(0, Math.floor(N/2)+1)

  const isDark = theme.isDark
  Plotly.newPlot('demoPlot', [{
    x: freqs, y: half, type: 'scatter', mode: 'lines',
    line: { color: isDark ? '#ffffff' : '#000000', width: 1.5 },
    fill: 'tozeroy', fillcolor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'
  }], {
    paper_bgcolor: isDark ? '#000000' : '#ffffff',
    plot_bgcolor: isDark ? '#000000' : '#ffffff',
    font: { color: isDark ? '#ffffff' : '#000000' },
    xaxis: { title: 'Frequency (Hz)' },
    yaxis: { title: 'Magnitude' },
    margin: { t: 10, r: 20, b: 40, l: 50 }
  }, { displayModeBar: false, responsive: true })
})
</script>

<style scoped>
.about-page { max-width: 1200px; margin: 0 auto; padding: 0 2rem; }
.header { margin-bottom: 2rem; }
.header h1 { color: var(--color-text); font-size: 2rem; font-weight: 600; letter-spacing: -0.02em; margin-bottom: 0.5rem; }
.header p { color: var(--color-text-secondary); }
.content-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.card { background: var(--color-bg-secondary); border: 1px solid var(--color-border); border-radius: 4px; padding: 1.25rem; }
.bullets { margin-top: 0.5rem; color: var(--color-text-secondary); }
.plot { height: 360px; }
@media (max-width: 1024px) { .content-grid { grid-template-columns: 1fr; } }
</style>
