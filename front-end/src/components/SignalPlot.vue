<template>
  <div class="plot-container">
    <div class="plot-header">
      <h3>Time Domain</h3>
      <span class="plot-subtitle">Signal amplitude over time</span>
    </div>
    <div ref="plotElement" class="plot"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import Plotly from 'plotly.js-dist-min'
import { useThemeStore } from '../stores/themeStore'

const props = defineProps<{ signalData: number[]; samplingRate: number }>()

const plotElement = ref<HTMLElement | null>(null)
const themeStore = useThemeStore()

const renderPlot = () => {
  if (!plotElement.value || props.signalData.length === 0) return
  const timeAxis = props.signalData.map((_, i) => i / props.samplingRate)
  const isDark = themeStore.isDark
  const trace: Partial<Plotly.PlotData> = {
    x: timeAxis, y: props.signalData, type: 'scatter', mode: 'lines',
    line: { color: isDark ? '#ffffff' : '#000000', width: 1 }, name: 'Signal'
  }
  const layout: Partial<Plotly.Layout> = {
    paper_bgcolor: isDark ? '#000000' : '#ffffff', plot_bgcolor: isDark ? '#000000' : '#ffffff',
    font: { color: isDark ? '#ffffff' : '#000000', family: 'Inter, sans-serif', size: 12 },
    xaxis: { title: { text: 'Time (s)' }, gridcolor: isDark ? '#1a1a1a' : '#f0f0f0', color: isDark ? '#ffffff' : '#000000', zeroline: false },
    yaxis: { title: { text: 'Amplitude' }, gridcolor: isDark ? '#1a1a1a' : '#f0f0f0', color: isDark ? '#ffffff' : '#000000', zeroline: false },
    margin: { t: 20, r: 30, b: 50, l: 60 }, hovermode: 'closest'
  }
  const config = { responsive: true, displayModeBar: false as const }
  Plotly.newPlot(plotElement.value, [trace], layout, config)
}

watch(() => [props.signalData, props.samplingRate, themeStore.isDark], renderPlot, { deep: true })
onMounted(renderPlot)
</script>

<style scoped>
.plot-container { background: var(--color-bg-secondary); border: 1px solid var(--color-border); border-radius: 4px; padding: 1.5rem; height: 100%; }
.plot-header { margin-bottom: 1.5rem; }
.plot-header h3 { color: var(--color-text); margin: 0 0 0.25rem 0; font-size: 1rem; font-weight: 600; letter-spacing: -0.01em; }
.plot-subtitle { color: var(--color-text-tertiary); font-size: 0.8125rem; }
.plot { height: 380px; }
</style>
