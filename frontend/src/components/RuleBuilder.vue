
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
  <div class="rule-builder card">
    <div class="section-header" @click="toggleCollapse">
        <h2>Success Conditions</h2>
        <span class="toggle-icon">{{ isCollapsed ? '▼' : '▲' }}</span>
    </div>
    
    <div v-show="!isCollapsed" class="section-content">
        <p class="desc">The hand is successful if <strong>ANY</strong> of these groups are met.</p>

        <div class="rules-container">
            <div v-for="(group, gIndex) in rules" :key="gIndex" class="rule-group">
                <div class="group-header">
                    <span>Option {{ gIndex + 1 }} (All must be true)</span>
                    <button class="danger small" @click.stop="removeGroup(gIndex)">Remove Option</button>
                </div>
                
                <RuleGroup 
                    :model-value="group"
                    :all-options="allOptions"
                    @update:model-value="updateGroup(gIndex, $event)"
                />
            </div>
        </div>

        <button class="primary" @click="addGroup">+ Add Success Option (OR)</button>
    </div>
  </div>
</template>

<style scoped>
.rule-builder {
  padding: 1.5rem;
  background: var(--surface-card);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    user-select: none;
}

.section-header h2 {
    margin: 0;
}

.toggle-icon {
    font-size: 1.2rem;
    color: var(--text-secondary);
}

.section-content {
    margin-top: 1rem;
}

.desc {
    color: var(--text-secondary);
    margin-bottom: 1rem;
    font-size: 0.9rem;
}

.rule-group {
    background: rgba(255, 255, 255, 0.05);
    padding: 1rem;
    border-radius: 6px;
    margin-bottom: 1rem;
    border-left: 3px solid var(--primary-color);
}

.group-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-weight: bold;
    color: var(--primary-color);
}

.req-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}

.small-input {
    width: 50px;
}

.danger.small {
    padding: 2px 6px;
    font-size: 0.8rem;
}

.secondary.small {
    font-size: 0.8rem;
    margin-top: 5px;
}

.operator-toggle {
    display: flex;
    gap: 4px;
    margin-left: 8px;
}

.operator-btn {
    padding: 4px 10px;
    font-size: 0.75rem;
    font-weight: bold;
    border: 1px solid var(--border-color);
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-secondary);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
}

.operator-btn:hover {
    background: rgba(255, 255, 255, 0.1);
}

.operator-btn.active {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
}
</style>
