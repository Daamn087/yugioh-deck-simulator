
<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Requirement } from '../api';
import { useSimulationStore } from '../store';
import RuleGroup from './RuleGroup.vue';

const isCollapsed = ref(false);
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};

const props = defineProps<{
  rules: Requirement[][];
  availableCategories: string[];
}>();

const emit = defineEmits<{
  (e: 'update:rules', rules: Requirement[][]): void;
}>();

const store = useSimulationStore();

// Compute all available options: categories + subcategories
const allOptions = computed(() => {
  const categories = props.availableCategories;
  const subcategories = new Set<string>();
  
  // Collect all unique subcategories
  store.cardCategories.forEach(cat => {
    cat.subcategories.forEach(sub => subcategories.add(sub));
  });
  
  return {
    categories,
    subcategories: Array.from(subcategories).sort()
  };
});

const addGroup = () => {
    // Start with a default requirement if possible
    const firstCat = props.availableCategories[0] || "Starter";
    const newRule: Requirement[] = [{ card_name: firstCat, min_count: 1, operator: 'AND' }];
    emit('update:rules', [...props.rules, newRule]);
};

const removeGroup = (index: number) => {
    const newRules = [...props.rules];
    newRules.splice(index, 1);
    emit('update:rules', newRules);
};
const updateGroup = (index: number, newGroup: Requirement[]) => {
    const newRules = [...props.rules];
    newRules[index] = newGroup;
    emit('update:rules', newRules);
};
</script>

<template>
  <div class="card overflow-hidden">
    <div 
        class="flex justify-between items-center cursor-pointer select-none p-6 hover:bg-white/5 transition-colors" 
        @click="toggleCollapse"
    >
        <h2 class="text-xl font-bold text-white flex items-center gap-2">
          <span>🏆</span> Success Conditions
        </h2>
        <span class="text-text-secondary text-xl transition-transform duration-300" :class="{ 'rotate-180': isCollapsed }">
          ▲
        </span>
    </div>
    
    <div v-show="!isCollapsed" class="p-6 pt-0 animate-in slide-in-from-top-4 duration-300">
        <p class="text-text-secondary text-sm mb-6 pb-4 border-b border-border-primary">
          The hand is successful if <strong class="text-primary uppercase tracking-wider">ANY</strong> of these groups are met (OR logic between groups).
        </p>

        <div class="flex flex-col gap-6">
            <div v-for="(group, gIndex) in rules" :key="gIndex" class="bg-surface-card border-l-4 border-primary rounded-r-lg p-5 shadow-inner relative group/item">
                <div class="flex justify-between items-center mb-4">
                    <span class="text-sm font-bold text-primary uppercase tracking-widest flex items-center gap-2">
                      <span class="w-6 h-6 flex items-center justify-center bg-primary text-white rounded-full text-[10px]">{{ gIndex + 1 }}</span>
                      Option {{ gIndex + 1 }} (All requirements must be true)
                    </span>
                    <button 
                      class="text-xs font-bold text-red-500 hover:text-white hover:bg-red-500 border border-red-500/30 px-3 py-1 rounded transition-all active:scale-95" 
                      @click.stop="removeGroup(gIndex)"
                    >
                      Remove
                    </button>
                </div>
                
                <RuleGroup 
                    :model-value="group"
                    :all-options="allOptions"
                    @update:model-value="updateGroup(gIndex, $event)"
                />
            </div>
        </div>

        <button 
          class="w-full mt-8 py-3 bg-gradient-to-r from-primary/20 to-blue-600/20 border border-primary/30 hover:border-primary text-primary font-bold rounded-xl transition-all active:scale-[0.98] uppercase tracking-widest text-sm flex items-center justify-center gap-2" 
          @click="addGroup"
        >
          <span>➕</span> Add Success Option (OR)
        </button>
    </div>
  </div>
</template>

<style scoped>
/* Scoped styles removed in favor of Tailwind CSS */
</style>
