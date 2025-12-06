<template>
  <div class="image-lab">
    <div class="header">
      <h1>Images</h1>
      <p>Upload, compress (JPEG), extract features, and register images.</p>
    </div>

    <div class="upload-row">
      <div class="image-upload">
        <h3>Upload Image A</h3>
        <input type="file" accept="image/*" @change="onFileA" />
        <div v-if="imgA" class="image-card">
          <img :src="origUrl(imgA.image_id)" alt="A" />
          <div class="meta">
            <span>{{ imgA.filename }}</span>
            <span>{{ imgA.width }}×{{ imgA.height }}</span>
          </div>
        </div>
      </div>

      <div class="image-upload">
        <h3>Upload Image B (optional)</h3>
        <input type="file" accept="image/*" @change="onFileB" />
        <div v-if="imgB" class="image-card">
          <img :src="origUrl(imgB.image_id)" alt="B" />
          <div class="meta">
            <span>{{ imgB.filename }}</span>
            <span>{{ imgB.width }}×{{ imgB.height }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="imgA" class="compress-panel">
      <h3>JPEG Compression</h3>
      <div class="controls">
        <label>Quality: <b>{{ quality }}</b></label>
        <input
          type="range"
          min="5"
          max="95"
          step="1"
          v-model.number="quality"
          @input="compressA"
        />
      </div>

      <div class="compress-grid">
        <div class="image-card">
          <h4>Original</h4>
          <img :src="origUrl(imgA.image_id)" alt="orig" />
        </div>
        <div class="image-card" v-if="compA">
          <h4>Compressed</h4>
          <img :src="apiBase + compA.url" alt="comp" />
          <div class="meta">
            <span>Size: {{ prettyBytes(compA.size_bytes) }}</span>
          </div>
        </div>
      </div>

      <div class="actions">
        <button class="btn" @click="extractFeaturesA">
          Extract Features (A)
        </button>
        <a
          v-if="overlayA"
          class="btn-link"
          :href="apiBase + overlayA"
          target="_blank"
        >
          View Features Overlay
        </a>
      </div>
    </div>

    <div v-if="imgA && imgB" class="register-panel">
      <h3>Registration</h3>
      <button class="btn" @click="registerAB">Align B to A</button>
      <div v-if="reg" class="image-card">
        <h4>Aligned</h4>
        <img :src="apiBase + reg.url" alt="aligned" />
      </div>
    </div>

    <div v-if="imgA && imgB" class="video-panel">
      <h3>Make MJPEG Video (A,B)</h3>
      <div class="controls">
        <label>FPS: <b>{{ fps }}</b></label>
        <input type="range" min="1" max="30" v-model.number="fps" />
      </div>
      <button class="btn" @click="makeVideo">Build Video</button>
      <div v-if="videoUrl" class="video-card">
        <video
          :src="apiBase + videoUrl"
          controls
          playsinline
          style="width: 100%; height: auto;"
        ></video>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api } from '../services/api'

const API_BASE_URL = 'http://localhost:8000'
const apiBase = API_BASE_URL

type ImgMeta = { image_id: string; filename: string; width: number; height: number }

const imgA = ref<ImgMeta | null>(null)
const imgB = ref<ImgMeta | null>(null)
const compA = ref<any>(null)
const overlayA = ref<string | null>(null)
const reg = ref<any>(null)
const fps = ref<number>(10)
const videoUrl = ref<string | null>(null)
const quality = ref<number>(75)

const origUrl = (id: string) => `${apiBase}/api/image/view/${id}`

const onFileA = async (e: Event) => {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (!f) return
  imgA.value = await api.uploadImage(f)
  await compressA()
}

const onFileB = async (e: Event) => {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (!f) return
  imgB.value = await api.uploadImage(f)
}

const compressA = async () => {
  if (!imgA.value) return
  compA.value = await api.compressImage(imgA.value.image_id, quality.value, 2)
}

const extractFeaturesA = async () => {
  if (!imgA.value) return
  const out = await api.features(imgA.value.image_id)
  overlayA.value = out.overlay_url
}

const registerAB = async () => {
  if (!imgA.value || !imgB.value) return
  reg.value = await api.register(imgA.value.image_id, imgB.value.image_id)
}

const makeVideo = async () => {
  if (!imgA.value || !imgB.value) return
  const out = await api.makeMjpeg([imgA.value.image_id, imgB.value.image_id], fps.value)
  videoUrl.value = out.url
}

const prettyBytes = (n: number) => {
  if (n < 1024) return n + ' B'
  if (n < 1024 * 1024) return (n / 1024).toFixed(1) + ' KB'
  return (n / 1024 / 1024).toFixed(2) + ' MB'
}
</script>

<style scoped>
.image-lab {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}
.header {
  margin-bottom: 2rem;
}
.header h1 {
  color: var(--color-text);
  font-size: 2rem;
  font-weight: 600;
  letter-spacing: -0.02em;
}
.upload-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}
.image-upload {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 1.25rem;
}
.image-card {
  margin-top: 1rem;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 0.75rem;
}
.image-card img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 4px;
}
.meta {
  display: flex;
  justify-content: space-between;
  color: var(--color-text-tertiary);
  font-size: 0.8125rem;
  margin-top: 0.25rem;
}
.compress-panel {
  margin-top: 1.5rem;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 1.25rem;
}
.controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
  color: var(--color-text-secondary);
}
.compress-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.actions {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
}
.btn {
  padding: 0.625rem 1rem;
  background: var(--color-primary);
  color: var(--color-bg);
  border: none;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
}
.btn-link {
  padding: 0.625rem 1rem;
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-radius: 4px;
  text-decoration: none;
}
.register-panel {
  margin-top: 2rem;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 1.25rem;
}
@media (max-width: 1024px) {
  .upload-row,
  .compress-grid {
    grid-template-columns: 1fr;
  }
}
.video-panel {
  margin-top: 2rem;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 1.25rem;
}
.video-card {
  margin-top: 1rem;
}
</style>
