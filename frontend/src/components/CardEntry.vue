<script setup lang="ts">
import { ref, nextTick } from 'vue';
import { useSimulationStore } from '../store';
import { getTagColor } from '../utils/tagColors';
import TagButton from './TagButton.vue';
import DeleteButton from './DeleteButton.vue';

const props = defineProps<{
  category: {
    name: string;
    count: number;
    subcategories: string[];
  };
  allExistingSubcategories: string[];
}>();

const emit = defineEmits<{
  (e: 'update-count', name: string, count: number): void;
  (e: 'delete-category', name: string): void;
}>();

const store = useSimulationStore();

const editingSubcategories = ref(false);
const newSubcategory = ref('');
const editingCardName = ref(false);
const editedCardName = ref(props.category.name);
const nameEditInput = ref<HTMLInputElement | null>(null);
const isProcessingSave = ref(false);

const toggleSubcategoryEditor = () => {
  editingSubcategories.value = !editingSubcategories.value;
  newSubcategory.value = '';
};

const startEditingCardName = () => {
  editingCardName.value = true;
  editedCardName.value = props.category.name;
  nextTick(() => {
    nameEditInput.value?.focus();
    nameEditInput.value?.select();
  });
};

const saveCardName = async () => {
  if (isProcessingSave.value) return;
  
  if (!editedCardName.value.trim() || editedCardName.value === props.category.name) {
    editingCardName.value = false;
    return;
  }
  
  isProcessingSave.value = true;
  const category = store.cardCategories.find(c => c.name === props.category.name);
  if (category) {
    category.name = editedCardName.value.trim();
    store.syncDeckContents();
  }
  editingCardName.value = false;
  isProcessingSave.value = false;
};

const cancelEditCardName = () => {
  isProcessingSave.value = true;
  editingCardName.value = false;
  nextTick(() => {
    isProcessingSave.value = false;
  });
};

const addSubcategory = () => {
  if (!newSubcategory.value.trim()) return;
  const category = store.cardCategories.find(c => c.name === props.category.name);
  if (category && !category.subcategories.includes(newSubcategory.value.trim())) {
    category.subcategories.push(newSubcategory.value.trim());
    newSubcategory.value = '';
  }
};

const removeSubcategory = (subcategory: string) => {
  const category = store.cardCategories.find(c => c.name === props.category.name);
  if (category) {
    category.subcategories = category.subcategories.filter(s => s !== subcategory);
  }
};

const handleSubcategoryKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Tab' && newSubcategory.value && props.allExistingSubcategories.length > 0) {
    const match = props.allExistingSubcategories.find(sub => 
      sub.toLowerCase().startsWith(newSubcategory.value.toLowerCase())
    );
    if (match) {
      event.preventDefault();
      newSubcategory.value = match;
    }
  }
};
</script>

<template>
  <div class="group flex flex-col gap-3 bg-white/5 hover:bg-white/[0.07] border border-border-primary p-3 sm:p-3 rounded-xl transition-all">
    <div class="flex flex-col sm:flex-row sm:items-center gap-3">
      <div class="flex items-center gap-3 flex-1 overflow-hidden">
        <input 
          v-if="editingCardName"
          v-model="editedCardName"
          class="flex-1 bg-[#2a2a2a] border-2 border-primary rounded px-2 py-1 text-white font-medium outline-none focus:ring-2 focus:ring-primary/50"
          @keyup.enter="saveCardName"
          @keydown.esc.stop="cancelEditCardName"
          @blur="saveCardName"
          ref="nameEditInput"
        />
        <span 
          v-else
          class="flex-1 font-medium truncate cursor-pointer hover:bg-primary/10 px-2 py-1 rounded transition-colors" 
          @click="startEditingCardName"
          :title="'Click to edit'"
        >
          {{ category.name }}
        </span>
        <button 
          v-if="!editingCardName"
          class="text-xs grayscale hover:grayscale-0 opacity-40 hover:opacity-100 transition-all p-1" 
          @click="startEditingCardName"
          title="Edit card name"
        >
          ✏️
        </button>
      </div>
      
      <div class="flex items-center justify-between sm:justify-end gap-3 border-t sm:border-0 border-white/5 pt-3 sm:pt-0">
        <input 
          type="number" 
          :value="category.count"
          min="0"
          class="w-14 sm:w-12 bg-[#2a2a2a] border border-border-primary rounded px-2 py-2 sm:py-1 text-center text-sm font-bold"
          @input="emit('update-count', category.name, Number(($event.target as HTMLInputElement).value))"
        >
        <div class="flex items-center gap-2">
          <TagButton :count="category.subcategories.length" @click="toggleSubcategoryEditor" />
          <DeleteButton @click="emit('delete-category', category.name)" />
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
    <div v-if="editingSubcategories" class="p-4 bg-primary/5 border border-primary/20 rounded-xl animate-in slide-in-from-top-2 duration-200">
      <div class="flex items-center gap-2 mb-4">
        <h4 class="text-sm font-bold text-primary italic">Manage Tags for {{ category.name }}</h4>
      </div>
      <div class="flex flex-col gap-2 mb-4">
        <div v-for="subcat in [...category.subcategories].sort()" :key="subcat" class="flex justify-between items-center bg-white/5 px-3 py-2 sm:py-1.5 rounded-lg border border-white/5 hover:border-white/10 transition-all">
          <span class="text-sm shadow-sm">{{ subcat }}</span>
          <button class="text-red-500 hover:text-red-400 font-bold text-xl hover:scale-125 transition-transform px-2 leading-none" @click="removeSubcategory(subcat)">×</button>
        </div>
        <div v-if="category.subcategories.length === 0" class="text-center py-4 text-xs italic text-text-secondary border border-dashed border-white/10 rounded">
          No tags yet.
        </div>
      </div>
      <div class="flex flex-col sm:flex-row gap-2">
        <input 
          v-model="newSubcategory" 
          placeholder="Tag name... (Tab to autocomplete)" 
          @keyup.enter="addSubcategory"
          @keydown.esc.stop="toggleSubcategoryEditor"
          @keydown="handleSubcategoryKeydown($event)"
          class="flex-1 bg-[#2a2a2a] border border-border-primary rounded-lg px-3 py-3 sm:py-1.5 text-xs text-white focus:ring-1 focus:ring-primary outline-none"
          list="subcategory-suggestions"
        />
        <datalist id="subcategory-suggestions">
          <option v-for="subcat in allExistingSubcategories" :key="subcat" :value="subcat" />
        </datalist>
        <button @click="addSubcategory" class="w-full sm:w-auto bg-gradient-to-r from-primary to-blue-600 hover:brightness-110 px-4 py-3 sm:py-1.5 rounded-lg text-xs font-bold transition-all active:scale-95 text-white">Add Tag</button>
      </div>
    </div>
  </div>
</template>
