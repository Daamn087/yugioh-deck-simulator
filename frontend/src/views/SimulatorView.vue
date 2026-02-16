<script setup lang="ts">
import { ref, computed } from 'vue';
import { storeToRefs } from 'pinia';
import DeckBuilder from '../components/DeckBuilder.vue';
import RuleBuilder from '../components/RuleBuilder.vue';
import CardEffectsEditor from '../components/CardEffectsEditor.vue';
import Results from '../components/Results.vue';
import { runSimulation, type SimulationResult } from '../api';
import { useSimulationStore } from '../store';

// State
const store = useSimulationStore();
const { deckSize, handSize, simulations, deckContents, rules } = storeToRefs(store);

const result = ref<SimulationResult | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

const availableCategories = computed(() => Object.keys(deckContents.value));

const simulationsFormatted = computed({
  get: () => simulations.value.toLocaleString('de-DE'),
  set: (val: string) => {
    const num = parseInt(val.replace(/\./g, ''), 10);
    if (!isNaN(num)) simulations.value = Math.max(1, num);
  }
});

const fileInput = ref<HTMLInputElement | null>(null);

const handleExport = () => {
  store.exportConfig();
};

const handleImportClick = () => {
  fileInput.value?.click();
};

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    try {
      await store.importConfig(file);
      target.value = '';
    } catch (e: any) {
      error.value = e.message;
    }
  }
};

const run = async () => {
    loading.value = true;
    error.value = null;
    try {
        result.value = await runSimulation({
            deck_size: deckSize.value,
            deck_contents: deckContents.value,
            card_categories: store.cardCategories,
            hand_size: handSize.value,
            simulations: simulations.value,
            rules: rules.value,
            card_effects: store.cardEffects
        });
    } catch (e: any) {
        error.value = e.message;
    } finally {
        loading.value = false;
    }
};
</script>

<template>
  <div class="animate-fade-in space-y-8">
    <!-- Utility Bar -->
    <div class="flex flex-wrap items-center gap-6 bg-surface-card p-3 rounded-lg border border-border-primary shadow-inner">
      <label class="flex items-center gap-2 text-sm font-medium text-text-secondary whitespace-nowrap">
          Simulations:
          <input type="text" v-model.lazy="simulationsFormatted" class="w-32 bg-[#2a2a2a] border border-[#444] rounded px-3 py-1 text-white focus:outline-none focus:ring-2 focus:ring-primary transition-all">
      </label>
      <div class="flex items-center gap-2 ml-auto">
        <button @click="handleExport" class="bg-gray-700 hover:bg-gray-600 px-4 py-1 rounded text-sm font-semibold transition-colors flex items-center gap-2" title="Download configuration">
          <span>⬇️</span> Export
        </button>
        <button @click="handleImportClick" class="bg-gray-700 hover:bg-gray-600 px-4 py-1 rounded text-sm font-semibold transition-colors flex items-center gap-2" title="Upload configuration">
          <span>⬆️</span> Import
        </button>
        <button @click="store.resetToDefaults" class="bg-red-900/40 hover:bg-red-900/60 border border-red-800/50 px-4 py-1 rounded text-sm font-semibold transition-colors flex items-center gap-2" title="Clear all settings">
          <span>🔄</span> Reset
        </button>
        <input 
          type="file" 
          ref="fileInput" 
          @change="handleFileUpload" 
          accept=".json"
          class="hidden"
        />
      </div>
    </div>

    <main class="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
      <div class="lg:col-span-2 flex flex-col gap-6">
        <DeckBuilder 
            v-model:contents="deckContents"
            v-model:deckSize="deckSize"
            v-model:handSize="handSize"
            @delete-category="store.deleteCategory"
        />
        <RuleBuilder
            v-model:rules="rules"
            :availableCategories="availableCategories" 
        />
        <CardEffectsEditor />
      </div>
      
      <div class="lg:col-span-1 flex flex-col gap-6 sticky top-8">
          <Results :result="result" :loading="loading" />
          
          <button 
            class="w-full py-5 text-xl font-black rounded-xl shadow-[0_0_30px_rgba(0,184,255,0.3)] transition-all transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed uppercase tracking-widest bg-gradient-to-r from-primary to-blue-600 text-white"
            @click="run" 
            :disabled="loading"
          >
            {{ loading ? 'Processing...' : 'Run Simulation' }}
          </button>
          
          <div v-if="error" class="bg-red-500/10 border border-red-500/30 text-red-500 p-4 rounded-lg text-sm font-medium animate-pulse">
            Error: {{ error }}
          </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out forwards;
}
</style>
