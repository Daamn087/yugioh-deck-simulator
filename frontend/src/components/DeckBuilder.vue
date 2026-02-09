
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

const newCardName = ref('');
const newCardCount = ref(3);
const importUrl = ref('');
const importing = ref(false);
const importError = ref<string | null>(null);
const editingSubcategories = ref<string | null>(null);
const newSubcategory = ref('');
const editingCardName = ref<string | null>(null);
const editedCardName = ref('');

const currentCount = computed(() => {
  return store.cardCategories.reduce((sum, cat) => sum + cat.count, 0);
});

// Compute all existing subcategories for autocomplete
const allExistingSubcategories = computed(() => {
  const subcats = new Set<string>();
  store.cardCategories.forEach(cat => {
    cat.subcategories.forEach(sub => subcats.add(sub));
  });
  return Array.from(subcats).sort();
});

const addCategory = () => {
  if (!newCardName.value) return;
  store.cardCategories.push({
    name: newCardName.value,
    count: newCardCount.value,
    subcategories: []
  });
  store.syncDeckContents();
  newCardName.value = '';
};

const removeCategory = (name: string) => {
  emit('delete-category', name);
};

const updateCount = (categoryName: string, count: number) => {
  const category = store.cardCategories.find(c => c.name === categoryName);
  if (category) {
    category.count = count;
    store.syncDeckContents();
  }
};

const addSubcategory = (categoryName: string) => {
  if (!newSubcategory.value.trim()) return;
  const category = store.cardCategories.find(c => c.name === categoryName);
  if (category && !category.subcategories.includes(newSubcategory.value.trim())) {
    category.subcategories.push(newSubcategory.value.trim());
    newSubcategory.value = '';
  }
};

const removeSubcategory = (categoryName: string, subcategory: string) => {
  const category = store.cardCategories.find(c => c.name === categoryName);
  if (category) {
    category.subcategories = category.subcategories.filter(s => s !== subcategory);
  }
};

const toggleSubcategoryEditor = (categoryName: string) => {
  editingSubcategories.value = editingSubcategories.value === categoryName ? null : categoryName;
  newSubcategory.value = '';
};

const startEditingCardName = (categoryName: string) => {
  editingCardName.value = categoryName;
  editedCardName.value = categoryName;
};

const saveCardName = (oldName: string) => {
  if (!editedCardName.value.trim() || editedCardName.value === oldName) {
    editingCardName.value = null;
    return;
  }
  
  const category = store.cardCategories.find(c => c.name === oldName);
  if (category) {
    category.name = editedCardName.value.trim();
    store.syncDeckContents();
  }
  editingCardName.value = null;
};

const cancelEditCardName = () => {
  editingCardName.value = null;
};

const handleSubcategoryKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Tab' && newSubcategory.value && allExistingSubcategories.value.length > 0) {
    // Find first matching suggestion
    const match = allExistingSubcategories.value.find(sub => 
      sub.toLowerCase().startsWith(newSubcategory.value.toLowerCase())
    );
    if (match) {
      event.preventDefault();
      newSubcategory.value = match;
    }
  }
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
  if (store.cardCategories.length === 0) return;
  if (confirm('Are you sure you want to clear all cards?')) {
    store.cardCategories = [];
    store.syncDeckContents();
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
        <h3>Card Names</h3>
        <button 
          v-if="store.cardCategories.length > 0" 
          class="clear-btn" 
          @click="clearAll"
        >
          Clear All
        </button>
      </div>
      
      <div v-for="category in store.cardCategories" :key="category.name" class="category-container">
        <div class="category-row">
          <input 
            v-if="editingCardName === category.name"
            v-model="editedCardName"
            class="name-edit-input"
            @keyup.enter="saveCardName(category.name)"
            @keyup.esc="cancelEditCardName"
            @blur="saveCardName(category.name)"
            ref="nameEditInput"
          />
          <span 
            v-else
            class="name editable" 
            @dblclick="startEditingCardName(category.name)"
            :title="'Double-click to edit'"
          >
            {{ category.name }}
          </span>
          <button 
            v-if="editingCardName !== category.name"
            class="edit-btn" 
            @click="startEditingCardName(category.name)"
            title="Edit card name"
          >
            ✏️
          </button>
          <input 
            type="number" 
            :value="category.count"
            @input="updateCount(category.name, Number(($event.target as HTMLInputElement).value))"
          >
          <button class="tag-btn" @click="toggleSubcategoryEditor(category.name)" title="Manage tags">
            🏷️ {{ category.subcategories.length }}
          </button>
          <button class="danger" @click="removeCategory(category.name)">X</button>
        </div>
        
        <!-- Subcategory tags display -->
        <div v-if="category.subcategories.length > 0" class="subcategory-chips">
          <span v-for="subcat in category.subcategories" :key="subcat" class="chip">
            {{ subcat }}
          </span>
        </div>
        
        <!-- Subcategory editor -->
        <div v-if="editingSubcategories === category.name" class="subcategory-editor">
          <div class="editor-header">
            <h4>Manage Tags for {{ category.name }}</h4>
          </div>
          <div class="tag-list">
            <div v-for="subcat in category.subcategories" :key="subcat" class="tag-item">
              <span>{{ subcat }}</span>
              <button class="remove-tag" @click="removeSubcategory(category.name, subcat)">×</button>
            </div>
            <div v-if="category.subcategories.length === 0" class="no-tags">
              No tags yet. Add tags to group cards for success conditions.
            </div>
          </div>
          <div class="add-tag-row">
            <input 
              v-model="newSubcategory" 
              placeholder="e.g., Starter, Extender, Lunalight Monster (Tab to autocomplete)" 
              @keyup.enter="addSubcategory(category.name)"
              @keydown="handleSubcategoryKeydown($event)"
              class="tag-input"
              list="subcategory-suggestions"
            />
            <datalist id="subcategory-suggestions">
              <option v-for="subcat in allExistingSubcategories" :key="subcat" :value="subcat" />
            </datalist>
            <button @click="addSubcategory(category.name)" class="add-tag-btn">Add Tag</button>
          </div>
        </div>
      </div>

      <div class="add-row">
        <input 
            v-model="newCardName" 
            placeholder="Card name (e.g., Ash Blossom, Polymerization)" 
            @keyup.enter="addCategory"
        />
        <input 
            v-model.number="newCardCount" 
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

.name.editable {
  cursor: pointer;
  transition: all 0.2s;
  padding: 4px 8px;
  border-radius: 4px;
}

.name.editable:hover {
  background: rgba(51, 51, 255, 0.1);
}

.name-edit-input {
  flex: 1;
  padding: 4px 8px;
  border: 2px solid #9898ee;
  border-radius: 4px;
  background: var(--surface-base);
  color: var(--text-primary);
  font-weight: 500;
  font-size: 1rem;
}

.edit-btn {
  background: transparent;
  border: 1px solid #888;
  color: #888;
  padding: 2px 6px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.edit-btn:hover {
  background: rgba(136, 136, 136, 0.1);
  border-color: #9898ee;
  color: #9898ee;
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
  background: linear-gradient(90deg, #9898ee, #ff00cc);
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
  background: linear-gradient(90deg, #9898ee, #ff00cc);
  transition: width 0.3s ease-out;
}

/* Subcategory styles */
.category-container {
  margin-bottom: 1rem;
}

.tag-btn {
  background: transparent;
  border: 1px solid #9898ee;
  color: #9898ee;
  padding: 2px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.tag-btn:hover {
  background: rgba(51, 51, 255, 0.1);
}

.subcategory-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
  margin-left: 0;
  padding-left: 0;
}

.chip {
  background: linear-gradient(135deg, #9898ee, #5555ff);
  color: white;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.subcategory-editor {
  background: rgba(51, 51, 255, 0.05);
  border: 1px solid rgba(51, 51, 255, 0.2);
  border-radius: 6px;
  padding: 1rem;
  margin-top: 8px;
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.editor-header h4 {
  margin: 0 0 0.75rem 0;
  font-size: 0.9rem;
  color: var(--primary-color);
}

.tag-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 0.75rem;
}

.tag-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  padding: 6px 10px;
  border-radius: 4px;
}

.tag-item span {
  font-size: 0.85rem;
}

.remove-tag {
  background: transparent;
  border: none;
  color: #ff4444;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 6px;
  transition: all 0.2s;
}

.remove-tag:hover {
  color: #ff6666;
  transform: scale(1.2);
}

.no-tags {
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-style: italic;
  padding: 1rem;
  text-align: center;
}

.add-tag-row {
  display: flex;
  gap: 8px;
}

.tag-input {
  flex: 1;
  padding: 6px 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--surface-base);
  color: var(--text-primary);
  font-size: 0.85rem;
}

.add-tag-btn {
  padding: 6px 12px;
  background: linear-gradient(90deg, #9898ee, #5555ff);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s;
}

.add-tag-btn:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}
</style>
