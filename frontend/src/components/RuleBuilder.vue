
<script setup lang="ts">
import type { Requirement } from '../api';

const props = defineProps<{
  rules: Requirement[][];
  availableCategories: string[];
}>();

const emit = defineEmits<{
  (e: 'update:rules', rules: Requirement[][]): void;
}>();


const addGroup = () => {
    // Start with a default requirement if possible
    const firstCat = props.availableCategories[0] || "Starter";
    const newRule: Requirement[] = [{ card_name: firstCat, min_count: 1 }];
    emit('update:rules', [...props.rules, newRule]);
};

const removeGroup = (index: number) => {
    const newRules = [...props.rules];
    newRules.splice(index, 1);
    emit('update:rules', newRules);
};

const addReq = (groupIndex: number) => {
    const newRules = [...props.rules];
    const firstCat = props.availableCategories[0] || "Starter";
    if (newRules[groupIndex]) {
        newRules[groupIndex].push({ card_name: firstCat, min_count: 1 });
        emit('update:rules', newRules);
    }
};

const removeReq = (groupIndex: number, reqIndex: number) => {
    const newRules = [...props.rules];
    if (newRules[groupIndex]) {
        newRules[groupIndex].splice(reqIndex, 1);
        if (newRules[groupIndex].length === 0) {
            newRules.splice(groupIndex, 1);
        }
        emit('update:rules', newRules);
    }
};

const updateReq = (groupIndex: number, reqIndex: number, field: keyof Requirement, value: any) => {
    const newRules = [...props.rules];
    if (newRules[groupIndex] && newRules[groupIndex][reqIndex]) {
        const req = { ...newRules[groupIndex][reqIndex], [field]: value } as Requirement;
        newRules[groupIndex][reqIndex] = req;
        emit('update:rules', newRules);
    }
};
</script>

<template>
  <div class="rule-builder card">
    <h2>Success Conditions</h2>
    <p class="desc">The hand is successful if <strong>ANY</strong> of these groups are met.</p>

    <div class="rules-container">
        <div v-for="(group, gIndex) in rules" :key="gIndex" class="rule-group">
            <div class="group-header">
                <span>Option {{ gIndex + 1 }} (All must be true)</span>
                <button class="danger small" @click="removeGroup(gIndex)">Remove Option</button>
            </div>
            
            <div v-for="(req, rIndex) in group" :key="rIndex" class="req-row">
                <select 
                    :value="req.card_name"
                    @change="updateReq(gIndex, rIndex, 'card_name', ($event.target as HTMLSelectElement).value)"
                >
                    <option v-for="cat in availableCategories" :key="cat" :value="cat">{{ cat }}</option>
                </select>
                <span>>=</span>
                <input 
                    type="number" 
                    :value="req.min_count"
                    class="small-input"
                    @input="updateReq(gIndex, rIndex, 'min_count', Number(($event.target as HTMLInputElement).value))"
                >
                <button class="danger small" @click="removeReq(gIndex, rIndex)">x</button>
                <span v-if="rIndex < group.length - 1" class="and-label">AND</span>
            </div>

            <button class="secondary small" @click="addReq(gIndex)">+ AND Requirement</button>
        </div>
    </div>

    <button class="primary" @click="addGroup">+ Add Success Option (OR)</button>
  </div>
</template>

<style scoped>
.rule-builder {
  padding: 1.5rem;
  background: var(--surface-card);
  border-radius: 8px;
  border: 1px solid var(--border-color);
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

.and-label {
    font-weight: bold;
    color: var(--text-secondary);
    font-size: 0.8rem;
}
</style>
