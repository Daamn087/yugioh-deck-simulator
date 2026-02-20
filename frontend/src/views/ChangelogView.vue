<template>
  <div class="changelog-container">
    <div class="changelog-header">
      <h1 class="text-primary">Changelog</h1>
      <p class="subtitle">List of latest updates, bugfixes and features</p>
    </div>
    
    <div v-if="loading" class="loading">
      <p>Loading changelog...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    
    <div v-else class="changelog-content" v-html="renderedChangelog"></div>
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
    // Configure marked options for better rendering
    marked.setOptions({
      breaks: true,
      gfm: true
    });
    
    // Convert markdown to HTML (using the raw content imported from root)
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
.changelog-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

.changelog-header {
  text-align: center;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 2px solid var(--border-color, #e0e0e0);
}

.changelog-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
}

.loading,
.error {
  text-align: center;
  padding: 3rem;
  font-size: 1.2rem;
}

.error {
  color: #e74c3c;
}

.changelog-content {
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.85);
  font-size: 1.05rem;
}

/* Style the rendered markdown content */
.changelog-content :deep(h1) {
  font-size: 2rem;
  margin-top: 2rem;
  margin-bottom: 1rem;
  color: #ffffff;
  font-weight: 700;
}

.changelog-content :deep(h2) {
  font-size: 1.6rem;
  margin-top: 2.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: #f8fafc;
  font-weight: 600;
}

.changelog-content :deep(h3) {
  font-size: 1.3rem;
  margin-top: 1.5rem;
  margin-bottom: 0.8rem;
  color: #818cf8;
  font-weight: 600;
}

.changelog-content :deep(ul) {
  margin-left: 1.5rem;
  margin-bottom: 1.5rem;
  list-style-type: disc;
}

.changelog-content :deep(li) {
  margin-bottom: 0.5rem;
  padding-left: 0.5rem;
  color: rgba(255, 255, 255, 0.85);
}

.changelog-content :deep(code) {
  background-color: rgba(255, 255, 255, 0.1);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 0.9em;
  color: #e2e8f0;
  word-break: break-word;
}

.changelog-content :deep(pre) {
  background-color: rgba(0, 0, 0, 0.3);
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  border: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 1.5rem;
}

.changelog-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
  color: #e2e8f0;
}

.changelog-content :deep(a) {
  color: #818cf8;
  text-decoration: none;
  transition: color 0.2s, text-decoration 0.2s;
}

.changelog-content :deep(a:hover) {
  color: #c7d2fe;
  text-decoration: underline;
}

.changelog-content :deep(p) {
  margin-bottom: 1rem;
  color: rgba(255, 255, 255, 0.85);
  word-break: break-word;
}

.changelog-content :deep(blockquote) {
  border-left: 4px solid #818cf8;
  padding-left: 1rem;
  margin-left: 0;
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
}

/* Version badge styling */
.changelog-content :deep(h2:has(+ h3)) {
  position: relative;
}

@media (max-width: 768px) {
  .changelog-container {
    padding: 1rem;
  }
  
  .changelog-header h1 {
    font-size: 2rem;
  }
  
  .changelog-content :deep(h2) {
    font-size: 1.4rem;
  }
}
</style>
