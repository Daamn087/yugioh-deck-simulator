<script setup lang="ts">
import { ref, computed } from 'vue';
import { useSimulationStore } from '../store';
import type { CardEffectDefinition } from '../api';
import { getTagBadgeColors } from '../utils/tagColors';

const store = useSimulationStore();

const isCollapsed = ref(false);
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};

const newEffect = ref<CardEffectDefinition>({
  card_name: '',
  effect_type: 'draw',
  parameters: { count: 2 }
});

const effectTypes = [
  { value: 'draw', label: 'Draw Cards' },
  { value: 'conditional_discard', label: 'Draw & Conditional Discard' }
];

const allSubcategories = computed(() => {
  const subcats = new Set<string>();
  store.cardCategories.forEach(cat => {
    cat.subcategories.forEach(sub => subcats.add(sub));
  });
  return Array.from(subcats).sort();
});

const addEffect = () => {
  if (!newEffect.value.card_name) return;
  
  // Clone the effect to avoid reactivity issues with the form
  const effectToAdd = {
    card_name: newEffect.value.card_name,
    effect_type: newEffect.value.effect_type,
    parameters: { ...newEffect.value.parameters }
  };
  
  store.cardEffects.push(effectToAdd);
  
  // Reset card name for next add
  newEffect.value.card_name = '';
};

const updateEffectType = () => {
  if (newEffect.value.effect_type === 'draw') {
    newEffect.value.parameters = { count: 2 };
  } else if (newEffect.value.effect_type === 'conditional_discard') {
    newEffect.value.parameters = { 
      draw_count: 2, 
      discard_filter: allSubcategories.value[0] || '', 
      discard_count: 1 
    };
  }
};

const removeEffect = (index: number) => {
  store.cardEffects.splice(index, 1);
};
</script>

