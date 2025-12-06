import { createRouter, createWebHistory } from 'vue-router'
import Home from './pages/Home.vue'
import Analysis from './pages/Analysis.vue'
import About from './pages/About.vue'
import ImageLab from './pages/ImageLab.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/analysis', component: Analysis },
  { path: '/images', component: ImageLab },
  { path: '/about', component: About }
]

const router = createRouter({ history: createWebHistory(), routes })
export default router
