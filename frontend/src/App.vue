
<script setup lang="ts">
import { ref, computed } from 'vue';
import { storeToRefs } from 'pinia';
import DeckBuilder from './components/DeckBuilder.vue';
import RuleBuilder from './components/RuleBuilder.vue';
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
            hand_size: handSize.value,
            simulations: simulations.value,
            rules: rules.value
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
</script>

<template>
  <div class="app-container">
    <header>
      <h1>Yu-Gi-Oh! Deck Sim</h1>
      <div class="global-opts">
        <label>
            Hand Size:
            <input type="number" class="input-slim" v-model="handSize">
        </label>
        <label>
            Simulations:
            <input type="text" v-model.lazy="simulationsFormatted">
        </label>
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
</style>