<template>
  <div class="card overflow-hidden mt-4">
    <div 
        class="flex justify-between items-center cursor-pointer select-none p-6 hover:bg-white/5 transition-colors" 
        @click="toggleCollapse"
    >
        <h2 class="text-xl font-bold text-white flex items-center gap-2">
          <span>⚡</span> Card Effects
        </h2>
        <span class="text-text-secondary text-xl transition-transform duration-300" :class="{ 'rotate-180': isCollapsed }">
          ▲
        </span>
    </div>

    <div v-show="!isCollapsed" class="p-6 pt-0 animate-in slide-in-from-top-4 duration-300">
        <p class="text-text-secondary text-sm mb-8">
          Define effects for specific cards. All effects are <strong class="text-white uppercase tracking-wider">Once-Per-Turn (OPT)</strong> and resolve in a single pass on the starting hand.
        </p>

        <div class="bg-primary/5 border border-primary/20 rounded-xl p-4 mb-10 shadow-inner">
            <h3 class="text-xs font-black uppercase tracking-[0.2em] text-primary mb-4 flex items-center gap-2">
              <span class="w-2 h-2 bg-primary rounded-full"></span>
              Supported Effects & Examples
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="flex flex-col gap-2">
                    <div class="font-bold text-sm text-white">Draw Cards</div>
                    <p class="text-xs text-text-secondary leading-relaxed">Draws a fixed number of cards. If the deck is smaller than the draw count, the effect fails to activate.</p>
                    <div class="text-[10px] font-bold text-primary italic mt-1">Example: <span class="bg-primary/10 px-1 rounded">Pot of Greed</span> (Draw 2)</div>
                </div>
                <div class="flex flex-col gap-2">
                    <div class="font-bold text-sm text-white">Draw & Conditional Discard</div>
                    <p class="text-xs text-text-secondary leading-relaxed">Draws cards, then checks if the hand contains cards with a specific Tag. If yes, it discards them. If it can't fulfill the discard count, the entire effect (including the draw) is reverted.</p>
                    <div class="text-[10px] font-bold text-primary italic mt-1">Example: <span class="bg-primary/10 px-1 rounded">Allure of Darkness</span> (Draw 2, then Discard 1 DARK)</div>
                </div>
            </div>
        </div>

        <div class="flex flex-col gap-3 mb-10">
            <div v-for="(effect, index) in store.cardEffects" :key="index" class="bg-white/5 border border-border-primary rounded-lg overflow-hidden transition-all hover:border-white/20">
                <div class="flex justify-between items-center px-4 py-2 bg-white/5 border-b border-white/5">
                <span class="text-xs font-black text-primary uppercase tracking-widest">{{ effect.card_name }}</span>
                <button class="text-[10px] font-bold text-red-500 hover:text-white hover:bg-red-500 px-2 py-0.5 rounded transition-all active:scale-95" @click="removeEffect(index)">Remove</button>
                </div>
                <div class="p-4 text-sm">
                <div v-if="effect.effect_type === 'draw'" class="flex items-center gap-2">
                    <span>Draw</span>
                    <strong class="text-primary text-lg">{{ effect.parameters.count }}</strong>
                    <span>cards.</span>
                </div>
                <div v-else-if="effect.effect_type === 'conditional_discard'" class="flex flex-wrap items-center gap-x-2 gap-y-1">
                    <span>Draw</span>
                    <strong class="text-primary text-lg">{{ effect.parameters.draw_count }}</strong>
                    <span>cards, then discard</span>
                    <strong class="text-pink-500 text-lg">{{ effect.parameters.discard_count }}</strong>
                    <span>card(s) tagged</span>
                    <span 
                      class="text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded-full border shadow-sm"
                      :style="{ 
                        background: getTagBadgeColors(effect.parameters.discard_filter).background,
                        color: getTagBadgeColors(effect.parameters.discard_filter).color,
                        borderColor: getTagBadgeColors(effect.parameters.discard_filter).border
                      }"
                    >{{ effect.parameters.discard_filter }}</span> 
                    <span>from the final hand.</span>
                </div>
                </div>
            </div>

            <div v-if="store.cardEffects.length === 0" class="text-center py-10 text-text-secondary/50 italic text-sm border-2 border-dashed border-white/5 rounded-xl">
                No card effects defined yet.
            </div>
        </div>

        <div class="pt-8 border-t-2 border-border-primary">
            <h3 class="text-lg font-bold text-white mb-6 flex items-center gap-2">
              <span>➕</span> Add New Effect
            </h3>
            <div class="flex flex-col gap-6 bg-black/20 p-6 rounded-xl border border-white/5">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="flex flex-col gap-2">
                    <label class="text-xs font-bold text-text-secondary uppercase tracking-widest pl-1">Card Name</label>
                    <select 
                      v-model="newEffect.card_name"
                      class="bg-[#2a2a2a] border border-border-primary rounded-lg px-4 py-2 text-sm text-white focus:ring-2 focus:ring-primary outline-none"
                    >
                      <option value="" disabled>Select a card from your deck</option>
                      <option v-for="cat in store.cardCategories" :key="cat.name" :value="cat.name">
                          {{ cat.name }}
                      </option>
                    </select>
                </div>
                <div class="flex flex-col gap-2">
                    <label class="text-xs font-bold text-text-secondary uppercase tracking-widest pl-1">Effect Type</label>
                    <select 
                      v-model="newEffect.effect_type" 
                      @change="updateEffectType"
                      class="bg-[#2a2a2a] border border-border-primary rounded-lg px-4 py-2 text-sm text-white focus:ring-2 focus:ring-primary outline-none"
                    >
                      <option v-for="type in effectTypes" :key="type.value" :value="type.value">
                          {{ type.label }}
                      </option>
                    </select>
                </div>
                </div>

                <div class="p-6 bg-white/5 border border-white/5 rounded-lg shadow-inner">
                <!-- Draw Effect Params -->
                <div v-if="newEffect.effect_type === 'draw'" class="flex flex-col gap-2 max-w-[200px]">
                    <label class="text-xs font-bold text-text-secondary uppercase tracking-widest pl-1">Cards to Draw</label>
                    <input 
                      type="number" 
                      v-model.number="newEffect.parameters.count" 
                      min="1" max="40"
                      class="bg-[#2a2a2a] border border-border-primary rounded-lg px-4 py-2 text-sm text-white focus:ring-2 focus:ring-primary outline-none text-center font-bold"
                    >
                </div>

                <!-- Conditional Discard Params -->
                <div v-if="newEffect.effect_type === 'conditional_discard'" class="grid grid-cols-1 sm:grid-cols-3 gap-6">
                    <div class="flex flex-col gap-2">
                      <label class="text-xs font-bold text-text-secondary uppercase tracking-widest pl-1">Cards to Draw</label>
                      <input 
                        type="number" 
                        v-model.number="newEffect.parameters.draw_count" 
                        min="1" max="40"
                        class="bg-[#2a2a2a] border border-border-primary rounded-lg px-4 py-2 text-sm text-white focus:ring-2 focus:ring-primary outline-none text-center font-bold"
                      >
                    </div>
                    <div class="flex flex-col gap-2">
                      <label class="text-xs font-bold text-text-secondary uppercase tracking-widest pl-1">Discard Filter (Tag)</label>
                      <select 
                        v-model="newEffect.parameters.discard_filter"
                        class="bg-[#2a2a2a] border border-border-primary rounded-lg px-4 py-2 text-sm text-white focus:ring-2 focus:ring-primary outline-none"
                      >
                          <option value="" disabled>Select a tag</option>
                          <option v-for="subcat in allSubcategories" :key="subcat" :value="subcat">
                          {{ subcat }}
                          </option>
                      </select>
                    </div>
                    <div class="flex flex-col gap-2">
                      <label class="text-xs font-bold text-text-secondary uppercase tracking-widest pl-1">Discard Count</label>
                      <input 
                        type="number" 
                        v-model.number="newEffect.parameters.discard_count" 
                        min="1" max="10"
                        class="bg-[#2a2a2a] border border-border-primary rounded-lg px-4 py-2 text-sm text-white focus:ring-2 focus:ring-primary outline-none text-center font-bold"
                      >
                    </div>
                </div>
                </div>

                <button 
                  class="w-full py-4 bg-gradient-to-r from-primary to-blue-600 hover:brightness-110 text-white font-black rounded-xl shadow-lg shadow-primary/20 transition-all active:scale-[0.99] disabled:opacity-50 disabled:grayscale uppercase tracking-widest" 
                  @click="addEffect" 
                  :disabled="!newEffect.card_name"
                >
                  Add Effect to Simulation
                </button>
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
/* Scoped styles removed in favor of Tailwind CSS */
</style>
