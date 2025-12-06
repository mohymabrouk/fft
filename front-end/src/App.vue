<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-content">
        <router-link to="/" class="logo">FFT Signal Analyzer</router-link>
        <div class="nav-right">
          <div class="nav-links">
            <router-link to="/">Home</router-link>
            <router-link to="/analysis">Analysis</router-link>
            <router-link to="/images">Images</router-link>
            <router-link to="/about">About</router-link>
          </div>
          <button
            @click="themeStore.toggleTheme()"
            class="theme-toggle"
            :aria-label="themeStore.isDark ? 'Switch to light mode' : 'Switch to dark mode'">
            <svg v-if="themeStore.isDark" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="5"></circle>
              <line x1="12" y1="1" x2="12" y2="3"></line>
              <line x1="12" y1="21" x2="12" y2="23"></line>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
              <line x1="1" y1="12" x2="3" y2="12"></line>
              <line x1="21" y1="12" x2="23" y2="12"></line>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
            <svg v-else class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
          </button>
        </div>
      </div>
    </nav>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useThemeStore } from './stores/themeStore'
const themeStore = useThemeStore()
</script>

<style>
:root[data-theme="light"] {
  --color-bg: #ffffff;
  --color-bg-secondary: #f5f5f5;
  --color-bg-tertiary: #fafafa;
  --color-text: #000000;
  --color-text-secondary: #666666;
  --color-text-tertiary: #999999;
  --color-border: #e6e6e6;
  --color-border-secondary: #cccccc;
  --color-primary: #000000;
  --color-primary-hover: #333333;
  --color-plot-line: #000000;
  --color-plot-fill: rgba(0, 0, 0, 0.1);
  --color-grid: #f0f0f0;
  --color-error-bg: #fff5f5;
  --color-error-border: #ffcccc;
  --color-error-text: #cc0000;
}

:root[data-theme="dark"] {
  --color-bg: #000000;
  --color-bg-secondary: #0a0a0a;
  --color-bg-tertiary: #0f0f0f;
  --color-text: #ffffff;
  --color-text-secondary: #999999;
  --color-text-tertiary: #666666;
  --color-border: #1a1a1a;
  --color-border-secondary: #333333;
  --color-primary: #ffffff;
  --color-primary-hover: #e6e6e6;
  --color-plot-line: #ffffff;
  --color-plot-fill: rgba(255, 255, 255, 0.1);
  --color-grid: #1a1a1a;
  --color-error-bg: #1a0000;
  --color-error-border: #4d0000;
  --color-error-text: #ff6666;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--color-bg); color: var(--color-text); min-height: 100vh; line-height: 1.6; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; transition: background-color 0.3s ease, color 0.3s ease; }
#app { min-height: 100vh; display: flex; flex-direction: column; }
.navbar { background: var(--color-bg); border-bottom: 1px solid var(--color-border-secondary); padding: 1.25rem 2rem; position: sticky; top: 0; z-index: 100; backdrop-filter: blur(10px); }
.nav-content { max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
.nav-right { display: flex; align-items: center; gap: 2rem; }
.logo { font-size: 1.125rem; font-weight: 600; color: var(--color-text); text-decoration: none; letter-spacing: -0.02em; transition: opacity 0.2s; }
.logo:hover { opacity: 0.7; }
.nav-links { display: flex; gap: 2.5rem; }
.nav-links a { color: var(--color-text-secondary); text-decoration: none; font-size: 0.9375rem; font-weight: 500; transition: color 0.2s; letter-spacing: -0.01em; }
.nav-links a:hover { color: var(--color-text); }
.nav-links a.router-link-active { color: var(--color-text); position: relative; }
.nav-links a.router-link-active::after { content: ''; position: absolute; bottom: -1.35rem; left: 0; right: 0; height: 1px; background: var(--color-text); }
.theme-toggle { background: transparent; border: 1px solid var(--color-border); width: 36px; height: 36px; border-radius: 4px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; padding: 0; }
.theme-toggle:hover { border-color: var(--color-border-secondary); background: var(--color-bg-secondary); }
.theme-toggle .icon { width: 18px; height: 18px; color: var(--color-text); }
main { flex: 1; padding: 3rem 0; }
@media (max-width: 768px) { .nav-links { gap: 1.5rem; } .nav-right { gap: 1rem; } main { padding: 2rem 0; } }
</style>
