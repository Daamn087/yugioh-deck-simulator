
<script setup lang="ts">
import { ref, computed } from 'vue';

const props = defineProps<{
  deckSize: number;
  contents: Record<string, number>;
}>();

const emit = defineEmits<{
  (e: 'update:deckSize', size: number): void;
  (e: 'update:contents', contents: Record<string, number>): void;
  (e: 'delete-category', name: string): void;
}>();

const newCategoryName = ref('');
const newCategoryCount = ref(3);

const currentCount = computed(() => {
  return Object.values(props.contents).reduce((a, b) => a + b, 0);
});

const addCategory = () => {
  if (!newCategoryName.value) return;
  const newContents = { ...props.contents, [newCategoryName.value]: newCategoryCount.value };
  emit('update:contents', newContents);
  newCategoryName.value = '';
};

const removeCategory = (name: string) => {
  emit('delete-category', name);
};

const updateCount = (name: string, count: number) => {
  const newContents = { ...props.contents, [name]: count };
  emit('update:contents', newContents);
};
</script>

<template>
  <div class="deck-builder card">
    <h2>Deck Configuration</h2>
    
    <div class="form-group">
      <label>Total Deck Size </label>
      <input 
        type="number" 
        :value="deckSize" 
        @input="emit('update:deckSize', Number(($event.target as HTMLInputElement).value))"
      >
    </div>

    <div class="contents-list">
      <h3>Card Categories</h3>
      
      <div v-for="(count, name) in contents" :key="name" class="category-row">
        <span class="name">{{ name }}</span>
        <input 
          type="number" 
          :value="count"
          @input="updateCount(name, Number(($event.target as HTMLInputElement).value))"
        >
        <button class="danger" @click="removeCategory(name)">X</button>
      </div>

      <div class="add-row">
        <input 
            v-model="newCategoryName" 
            placeholder="Category Name (e.g. Starter)" 
            @keyup.enter="addCategory"
        />
        <input 
            v-model.number="newCategoryCount" 
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
}
</style>
