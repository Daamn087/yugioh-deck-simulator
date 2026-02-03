
<script setup lang="ts">
import { ref, computed } from 'vue';
import { useSimulationStore } from '../store';

const props = defineProps<{
  deckSize: number;
  contents: Record<string, number>;
}>();

const emit = defineEmits<{
  (e: 'update:deckSize', size: number): void;
  (e: 'update:contents', contents: Record<string, number>): void;
  (e: 'delete-category', name: string): void;
}>();

const store = useSimulationStore();

const newCategoryName = ref('');
const newCategoryCount = ref(3);
const importUrl = ref('');
const importing = ref(false);
const importError = ref<string | null>(null);

const currentCount = computed(() => {
  return Object.values(props.contents).reduce((a, b) => a + b, 0);
});

const addCategory = () => {
  if (!newCategoryName.value) return;
  const newContents = { ...props.contents, [newCategoryName.value]: newCategoryCount.value };
  emit('update:contents', newContents);
  newCategoryName.value = '';
};

const removeCategory = (name: string) => {
  emit('delete-category', name);
};

const updateCount = (name: string, count: number) => {
  const newContents = { ...props.contents, [name]: count };
  emit('update:contents', newContents);
};

const importProgress = ref(0);
const TIMEOUT_MS = 30000; // 30 seconds

const importDeck = async () => {
  if (!importUrl.value) return;
  
  importing.value = true;
  importError.value = null;
  importProgress.value = 0;
  
  // Start fake progress
  const interval = setInterval(() => {
    // Increment progress but slow down as it gets higher, capping at 95% until done
    if (importProgress.value < 40) {
      importProgress.value += 2;
    } else if (importProgress.value < 70) {
      importProgress.value += 1;
    } else if (importProgress.value < 95) {
      importProgress.value += 0.5;
    }
  }, TIMEOUT_MS / 100); // Rough approximation to fill in ~30s
  
  try {
    // Create a timeout promise
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error(`Import timed out after ${TIMEOUT_MS/1000} seconds. The deck list might be too large or DuelingBook is unresponsive.`)), TIMEOUT_MS)
    );

    // Race the actual import against the timeout
    await Promise.race([
      store.importFromDuelingBook(importUrl.value),
      timeoutPromise
    ]);
    
    importProgress.value = 100;
    importUrl.value = '';
  } catch (e: any) {
    importError.value = e.message || 'Failed to import deck';
  } finally {
    clearInterval(interval);
    
    // Keep the success state visible for a moment
    if (!importError.value) {
      setTimeout(() => {
        importing.value = false;
        setTimeout(() => { importProgress.value = 0; }, 300); // Clear bar after fade out
      }, 1000);
    } else {
      importing.value = false;
    }
  }
};
const clearAll = () => {
  if (Object.keys(props.contents).length === 0) return;
  if (confirm('Are you sure you want to clear all cards?')) {
    emit('update:contents', {});
  }
};
</script>

<template>
  <div class="deck-builder card">
    <h2>Deck Configuration</h2>
    
    <!-- Import Section -->
    <div class="import-section">
      <h3>Import from DuelingBook</h3>
      <div class="import-group">
        <div class="import-row">
          <input 
            v-model="importUrl" 
            placeholder="https://www.duelingbook.com/deck?id=..."
            class="import-input"
            @keyup.enter="importDeck"
            :disabled="importing"
          />
          <button 
            @click="importDeck" 
            :disabled="importing || !importUrl"
            class="import-btn"
          >
            <div v-if="importing" class="spinner"></div>
            <span v-else>Import</span>
          </button>
        </div>
        
        <!-- Progress Bar -->
        <div v-if="importing" class="progress-container">
          <div class="progress-bar" :style="{ width: `${Math.min(importProgress, 100)}%` }"></div>
        </div>
      </div>
      <p v-if="importError" class="error">{{ importError }}</p>
    </div>
    
    <div class="form-group">
      <label>Total Deck Size </label>
      <input 
        type="number" 
        :value="deckSize" 
        class="input-slim"
        @input="emit('update:deckSize', Number(($event.target as HTMLInputElement).value))"
      >
    </div>

    <div class="contents-list">
      <div class="header-row">
        <h3>Card Categories</h3>
        <button 
          v-if="Object.keys(contents).length > 0" 
          class="clear-btn" 
          @click="clearAll"
        >
          Clear All
        </button>
      </div>
      
      <div v-for="(count, name) in contents" :key="name" class="category-row">
        <span class="name">{{ name }}</span>
        <input 
          type="number" 
          :value="count"
          @input="updateCount(name, Number(($event.target as HTMLInputElement).value))"
        >
        <button class="danger" @click="removeCategory(name)">X</button>
      </div>

      <div class="add-row">
        <input 
            v-model="newCategoryName" 
            placeholder="Starter, Extender, ..." 
            @keyup.enter="addCategory"
        />
        <input 
            v-model.number="newCategoryCount" 
            type="number" 
            style="width: 60px" 
            @keyup.enter="addCategory"
        />
        <button @click="addCategory">Add</button>
      </div>
    </div>

    <div class="stats">
      <p>Cards defined: {{ currentCount }} / {{ deckSize }}</p>
      <p v-if="currentCount < deckSize" class="hint">Remaining {{ deckSize - currentCount }} cards will be empty.</p>
      <p v-if="currentCount > deckSize" class="error">Error: Defined cards exceed deck size!</p>
    </div>
  </div>
</template>

<style scoped>
.deck-builder {
  padding: 1.5rem;
  background: var(--surface-card);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.clear-btn {
  background: transparent;
  color: #ff4444;
  border: 1px solid #ff4444;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: rgba(255, 68, 68, 0.1);
}

.category-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.name {
  flex: 1;
  font-weight: 500;
}

.add-row {
  display: flex;
  gap: 10px;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.danger {
  background: #ff4444;
  color: white;
  border: none;
  padding: 2px 8px;
  border-radius: 4px;
  cursor: pointer;
}

.error {
  color: #ff4444;
  font-weight: bold;
  margin-top: 0.5rem;
  font-size: 0.9rem;
}

.input-slim {
  width: 50px;
}

.import-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.import-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid var(--border-color);
}

.import-section h3 {
  font-size: 1rem;
  margin-bottom: 0.75rem;
  color: var(--text-secondary);
}

.import-row {
  display: flex;
  gap: 10px;
}

.import-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--surface-base);
  color: var(--text-primary);
  font-size: 0.9rem;
}

.import-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.import-btn {
  padding: 8px 20px;
  background: linear-gradient(90deg, #3333ff, #ff00cc);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
  min-width: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.import-btn:hover:not(:disabled) {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

.import-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.progress-container {
  height: 4px;
  background-color: var(--surface-base);
  border-radius: 2px;
  overflow: hidden;
  width: 100%;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3333ff, #ff00cc);
  transition: width 0.3s ease-out;
}
</style>
