<script setup lang="ts">
import { ref, computed } from 'vue';
import { useSimulationStore } from '../store';
import DeckImport from './DeckImport.vue';
import CardEntry from './CardEntry.vue';

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
    count: Math.max(0, newCardCount.value),
    subcategories: []
  });
  store.syncDeckContents();
  newCardName.value = '';
};

const updateCount = (categoryName: string, count: number) => {
  const category = store.cardCategories.find(c => c.name === categoryName);
  if (category) {
    category.count = Math.max(0, count);
    store.syncDeckContents();
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
      <img
        src="../assets/icons/yugioh_card_background.png"
        alt="yugioh_card_background"
        class="w-5"
      /> Deck Configuration
    </h2>
    
    <!-- Import Section -->
    <DeckImport />
    
    <!-- Global Stats -->
    <div class="flex flex-col sm:flex-row sm:flex-wrap gap-4 sm:gap-8 mb-8">
      <div class="flex items-center justify-between sm:justify-start gap-4 sm:pr-8 sm:border-r border-border-primary">
        <label class="text-sm font-medium text-text-secondary whitespace-nowrap">Total Deck Size </label>
        <input 
          type="number" 
          :value="deckSize" 
          min="0"
          class="w-16 sm:w-16 bg-[#2a2a2a] border border-[#444] rounded p-2 sm:p-1 text-center text-white focus:ring-2 focus:ring-primary outline-none"
          @input="emit('update:deckSize', Math.max(0, Number(($event.target as HTMLInputElement).value)))"
        >
      </div>
      <div class="flex items-center justify-between sm:justify-start gap-4">
        <label class="text-sm font-medium text-text-secondary whitespace-nowrap">Hand Size </label>
        <input 
          type="number" 
          :value="handSize" 
          min="0"
          class="w-16 sm:w-16 bg-[#2a2a2a] border border-[#444] rounded p-2 sm:p-1 text-center text-white focus:ring-2 focus:ring-primary outline-none"
          @input="emit('update:handSize', Math.max(0, Number(($event.target as HTMLInputElement).value)))"
        >
      </div>
    </div>

    <!-- Card List -->
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
            class="hidden sm:block text-xs font-bold text-red-500 hover:text-white hover:bg-red-500 border border-red-500/30 px-3 py-1 rounded-md transition-all active:scale-95" 
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
        <CardEntry 
          v-for="category in store.cardCategories" 
          :key="category.name"
          :category="category"
          :all-existing-subcategories="allExistingSubcategories"
          @update-count="updateCount"
          @delete-category="emit('delete-category', $event)"
        />

        <!-- Add Category Section -->
        <div class="flex flex-col sm:flex-row gap-3 mt-6 pt-6 border-t border-border-primary">
          <input 
              v-model="newCardName" 
              placeholder="Card name (e.g., Ash Blossom, Polymerization)" 
              class="w-full sm:flex-1 bg-[#2a2a2a] border border-border-primary rounded-xl px-4 py-4 sm:py-2 text-sm text-white focus:ring-2 focus:ring-primary outline-none"
              @keyup.enter="addCategory"
          />
          <div class="flex gap-3">
            <input 
                v-model.number="newCardCount" 
                type="number" 
                min="0"
                class="flex-1 sm:w-20 bg-[#2a2a2a] border border-border-primary rounded-xl px-2 py-4 sm:py-2 text-center text-sm text-white focus:ring-2 focus:ring-primary outline-none"
                @keyup.enter="addCategory"
            />
            <button @click="addCategory" class="flex-1 sm:flex-none bg-primary hover:bg-blue-500 px-8 py-4 sm:py-2 rounded-xl font-bold transition-all active:scale-95 shadow-lg shadow-primary/20 text-white">Add</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Summary -->
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
      <p v-if="currentCount > deckSize" class="text-[10px] sm:text-xs font-bold text-red-500 mt-2 bg-red-500/10 p-2 rounded border border-red-500/20 text-center">
        ❌ Error: Defined cards exceed deck size!
      </p>
    </div>
  </div>
</template>


<style scoped>
/* Scoped styles removed in favor of Tailwind CSS */
</style>
