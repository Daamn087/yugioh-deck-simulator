<template>
  <div class="max-w-4xl mx-auto px-6 py-12 min-h-screen animate-in fade-in slide-in-from-bottom-4 duration-700">
    <div class="text-center mb-16 relative">
      <div class="absolute -top-10 left-1/2 -translate-x-1/2 w-40 h-40 bg-primary/10 blur-[100px] rounded-full -z-10"></div>
      <h1 class="text-5xl font-black tracking-tighter text-white mb-3">
        CHANGELOG
      </h1>
      <p class="text-[10px] font-black uppercase tracking-[0.3em] text-primary/80">
        Latest updates • Bugfixes • Features
      </p>
    </div>
    
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-4">
      <div class="w-10 h-10 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
      <p class="text-[10px] font-black uppercase tracking-widest text-white/40">Loading changelog...</p>
    </div>
    
    <div v-else-if="error" class="bg-red-500/10 border border-red-500/20 rounded-2xl p-8 text-center">
      <p class="text-red-400 font-bold">{{ error }}</p>
    </div>
    
    <div v-else class="changelog-content prose prose-invert max-w-none" v-html="renderedChangelog"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { marked } from 'marked';
import changelogRaw from '../../../CHANGELOG.md?raw';

const loading = ref(true);
const error = ref('');
const renderedChangelog = ref('');

onMounted(async () => {
  try {
    marked.setOptions({
      breaks: true,
      gfm: true
    });
    
    renderedChangelog.value = await marked(changelogRaw);
    loading.value = false;
  } catch (err) {
    error.value = 'Unable to render changelog. Please try again later.';
    loading.value = false;
    console.error('Error rendering changelog:', err);
  }
});
</script>

<style scoped>
@reference "../style.css";

.changelog-content :deep(h1) {
  display: none; /* Hide the H1 from markdown as we have our own */
}

.changelog-content :deep(h2) {
  @apply text-2xl font-black tracking-tight text-white mt-16 mb-6 pb-4 border-b border-white/5;
}

.changelog-content :deep(h3) {
  @apply text-base font-black uppercase tracking-[0.1em] text-primary mt-12 mb-6 flex items-center gap-4;
}

.changelog-content :deep(h3)::before {
  content: "";
  @apply w-2 h-2 rounded-full bg-primary shadow-[0_0_10px_rgba(var(--color-primary),0.6)];
}

.changelog-content :deep(ul) {
  @apply space-y-3 my-6 list-none pl-0;
}

.changelog-content :deep(li) {
  @apply relative pl-6 text-white/70 text-sm leading-relaxed transition-colors hover:text-white;
}

.changelog-content :deep(li)::before {
  content: '→';
  @apply absolute left-0 text-primary/40 font-bold;
}

.changelog-content :deep(code) {
  @apply bg-white/5 px-1.5 py-0.5 rounded border border-white/10 font-mono text-xs text-primary/90;
}

.changelog-content :deep(a) {
  @apply text-primary hover:text-white underline decoration-primary/30 underline-offset-4 transition-all;
}

.changelog-content :deep(p) {
  @apply text-white/50 text-sm mb-4 leading-relaxed;
}

.changelog-content :deep(blockquote) {
  @apply border-l-2 border-primary/30 pl-4 my-6 italic text-white/40;
}
</style>
