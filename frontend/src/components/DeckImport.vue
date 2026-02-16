<script setup lang="ts">
import { ref } from 'vue';
import { useSimulationStore } from '../store';

const store = useSimulationStore();
const selectedFile = ref<File | null>(null);
const importing = ref(false);
const importError = ref<string | null>(null);

const importDeck = async () => {
  if (!selectedFile.value) return;
  
  importing.value = true;
  importError.value = null;
  
  try {
    const file = selectedFile.value;
    await store.importFromXML(file);
    selectedFile.value = null;
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) fileInput.value = '';
  } catch (e: any) {
    importError.value = e.message || 'Failed to import deck';
  } finally {
    importing.value = false;
  }
};

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = target.files;
  if (files && files.length > 0) {
    const file = files[0];
    if (file) {
      selectedFile.value = file;
      importError.value = null;
    }
  }
};
</script>

<template>
  <div class="mb-8 pb-8 border-b-2 border-border-primary">
    <h3 class="text-sm font-semibold uppercase tracking-wider text-text-secondary mb-4 flex items-center gap-2">
      <span>📂</span> Import Deck from XML
    </h3>
    <div class="flex flex-col gap-3">
      <div class="flex flex-col sm:flex-row gap-3">
        <input 
          type="file"
          accept=".xml"
          @change="handleFileSelect"
          class="w-full sm:flex-1 bg-[#2a2a2a] border border-border-primary rounded-lg px-4 py-2 text-sm text-text-secondary cursor-pointer file:mr-4 file:py-1 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-gradient-to-r file:from-primary file:to-blue-600 file:text-white hover:file:brightness-110 disabled:opacity-50 transition-all"
          :disabled="importing"
        />
        <button 
          @click="importDeck" 
          :disabled="importing || !selectedFile"
          class="w-full sm:min-w-[100px] flex flex-0 items-center justify-center bg-gradient-to-r from-primary to-pink-500 hover:brightness-110 text-white font-bold py-3 sm:py-2 px-6 rounded-lg shadow-lg shadow-primary/20 transition-all active:scale-95 disabled:opacity-50 disabled:grayscale disabled:cursor-not-allowed"
        >
          <div v-if="importing" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          <span v-else>Import</span>
        </button>
      </div>
    </div>
    <p v-if="importError" class="mt-3 text-red-500 text-xs font-bold bg-red-500/10 p-2 rounded border border-red-500/20">{{ importError }}</p>
  </div>
</template>
