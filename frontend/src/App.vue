
<script setup lang="ts">
import { ref, computed } from 'vue';
import { storeToRefs } from 'pinia';
import DeckBuilder from './components/DeckBuilder.vue';
import RuleBuilder from './components/RuleBuilder.vue';
import CardEffectsEditor from './components/CardEffectsEditor.vue';
import Results from './components/Results.vue';
import { runSimulation, type SimulationResult } from './api';
import { useSimulationStore } from './store';

// State
const store = useSimulationStore();
const { deckSize, handSize, simulations, deckContents, rules } = storeToRefs(store);

const result = ref<SimulationResult | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

const availableCategories = computed(() => Object.keys(deckContents.value));

const run = async () => {
    loading.value = true;
    error.value = null;
    try {
        result.value = await runSimulation({
            deck_size: deckSize.value,
            deck_contents: deckContents.value,
            card_categories: store.cardCategories,  // Send subcategory data
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
const simulationsFormatted = computed({
  get: () => simulations.value.toLocaleString('de-DE'),
  set: (val: string) => {
    const num = parseInt(val.replace(/\./g, ''), 10);
    if (!isNaN(num)) simulations.value = num;
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
      // Reset the input so the same file can be uploaded again
      target.value = '';
    } catch (e: any) {
      error.value = e.message;
    }
  }
};

</script>

<template>
  <div class="app-container">
    <header>
      <h1>Yu-Gi-Oh! Deck Simulator</h1>
      <div class="global-opts">
        <label>
            Hand Size:
            <input type="number" class="input-slim" v-model="handSize">
        </label>
        <label>
            Simulations:
            <input type="text" v-model.lazy="simulationsFormatted">
        </label>
        <div class="config-buttons">
          <button @click="handleExport" class="config-btn export-btn" title="Download configuration">
            📥 Export
          </button>
          <button @click="handleImportClick" class="config-btn import-btn" title="Upload configuration">
            📤 Import
          </button>
          <button @click="store.resetToDefaults" class="config-btn reset-btn" title="Clear all settings">
            🔄 Reset
          </button>
          <input 
            type="file" 
            ref="fileInput" 
            @change="handleFileUpload" 
            accept=".json"
            style="display: none"
          />
        </div>
      </div>
    </header>

    <main class="grid">
      <div class="col">
        <DeckBuilder 
            v-model:contents="deckContents"
            v-model:deckSize="deckSize"
            @delete-category="store.deleteCategory"
        />
        <RuleBuilder
            v-model:rules="rules"
            :availableCategories="availableCategories" 
        />
        <CardEffectsEditor />
      </div>
      
      <div class="col results-col">
          <Results :result="result" :loading="loading" />
          
          <button class="run-btn" @click="run" :disabled="loading">
            RUN SIMULATION
          </button>
          
          <div v-if="error" class="error-msg">
            Error: {{ error }}
          </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

h1 {
    font-size: 2rem;
    background: linear-gradient(90deg, #ff00cc, #3333ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.global-opts {
    display: flex;
    gap: 1rem;
}

.grid {
    display: grid;
    grid-template-columns: 1.5fr 1fr;
    gap: 2rem;
}

.col {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.results-col {
    position: sticky;
    top: 2rem;
}

.run-btn {
    font-size: 1.5rem;
    padding: 1rem;
    background: linear-gradient(90deg, #3333ff, #ff00cc);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    transition: transform 0.1s;
    width: 100%;
    margin-top: 1rem;
}

.run-btn:hover {
    filter: brightness(1.1);
    transform: scale(1.02);
}

.run-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.error-msg {
    color: red;
    margin-top: 1rem;
    text-align: center;
}

.input-slim {
  width: 50px;
}

.config-buttons {
  display: flex;
  gap: 0.5rem;
}

.config-btn {
  padding: 0.5rem 1rem;
  border: 2px solid #3333ff;
  border-radius: 6px;
  background: transparent;
  color: #3333ff;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.config-btn:hover {
  background: #3333ff;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(51, 51, 255, 0.3);
}

.export-btn:hover {
  background: linear-gradient(135deg, #3333ff, #5555ff);
}

.import-btn:hover {
  background: linear-gradient(135deg, #ff00cc, #ff33dd);
  border-color: #ff00cc;
}

.reset-btn {
  border-color: #ff4444;
  color: #ff4444;
}

.reset-btn:hover {
  background: linear-gradient(135deg, #ff4444, #ff6666);
  border-color: #ff4444;
}

</style>
