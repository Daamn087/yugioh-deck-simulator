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
const activeTab = ref<'deck' | 'rules' | 'effects'>('deck');

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
  <div class="relative w-full">
    <!-- Animated Content Container -->
    <div class="animate-fade-in space-y-8 pb-32 lg:pb-0">
      <!-- Utility Bar (Desktop/Tablets) -->
      <div class="flex flex-col sm:flex-row items-center gap-4 bg-surface-card p-3 rounded-xl border border-border-primary shadow-inner w-full">
        <label class="flex items-center justify-between sm:justify-start gap-3 text-sm font-medium text-text-secondary w-full sm:w-auto px-2 sm:px-0">
            <span class="whitespace-nowrap">Simulations:</span>
            <input type="text" v-model.lazy="simulationsFormatted" class="w-full sm:w-32 bg-[#2a2a2a] border border-[#444] rounded px-3 py-1.5 text-white focus:outline-none focus:ring-2 focus:ring-primary transition-all">
        </label>
        <div class="flex items-center gap-2 w-full sm:w-auto ml-auto">
          <button @click="handleExport" class="flex-1 sm:flex-none bg-gray-700 hover:bg-gray-600 px-4 py-2 sm:py-1 rounded text-sm font-semibold transition-colors flex items-center justify-center gap-2" title="Download configuration">
            <span>⬇️</span> Export
          </button>
          <button @click="handleImportClick" class="flex-1 sm:flex-none bg-gray-700 hover:bg-gray-600 px-4 py-2 sm:py-1 rounded text-sm font-semibold transition-colors flex items-center justify-center gap-2" title="Upload configuration">
            <span>⬆️</span> Import
          </button>
          <button @click="store.resetToDefaults" class="bg-red-900/40 hover:bg-red-900/80 border border-red-800/50 p-2 sm:px-4 sm:py-1 rounded text-sm font-semibold transition-colors flex items-center justify-center gap-2" title="Clear all settings">
            <span class="sm:hidden">🔄</span>
            <span class="hidden sm:inline">🔄 Reset</span>
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

      <!-- Mobile Navigation Tabs -->
      <nav class="lg:hidden flex gap-3 p-1 bg-surface-card rounded-xl border border-border-primary">
        <button 
          @click="activeTab = 'deck'"
          class="flex-1 py-3 px-2 rounded-lg text-sm font-bold transition-all flex flex-col items-center gap-1"
          :class="activeTab === 'deck' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'text-text-secondary hover:text-white'"
        >
          <span class="text-xl">🎴</span>
          <span>Deck</span>
        </button>
        <button 
          @click="activeTab = 'rules'"
          class="flex-1 py-3 px-2 rounded-lg text-sm font-bold transition-all flex flex-col items-center gap-1"
          :class="activeTab === 'rules' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'text-text-secondary hover:text-white'"
        >
          <span class="text-xl">⚖️</span>
          <span>Rules</span>
        </button>
        <button 
          @click="activeTab = 'effects'"
          class="flex-1 py-3 px-2 rounded-lg text-sm font-bold transition-all flex flex-col items-center gap-1"
          :class="activeTab === 'effects' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'text-text-secondary hover:text-white'"
        >
          <span class="text-xl">⚡</span>
          <span>Effects</span>
        </button>
      </nav>

      <main class="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        <!-- Content Area -->
        <div class="lg:col-span-2 flex flex-col gap-6">
          <div :class="{'hidden lg:block': activeTab !== 'deck'}">
            <DeckBuilder 
                v-model:contents="deckContents"
                v-model:deckSize="deckSize"
                v-model:handSize="handSize"
                @delete-category="store.deleteCategory"
            />
          </div>
          
          <div :class="{'hidden lg:block': activeTab !== 'rules'}">
            <RuleBuilder
                v-model:rules="rules"
                :availableCategories="availableCategories" 
            />
          </div>
          
          <div :class="{'hidden lg:block': activeTab !== 'effects'}">
            <CardEffectsEditor />
          </div>
        </div>
        
        <!-- Desktop Sidebar -->
        <div class="hidden lg:flex lg:col-span-1 flex-col gap-6 sticky top-8">
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

    <!-- Mobile Sticky Footer - OUTSIDE animation container to avoid containing block issues -->
    <div class="lg:hidden fixed bottom-0 left-4 right-4 p-4 bg-bg-dark/95 backdrop-blur-md border-0 shadow-2xl">
      <div class="flex items-center gap-4">
        <div class="flex-1 bg-surface-card/50 p-3 rounded-xl border border-white/5 flex items-center justify-between">
          <div class="flex flex-col">
            <span class="text-[10px] uppercase tracking-wider text-text-secondary font-bold">Success Rate</span>
            <span class="text-xl font-black text-primary">{{ result ? result.success_rate.toFixed(2) + '%' : '0.00%' }}</span>
          </div>
          <div class="w-16 sm:w-20 bg-black/40 h-2 rounded-full overflow-hidden border border-white/5">
            <div 
              class="h-full bg-gradient-to-r from-primary to-blue-500 transition-all duration-500"
              :style="{ width: result ? result.success_rate + '%' : '0%' }"
            ></div>
          </div>
        </div>
        <button 
          @click="run"
          :disabled="loading"
          class="bg-gradient-to-r from-primary to-blue-600 text-white font-black px-6 py-4 rounded-xl shadow-lg shadow-primary/30 active:scale-95 disabled:opacity-50 disabled:grayscale transition-all min-w-[80px]"
        >
          {{ loading ? '...' : 'RUN' }}
        </button>
      </div>
    </div>
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
