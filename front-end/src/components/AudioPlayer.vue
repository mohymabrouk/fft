<template>
  <div class="audio-player">
    <div class="player-header">
      <span class="player-title">{{ title }}</span>
      <span class="player-duration">{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</span>
    </div>
    <div class="player-controls">
      <button @click="togglePlay" class="btn-play" :disabled="!audioUrl">
        <svg v-if="!isPlaying" class="icon" viewBox="0 0 24 24" fill="currentColor">
          <polygon points="5 3 19 12 5 21 5 3"></polygon>
        </svg>
        <svg v-else class="icon" viewBox="0 0 24 24" fill="currentColor">
          <rect x="6" y="4" width="4" height="16"></rect>
          <rect x="14" y="4" width="4" height="16"></rect>
        </svg>
      </button>
      <div class="progress-container">
        <input type="range" class="progress-bar" :value="progress" @input="seek" min="0" max="100" :disabled="!audioUrl" />
      </div>
      <button @click="download" class="btn-download" :disabled="!audioUrl" :title="'Download ' + title">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
      </button>
    </div>
    <audio ref="audioElement" :src="audioUrl" @timeupdate="updateProgress" @loadedmetadata="onLoadedMetadata" @ended="onEnded"></audio>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{ audioUrl: string | null; title: string; downloadUrl: string | null }>()

const audioElement = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const progress = ref(0)

const togglePlay = () => {
  if (!audioElement.value) return
  if (isPlaying.value) audioElement.value.pause()
  else audioElement.value.play()
  isPlaying.value = !isPlaying.value
}

const updateProgress = () => {
  if (!audioElement.value) return
  currentTime.value = audioElement.value.currentTime
  progress.value = (currentTime.value / duration.value) * 100 || 0
}

const onLoadedMetadata = () => {
  if (!audioElement.value) return
  duration.value = audioElement.value.duration
}

const onEnded = () => { isPlaying.value = false; currentTime.value = 0; progress.value = 0 }

const seek = (event: Event) => {
  if (!audioElement.value) return
  const target = event.target as HTMLInputElement
  const seekTime = (parseFloat(target.value) / 100) * duration.value
  audioElement.value.currentTime = seekTime
}

const formatTime = (seconds: number): string => {
  if (!seconds || isNaN(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const download = () => {
  if (!props.downloadUrl) return
  const link = document.createElement('a')
  link.href = props.downloadUrl
  link.download = `${props.title.toLowerCase().replace(/\s+/g, '_')}.wav`
  document.body.appendChild(link); link.click(); document.body.removeChild(link)
}

watch(() => props.audioUrl, () => { isPlaying.value = false; currentTime.value = 0; progress.value = 0 })
</script>

<style scoped>
.audio-player { background: var(--color-bg-secondary); border: 1px solid var(--color-border); border-radius: 4px; padding: 1rem; }
.player-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
.player-title { font-size: 0.875rem; font-weight: 500; color: var(--color-text); letter-spacing: -0.01em; }
.player-duration { font-size: 0.8125rem; color: var(--color-text-tertiary); font-variant-numeric: tabular-nums; }
.player-controls { display: flex; align-items: center; gap: 0.75rem; }
.btn-play { width: 40px; height: 40px; border-radius: 4px; background: var(--color-primary); color: var(--color-bg); border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; flex-shrink: 0; }
.btn-play:hover:not(:disabled) { background: var(--color-primary-hover); }
.btn-play:disabled { opacity: 0.3; cursor: not-allowed; }
.btn-play .icon { width: 16px; height: 16px; }
.progress-container { flex: 1; }
.progress-bar { width: 100%; height: 2px; background: var(--color-border); border-radius: 1px; outline: none; appearance: none; -webkit-appearance: none; cursor: pointer; }
.progress-bar::-webkit-slider-thumb { appearance: none; -webkit-appearance: none; width: 12px; height: 12px; background: var(--color-text); border-radius: 50%; cursor: pointer; }
.progress-bar::-moz-range-thumb { width: 12px; height: 12px; background: var(--color-text); border: none; border-radius: 50%; cursor: pointer; }
.progress-bar:disabled { opacity: 0.3; cursor: not-allowed; }
.btn-download { width: 36px; height: 36px; border-radius: 4px; background: transparent; border: 1px solid var(--color-border); color: var(--color-text); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; flex-shrink: 0; }
.btn-download:hover:not(:disabled) { border-color: var(--color-border-secondary); background: var(--color-bg-tertiary); }
.btn-download:disabled { opacity: 0.3; cursor: not-allowed; }
.btn-download .icon { width: 16px; height: 16px; }
</style>
