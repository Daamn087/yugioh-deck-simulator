
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

const importDeck = async () => {
  if (!importUrl.value) return;
  
  importing.value = true;
  importError.value = null;
  
  try {
    await store.importFromDuelingBook(importUrl.value);
    importUrl.value = '';
  } catch (e: any) {
    importError.value = e.message || 'Failed to import deck';
  } finally {
    importing.value = false;
  }
};
</script>

<template>
  <div class="deck-builder card">
    <h2>Deck Configuration</h2>
    
    <!-- Import Section -->
    <div class="import-section">
      <h3>Import from DuelingBook</h3>
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
          {{ importing ? 'Importing...' : 'Import' }}
        </button>
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
      <h3>Card Categories</h3>
      
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
</style>
