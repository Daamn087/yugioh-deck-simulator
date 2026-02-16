
<script setup lang="ts">
import { ref, computed } from 'vue';
import { useSimulationStore } from '../store';
import { getTagColor } from '../utils/tagColors';

const props = defineProps<{
  deckSize: number;
  handSize: number;
  contents: Record<string, number>;
}>();

const emit = defineEmits<{
  (e: 'update:deckSize', size: number): void;
  (e: 'update:handSize', size: number): void;
  (e: 'update:contents', contents: Record<string, number>): void;
  (e: 'delete-category', name: string): void;
}>();

const store = useSimulationStore();

const newCardName = ref('');
const newCardCount = ref(3);
const selectedFile = ref<File | null>(null);
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


const isCardListCollapsed = ref(false);

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

const clearAll = () => {
  if (store.cardCategories.length === 0) return;
  if (confirm('Are you sure you want to clear all cards?')) {
    store.cardCategories = [];
    store.syncDeckContents();
  }
};
</script>

<template>
  <div class="card overflow-hidden">
    <h2 class="text-xl font-bold mb-6 text-primary flex items-center gap-2">
      <span>🎴</span> Deck Configuration
    </h2>
    
    <!-- Import Section -->
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
            class="w-full sm:min-w-[100px] flex items-center justify-center bg-gradient-to-r from-primary to-pink-500 hover:brightness-110 text-white font-bold py-3 sm:py-2 px-6 rounded-lg shadow-lg shadow-primary/20 transition-all active:scale-95 disabled:opacity-50 disabled:grayscale disabled:cursor-not-allowed"
          >
            <div v-if="importing" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            <span v-else>Import</span>
          </button>
        </div>
      </div>
      <p v-if="importError" class="mt-3 text-red-500 text-xs font-bold bg-red-500/10 p-2 rounded border border-red-500/20">{{ importError }}</p>
    </div>
    
    <div class="flex flex-col sm:flex-row sm:flex-wrap gap-4 sm:gap-8 mb-8">
      <div class="flex items-center justify-between sm:justify-start gap-4 sm:pr-8 sm:border-r border-border-primary">
        <label class="text-sm font-medium text-text-secondary whitespace-nowrap">Total Deck Size </label>
        <input 
          type="number" 
          :value="deckSize" 
          class="w-16 sm:w-16 bg-[#2a2a2a] border border-[#444] rounded p-2 sm:p-1 text-center text-white focus:ring-2 focus:ring-primary outline-none"
          @input="emit('update:deckSize', Number(($event.target as HTMLInputElement).value))"
        >
      </div>
      <div class="flex items-center justify-between sm:justify-start gap-4">
        <label class="text-sm font-medium text-text-secondary whitespace-nowrap">Hand Size </label>
        <input 
          type="number" 
          :value="handSize" 
          class="w-16 sm:w-16 bg-[#2a2a2a] border border-[#444] rounded p-2 sm:p-1 text-center text-white focus:ring-2 focus:ring-primary outline-none"
          @input="emit('update:handSize', Number(($event.target as HTMLInputElement).value))"
        >
      </div>
    </div>

    <div class="flex flex-col gap-4">
      <div 
        class="flex justify-between items-center mb-2 cursor-pointer select-none"
        @click="isCardListCollapsed = !isCardListCollapsed"
      >
        <h3 class="text-lg font-bold text-white flex items-center gap-2">
          <span>📝</span> Card Names 
          <span class="text-xs text-text-secondary font-normal sm:hidden">({{ store.cardCategories.length }})</span>
        </h3>
        <div class="flex items-center gap-3">
          <button 
            v-if="store.cardCategories.length > 0" 
            class="hidden sm:block text-xs font-bold text-red-400 hover:text-red-300 border border-red-900/50 hover:bg-red-900/20 bg-transparent px-3 py-1 rounded-md transition-all active:scale-95" 
            @click.stop="clearAll"
          >
            Clear All
          </button>
          <span class="text-primary transition-transform duration-300" :class="{ 'rotate-180': isCardListCollapsed }">
            ▼
          </span>
        </div>
      </div>
      
      <div v-show="!isCardListCollapsed" class="flex flex-col gap-4">
        <div v-for="category in store.cardCategories" :key="category.name" class="group flex flex-col gap-3 bg-white/5 hover:bg-white/[0.07] border border-border-primary p-3 sm:p-3 rounded-xl transition-all">
          <div class="flex flex-col sm:flex-row sm:items-center gap-3">
            <div class="flex items-center gap-3 flex-1 overflow-hidden">
              <input 
                v-if="editingCardName === category.name"
                v-model="editedCardName"
                class="flex-1 bg-[#2a2a2a] border-2 border-primary rounded px-2 py-1 text-white font-medium outline-none focus:ring-2 focus:ring-primary/50"
                @keyup.enter="saveCardName(category.name)"
                @keyup.esc="cancelEditCardName"
                @blur="saveCardName(category.name)"
                ref="nameEditInput"
              />
              <span 
                v-else
                class="flex-1 font-medium truncate cursor-pointer hover:bg-primary/10 px-2 py-1 rounded transition-colors" 
                @click="startEditingCardName(category.name)"
                :title="'Click to edit'"
              >
                {{ category.name }}
              </span>
              <button 
                v-if="editingCardName !== category.name"
                class="text-xs grayscale hover:grayscale-0 opacity-40 hover:opacity-100 transition-all p-1" 
                @click="startEditingCardName(category.name)"
                title="Edit card name"
              >
                ✏️
              </button>
            </div>
            
            <div class="flex items-center justify-between sm:justify-end gap-3 border-t sm:border-0 border-white/5 pt-3 sm:pt-0">
              <input 
                type="number" 
                :value="category.count"
                class="w-14 sm:w-12 bg-[#2a2a2a] border border-border-primary rounded px-2 py-2 sm:py-1 text-center text-sm font-bold"
                @input="updateCount(category.name, Number(($event.target as HTMLInputElement).value))"
              >
              <div class="flex items-center gap-2">
                <button 
                  class="bg-transparent border border-primary/40 hover:border-primary text-primary/80 hover:text-primary text-xs px-3 py-2 sm:py-1 rounded-lg transition-all active:scale-90 flex items-center gap-2 font-bold" 
                  @click="toggleSubcategoryEditor(category.name)" 
                  title="Manage tags"
                >
                  🏷️ <span class="hidden sm:inline">Tags</span> {{ category.subcategories.length }}
                </button>
                <button class="bg-red-500 hover:bg-red-600 text-white font-bold px-3 py-2 sm:p-1 rounded-lg sm:rounded min-w-[32px] sm:min-w-[28px] text-xs transition-colors shadow-lg active:scale-90" @click="removeCategory(category.name)">X</button>
              </div>
            </div>
          </div>
          
          <!-- Subcategory tags display -->
          <div v-if="category.subcategories.length > 0" class="flex flex-wrap gap-2">
            <span 
              v-for="subcat in [...category.subcategories].sort()" 
              :key="subcat" 
              class="text-[0.6rem] sm:text-[0.65rem] font-bold uppercase tracking-wider px-2 py-1 sm:py-0.5 rounded-full border shadow-sm"
              :style="{ 
                background: getTagColor(subcat),
                borderColor: 'rgba(255,255,255,0.1)'
              }"
            >
              {{ subcat }}
            </span>
          </div>
          
          <!-- Subcategory editor -->
          <div v-if="editingSubcategories === category.name" class="p-4 bg-primary/5 border border-primary/20 rounded-xl">
            <div class="flex items-center gap-2 mb-4">
              <h4 class="text-sm font-bold text-primary italic">Manage Tags for {{ category.name }}</h4>
            </div>
            <div class="flex flex-col gap-2 mb-4">
              <div v-for="subcat in [...category.subcategories].sort()" :key="subcat" class="flex justify-between items-center bg-white/5 px-3 py-2 sm:py-1.5 rounded-lg border border-white/5 hover:border-white/10 transition-all">
                <span class="text-sm shadow-sm">{{ subcat }}</span>
                <button class="text-red-500 hover:text-red-400 font-bold text-xl hover:scale-125 transition-transform px-2 leading-none" @click="removeSubcategory(category.name, subcat)">×</button>
              </div>
              <div v-if="category.subcategories.length === 0" class="text-center py-4 text-xs italic text-text-secondary border border-dashed border-white/10 rounded">
                No tags yet.
              </div>
            </div>
            <div class="flex flex-col sm:flex-row gap-2">
              <input 
                v-model="newSubcategory" 
                placeholder="Tag name... (Tab to autocomplete)" 
                @keyup.enter="addSubcategory(category.name)"
                @keydown="handleSubcategoryKeydown($event)"
                class="flex-1 bg-[#2a2a2a] border border-border-primary rounded-lg px-3 py-3 sm:py-1.5 text-xs text-white focus:ring-1 focus:ring-primary outline-none"
                list="subcategory-suggestions"
              />
              <button @click="addSubcategory(category.name)" class="w-full sm:w-auto bg-gradient-to-r from-primary to-blue-600 hover:brightness-110 px-4 py-3 sm:py-1.5 rounded-lg text-xs font-bold transition-all active:scale-95 text-white">Add Tag</button>
            </div>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row gap-3 mt-6 pt-6 border-t border-border-primary">
          <input 
              v-model="newCardName" 
              placeholder="Card name (e.g., Ash Blossom)" 
              class="w-full sm:flex-1 bg-[#2a2a2a] border border-border-primary rounded-xl px-4 py-4 sm:py-2 text-sm text-white focus:ring-2 focus:ring-primary outline-none"
              @keyup.enter="addCategory"
          />
          <div class="flex gap-3">
            <input 
                v-model.number="newCardCount" 
                type="number" 
                class="flex-1 sm:w-20 bg-[#2a2a2a] border border-border-primary rounded-xl px-2 py-4 sm:py-2 text-center text-sm text-white focus:ring-2 focus:ring-primary outline-none"
                @keyup.enter="addCategory"
            />
            <button @click="addCategory" class="flex-1 sm:flex-none bg-primary hover:bg-blue-500 px-8 py-4 sm:py-2 rounded-xl font-bold transition-all active:scale-95 shadow-lg shadow-primary/20 text-white">Add</button>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-8 pt-4 border-t border-white/5 flex flex-col gap-2">
      <div class="flex justify-between items-center">
        <p class="text-sm font-medium text-text-secondary">Cards defined:</p>
        <p class="text-sm font-black" :class="currentCount > deckSize ? 'text-red-500' : 'text-primary'">{{ currentCount }} / {{ deckSize }}</p>
      </div>
      <div class="w-full bg-[#1a1a1a] h-1.5 rounded-full overflow-hidden">
        <div 
          class="h-full transition-all duration-500"
          :class="currentCount > deckSize ? 'bg-red-500' : 'bg-primary'"
          :style="{ width: Math.min(100, (currentCount / deckSize) * 100) + '%' }"
        ></div>
      </div>
      <p v-if="currentCount < deckSize" class="text-[10px] sm:text-xs italic text-text-secondary/60">
        💡 Remaining {{ deckSize - currentCount }} cards will be empty slots.
      </p>
      <p v-if="currentCount > deckSize" class="text-[10px] sm:text-xs font-bold text-red-500 mt-2 bg-red-500/10 p-2 rounded text-center">
        ❌ Error: Defined cards exceed deck size!
      </p>
    </div>
  </div>
</template>


<style scoped>
/* Scoped styles removed in favor of Tailwind CSS */
</style>
