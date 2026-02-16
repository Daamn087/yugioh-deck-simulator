<script setup lang="ts">
import { ref, computed } from 'vue';
import { useSimulationStore } from '../store';
import type { CardEffectDefinition } from '../api';
import EffectEntry from './EffectEntry.vue';
import EffectForm from './EffectForm.vue';

const store = useSimulationStore();

const isCollapsed = ref(false);
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};

const allSubcategories = computed(() => {
  const subcats = new Set<string>();
  store.cardCategories.forEach(cat => {
    cat.subcategories.forEach(sub => subcats.add(sub));
  });
  return Array.from(subcats).sort();
});

const availableCategories = computed(() => {
    return store.cardCategories.map(cat => cat.name);
});

const addEffect = (effect: CardEffectDefinition) => {
  store.cardEffects.push(effect);
};

const removeEffect = (index: number) => {
  store.cardEffects.splice(index, 1);
};
</script>

<template>
  <div class="card overflow-hidden mt-4">
    <div 
        class="flex justify-between items-center cursor-pointer select-none p-4 sm:p-6 hover:bg-white/5 transition-colors" 
        @click="toggleCollapse"
    >
        <h2 class="text-lg sm:text-xl font-bold text-white flex items-center gap-2">
          <span>⚡</span> Card Effects
        </h2>
        <span class="text-text-secondary text-lg sm:text-xl transition-transform duration-300" :class="{ 'rotate-180': isCollapsed }">
          ▲
        </span>
    </div>

    <div v-show="!isCollapsed" class="p-6 pt-0 animate-in slide-in-from-top-4 duration-300">
        <p class="text-text-secondary text-sm mb-8">
          Define effects for specific cards. All effects are <strong class="text-white uppercase tracking-wider">Once-Per-Turn (OPT)</strong> and resolve in a single pass on the starting hand.
        </p>

        <div class="bg-primary/5 border border-primary/20 rounded-xl p-4 mb-8 shadow-inner">
            <h3 class="text-[10px] font-black uppercase tracking-[0.2em] text-primary mb-4 flex items-center gap-2">
              <span class="w-2 h-2 bg-primary rounded-full"></span>
              Supported Effects & Examples
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
                <div class="flex flex-col gap-2">
                    <div class="font-bold text-xs sm:text-sm text-white">Draw Cards</div>
                    <p class="text-[10px] sm:text-xs text-text-secondary leading-relaxed">Draws a fixed number of cards. If the deck is smaller than the draw count, the effect fails to activate.</p>
                    <div class="text-[9px] sm:text-[10px] font-bold text-primary italic mt-1">Example: <span class="bg-primary/10 px-1 rounded">Pot of Greed</span> (Draw 2)</div>
                </div>
                <div class="flex flex-col gap-2">
                    <div class="font-bold text-xs sm:text-sm text-white">Draw & Conditional Discard</div>
                    <p class="text-[10px] sm:text-xs text-text-secondary leading-relaxed">Draws cards, then checks if the hand contains cards with a specific Tag. If yes, it discards them. If it can't fulfill the discard count, the entire effect (including the draw) is reverted.</p>
                    <div class="text-[9px] sm:text-[10px] font-bold text-primary italic mt-1">Example: <span class="bg-primary/10 px-1 rounded">Allure of Darkness</span> (Draw 2, then Discard 1 DARK)</div>
                </div>
            </div>
        </div>

        <div class="flex flex-col gap-3 mb-8">
            <EffectEntry 
                v-for="(effect, index) in store.cardEffects" 
                :key="index"
                :effect="effect"
                :index="index"
                @remove="removeEffect(index)"
            />

            <div v-if="store.cardEffects.length === 0" class="text-center py-10 text-text-secondary/50 italic text-sm border-2 border-dashed border-white/5 rounded-xl">
                No card effects defined yet.
            </div>
        </div>

        <EffectForm 
            :available-categories="availableCategories"
            :all-subcategories="allSubcategories"
            @add="addEffect"
        />
    </div>
  </div>
</template>

<style scoped>
/* Scoped styles removed in favor of Tailwind CSS */
</style>
