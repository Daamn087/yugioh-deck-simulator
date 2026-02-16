<script setup lang="ts">
import { ref } from 'vue';
import type { CardEffectDefinition } from '../api';

const props = defineProps<{
    availableCategories: string[];
    allSubcategories: string[];
}>();

const emit = defineEmits<{
    (e: 'add', effect: CardEffectDefinition): void;
}>();

const newEffect = ref<CardEffectDefinition>({
  card_name: '',
  effect_type: 'draw',
  parameters: { count: 2 }
});

const effectTypes = [
  { value: 'draw', label: 'Draw Cards' },
  { value: 'conditional_discard', label: 'Draw & Conditional Discard' }
];

const addEffect = () => {
  if (!newEffect.value.card_name) return;
  
  const effectToAdd = {
    card_name: newEffect.value.card_name,
    effect_type: newEffect.value.effect_type,
    parameters: { ...newEffect.value.parameters }
  };

  if (effectToAdd.parameters.count !== undefined) {
    effectToAdd.parameters.count = Math.max(1, effectToAdd.parameters.count);
  }
  if (effectToAdd.parameters.draw_count !== undefined) {
    effectToAdd.parameters.draw_count = Math.max(1, effectToAdd.parameters.draw_count);
  }
  if (effectToAdd.parameters.discard_count !== undefined) {
    effectToAdd.parameters.discard_count = Math.max(1, effectToAdd.parameters.discard_count);
  }
  
  emit('add', effectToAdd as CardEffectDefinition);
  newEffect.value.card_name = '';
};

const updateEffectType = () => {
  if (newEffect.value.effect_type === 'draw') {
    newEffect.value.parameters = { count: 2 };
  } else if (newEffect.value.effect_type === 'conditional_discard') {
    newEffect.value.parameters = { 
      draw_count: 2, 
      discard_filter: props.allSubcategories[0] || '', 
      discard_count: 1 
    };
  }
};
</script>

<template>
    <div class="pt-6 sm:pt-8 border-t-2 border-border-primary">
        <h3 class="text-base sm:text-lg font-bold text-white mb-6 flex items-center gap-2">
            <span>➕</span> Add New Effect
        </h3>
        <div class="flex flex-col gap-4 sm:gap-6 bg-black/20 p-4 sm:p-6 rounded-xl border border-white/5">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
                <div class="flex flex-col gap-2">
                    <label class="text-[10px] font-bold text-text-secondary uppercase tracking-widest pl-1">Card Name</label>
                    <select 
                        v-model="newEffect.card_name"
                        class="bg-[#2a2a2a] border border-border-primary rounded-lg px-3 py-3 sm:py-2 text-sm text-white focus:ring-2 focus:ring-primary outline-none"
                    >
                        <option value="" disabled>Select a card from deck</option>
                        <option v-for="catName in availableCategories" :key="catName" :value="catName">
                            {{ catName }}
                        </option>
                    </select>
                </div>
                <div class="flex flex-col gap-2">
                    <label class="text-[10px] font-bold text-text-secondary uppercase tracking-widest pl-1">Effect Type</label>
                    <select 
                        v-model="newEffect.effect_type" 
                        @change="updateEffectType"
                        class="bg-[#2a2a2a] border border-border-primary rounded-lg px-3 py-3 sm:py-2 text-sm text-white focus:ring-2 focus:ring-primary outline-none"
                    >
                        <option v-for="type in effectTypes" :key="type.value" :value="type.value">
                            {{ type.label }}
                        </option>
                    </select>
                </div>
            </div>

            <div class="p-4 sm:p-6 bg-white/5 border border-white/5 rounded-lg shadow-inner">
                <!-- Draw Effect Params -->
                <div v-if="newEffect.effect_type === 'draw'" class="flex flex-col gap-2 max-w-[200px]">
                    <label class="text-[10px] font-bold text-text-secondary uppercase tracking-widest pl-1">Cards to Draw</label>
                    <input 
                        type="number" 
                        v-model.number="newEffect.parameters.count" 
                        min="1" max="40"
                        class="bg-[#2a2a2a] border border-border-primary rounded-lg px-4 py-3 sm:py-2 text-sm text-white focus:ring-2 focus:ring-primary outline-none text-center font-bold"
                    >
                </div>

                <!-- Conditional Discard Params -->
                <div v-if="newEffect.effect_type === 'conditional_discard'" class="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6">
                    <div class="flex flex-col gap-2">
                        <label class="text-[10px] font-bold text-text-secondary uppercase tracking-widest pl-1">Cards to Draw</label>
                        <input 
                            type="number" 
                            v-model.number="newEffect.parameters.draw_count" 
                            min="1" max="40"
                            class="bg-[#2a2a2a] border border-border-primary rounded-lg px-4 py-3 sm:py-2 text-sm text-white focus:ring-2 focus:ring-primary outline-none text-center font-bold"
                        >
                    </div>
                    <div class="flex flex-col gap-2">
                        <label class="text-[10px] font-bold text-text-secondary uppercase tracking-widest pl-1">Discard Filter (Tag)</label>
                        <select 
                            v-model="newEffect.parameters.discard_filter"
                            class="bg-[#2a2a2a] border border-border-primary rounded-lg px-3 py-3 sm:py-2 text-sm text-white focus:ring-2 focus:ring-primary outline-none"
                        >
                            <option value="" disabled>Tag</option>
                            <option v-for="subcat in allSubcategories" :key="subcat" :value="subcat">
                                {{ subcat }}
                            </option>
                        </select>
                    </div>
                    <div class="flex flex-col gap-2">
                        <label class="text-[10px] font-bold text-text-secondary uppercase tracking-widest pl-1">Discard Count</label>
                        <input 
                            type="number" 
                            v-model.number="newEffect.parameters.discard_count" 
                            min="1" max="10"
                            class="bg-[#2a2a2a] border border-border-primary rounded-lg px-4 py-3 sm:py-2 text-sm text-white focus:ring-2 focus:ring-primary outline-none text-center font-bold"
                        >
                    </div>
                </div>
            </div>

            <button 
                class="w-full py-4 bg-gradient-to-r from-primary to-blue-600 hover:brightness-110 text-white font-black rounded-xl shadow-lg shadow-primary/20 transition-all active:scale-[0.99] disabled:opacity-50 disabled:grayscale uppercase tracking-widest text-xs sm:text-sm" 
                @click="addEffect" 
                :disabled="!newEffect.card_name"
            >
                Add Effect to Simulation
            </button>
        </div>
    </div>
</template>
