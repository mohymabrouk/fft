import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(true)
  const saved = localStorage.getItem('theme')
  if (saved) isDark.value = saved === 'dark'

  const update = () => {
    document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
  }
  watch(isDark, () => { localStorage.setItem('theme', isDark.value ? 'dark' : 'light'); update() })
  update()
  const toggleTheme = () => { isDark.value = !isDark.value }
  return { isDark, toggleTheme }
})
