<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const error = ref<string | null>(null);
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
            class="px-4 py-2 rounded-lg text-sm font-bold transition-all border"
            :class="route.path === '/changelog' ? 'bg-primary border-primary text-white' : 'bg-gray-700 border-border-primary text-text-secondary text-white hover:text-white hover:bg-gray-600'"
          >
            Changelog
          </router-link>
          <router-link 
            to="/docs-faq" 
            class="px-4 py-2 rounded-lg text-sm font-bold transition-all border"
            :class="route.path === '/docs-faq' ? 'bg-primary border-primary text-white' : 'bg-gray-700 border-border-primary text-text-secondary text-white hover:text-white hover:bg-gray-600'"
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
