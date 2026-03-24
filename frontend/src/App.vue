<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useSimulationStore } from './store';
import { getLatestChangelogVersion } from './utils/changelogUtils';
import changelogRaw from '../../CHANGELOG.md?raw';

const route = useRoute();
const store = useSimulationStore();
const error = ref<string | null>(null);

const latestVersion = getLatestChangelogVersion(changelogRaw);

const hasNewUpdate = computed(() => {
  if (!latestVersion) return false;
  return store.lastSeenChangelogVersion !== latestVersion;
});

// Watch for route changes to clear the notification
watch(() => route.path, (newPath) => {
  if (newPath === '/changelog' && latestVersion) {
    store.lastSeenChangelogVersion = latestVersion;
  }
}, { immediate: true });
</script>

<template>
  <div class="min-h-screen bg-bg-dark text-white/90 p-4 sm:p-8 flex flex-col items-center pb-32 lg:pb-8">
    <div class="w-full max-w-7xl">
      <header class="flex flex-col md:flex-row justify-between items-center mb-8 gap-4 border-b border-border-primary pb-6">
        <router-link to="/" class="group bg-transparent border-none">
          <h1 class="text-2xl sm:text-3xl font-extrabold bg-gradient-to-r from-primary to-blue-400 bg-clip-text text-transparent group-hover:opacity-80 transition-opacity text-center md:text-left">
            Yu-Gi-Oh! Deck Simulator
          </h1>
        </router-link>
        
        <div class="flex items-center gap-4">
          <router-link 
            to="/changelog" 
            class="px-5 py-2.5 rounded-xl text-xs font-black uppercase tracking-widest transition-all border shadow-sm active:scale-95 relative"
            :class="route.path === '/changelog' ? 'bg-primary border-primary text-black shadow-primary/20' : 'bg-white/5 border-white/10 text-white/60 hover:text-white hover:bg-white/10'"
          >
            Changelog
            <span v-if="hasNewUpdate" class="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-bg-dark shadow-[0_0_10px_rgba(239,68,68,0.5)] animate-pulse"></span>
          </router-link>
          <router-link 
            to="/docs-faq" 
            class="px-5 py-2.5 rounded-xl text-xs font-black uppercase tracking-widest transition-all border shadow-sm active:scale-95"
            :class="route.path === '/docs-faq' ? 'bg-primary border-primary text-black shadow-primary/20' : 'bg-white/5 border-white/10 text-white/60 hover:text-white hover:bg-white/10'"
          >
            Docs & FAQ
          </router-link>
        </div>
      </header>

      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>

      <div v-if="error" class="mt-8 bg-red-500/10 border border-red-500/30 text-red-500 p-4 rounded-lg text-sm font-medium animate-pulse">
        Error: {{ error }}
      </div>
    </div>
  </div>
</template>


<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
