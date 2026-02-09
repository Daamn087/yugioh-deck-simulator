<script setup lang="ts">
import { ref, computed } from 'vue';
import { useSimulationStore } from '../store';
import type { CardEffectDefinition } from '../api';

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
  <div class="card-effects-editor card">
    <div class="section-header" @click="toggleCollapse">
        <h2>Card Effects</h2>
        <span class="toggle-icon">{{ isCollapsed ? '▼' : '▲' }}</span>
    </div>

    <div v-show="!isCollapsed" class="section-content">
        <p class="desc">Define effects for specific cards. All effects are <strong>Once-Per-Turn (OPT)</strong> and resolve in a single pass on the starting hand.</p>

        <div class="effects-container">
            <div v-for="(effect, index) in store.cardEffects" :key="index" class="effect-item">
                <div class="effect-header">
                <span class="card-badge">{{ effect.card_name }}</span>
                <button class="danger small" @click="removeEffect(index)">Remove</button>
                </div>
                <div class="effect-content">
                <div v-if="effect.effect_type === 'draw'" class="effect-summary">
                    Draw <strong>{{ effect.parameters.count }}</strong> cards.
                </div>
                <div v-else-if="effect.effect_type === 'conditional_discard'" class="effect-summary">
                    Draw <strong>{{ effect.parameters.draw_count }}</strong> cards, then discard 
                    <strong>{{ effect.parameters.discard_count }}</strong> card(s) tagged 
                    <span class="tag-badge">{{ effect.parameters.discard_filter }}</span> 
                    from the final hand.
                </div>
                </div>
            </div>

            <div v-if="store.cardEffects.length === 0" class="empty-state">
                No card effects defined yet.
            </div>
        </div>

        <div class="add-effect-section">
            <h3>Add New Effect</h3>
            <div class="add-form">
                <div class="form-row">
                <div class="form-group flex-2">
                    <label>Card Name </label>
                    <select v-model="newEffect.card_name">
                    <option value="" disabled>Select a card from your deck</option>
                    <option v-for="cat in store.cardCategories" :key="cat.name" :value="cat.name">
                        {{ cat.name }}
                    </option>
                    </select>
                </div>
                <div class="form-group flex-1">
                    <label>Effect Type</label>
                    <select v-model="newEffect.effect_type" @change="updateEffectType">
                    <option v-for="type in effectTypes" :key="type.value" :value="type.value">
                        {{ type.label }}
                    </option>
                    </select>
                </div>
                </div>

                <div class="parameters-box">
                <!-- Draw Effect Params -->
                <div v-if="newEffect.effect_type === 'draw'" class="form-row">
                    <div class="form-group">
                    <label>Cards to Draw </label>
                    <input type="number" v-model.number="newEffect.parameters.count" min="1" max="40">
                    </div>
                </div>

                <!-- Conditional Discard Params -->
                <div v-if="newEffect.effect_type === 'conditional_discard'" class="form-row">
                    <div class="form-group">
                    <label>Cards to Draw</label>
                    <input type="number" v-model.number="newEffect.parameters.draw_count" min="1" max="40">
                    </div>
                    <div class="form-group">
                    <label>Discard Filter (Tag)</label>
                    <select v-model="newEffect.parameters.discard_filter">
                        <option value="" disabled>Select a tag</option>
                        <option v-for="subcat in allSubcategories" :key="subcat" :value="subcat">
                        {{ subcat }}
                        </option>
                    </select>
                    </div>
                    <div class="form-group">
                    <label>Discard Count</label>
                    <input type="number" v-model.number="newEffect.parameters.discard_count" min="1" max="10">
                    </div>
                </div>
                </div>

                <button class="primary full-width" @click="addEffect" :disabled="!newEffect.card_name">
                Add Effect to Simulation
                </button>
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
.card-effects-editor {
  padding: 1.5rem;
  background: var(--surface-card);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  margin-top: 1rem;
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
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.effects-container {
  margin-bottom: 2rem;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.effect-item {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  overflow: hidden;
}

.effect-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid var(--border-color);
}

.card-badge {
  font-weight: bold;
  color: var(--primary-color);
}

.effect-content {
  padding: 12px;
  font-size: 0.95rem;
}

.tag-badge {
  background: rgba(51, 51, 255, 0.2);
  color: #8888ff;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid rgba(51, 51, 255, 0.3);
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
  font-style: italic;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 6px;
  border: 1px dashed var(--border-color);
}

.add-effect-section {
  padding-top: 1.5rem;
  border-top: 2px solid var(--border-color);
}

.add-effect-section h3 {
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.add-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-row {
  display: flex;
  gap: 15px;
}

.flex-2 { flex: 2; }
.flex-1 { flex: 1; }

.parameters-box {
  padding: 15px;
  border-radius: 6px;
}

.full-width {
  width: 100%;
}

.danger.small {
  padding: 4px 8px;
  font-size: 0.8rem;
}

strong {
  color: var(--text-primary);
}
</style>
