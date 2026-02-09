<script setup lang="ts">
import { computed } from 'vue';
import type { Requirement } from '../api';

const props = defineProps<{
    modelValue: Requirement[];
    allOptions: { categories: string[]; subcategories: string[] };
    depth?: number;
}>();

const emit = defineEmits<{
    (e: 'update:modelValue', rules: Requirement[]): void;
}>();

// Ensure depth defaults to 0
const currentDepth = computed(() => props.depth || 0);

const addReq = () => {
    const newRules = [...props.modelValue];
    const firstCat = props.allOptions.categories[0] || "Starter";
    newRules.push({ card_name: firstCat, min_count: 1, operator: 'AND' });
    emit('update:modelValue', newRules);
};

const addSubGroup = () => {
    const newRules = [...props.modelValue];
    const firstCat = props.allOptions.categories[0] || "Starter";
    // A group is a Requirement with sub_requirements
    // Initialize with one default requirement inside
    newRules.push({ 
        operator: 'AND',
        sub_requirements: [{ card_name: firstCat, min_count: 1, operator: 'AND' }]
    });
    emit('update:modelValue', newRules);
};

const removeReq = (index: number) => {
    const newRules = [...props.modelValue];
    newRules.splice(index, 1);
    emit('update:modelValue', newRules);
};

const updateReq = (index: number, field: keyof Requirement, value: any) => {
    const newRules = [...props.modelValue];
    const req = { ...newRules[index], [field]: value } as Requirement;
    newRules[index] = req;
    emit('update:modelValue', newRules);
};

const updateSubRequirements = (index: number, newSubReqs: Requirement[]) => {
    const newRules = [...props.modelValue];
    const req = { ...newRules[index], sub_requirements: newSubReqs } as Requirement;
    newRules[index] = req;
    emit('update:modelValue', newRules);
};

</script>

<template>
    <div class="rule-group-container" :class="{ 'nested': currentDepth > 0 }">
        <div v-for="(req, index) in modelValue" :key="index" class="req-item">
            
            <div class="req-content">
                <!-- If it has sub_requirements, it's a group -->
                <div v-if="req.sub_requirements" class="nested-group">
                    <div class="nested-header">
                        <span class="depth-marker">Parentheses Group (Depth {{ currentDepth + 1 }})</span>
                        <button class="danger small" @click="removeReq(index)">x</button>
                    </div>
                    <!-- Recursive Component! -->
                    <RuleGroup 
                        :model-value="req.sub_requirements"
                        :all-options="allOptions"
                        :depth="currentDepth + 1"
                        @update:model-value="updateSubRequirements(index, $event)"
                    />
                </div>

                <!-- Otherwise it's a single requirement -->
                <div v-else class="single-req">
                     <select 
                        :value="req.card_name"
                        @change="updateReq(index, 'card_name', ($event.target as HTMLSelectElement).value)"
                    >
                        <optgroup label="Card Names">
                            <option v-for="cat in allOptions.categories" :key="cat" :value="cat">{{ cat }}</option>
                        </optgroup>
                        <optgroup v-if="allOptions.subcategories.length > 0" label="Tags (Subcategories)">
                            <option v-for="subcat in allOptions.subcategories" :key="subcat" :value="subcat">🏷️ {{ subcat }}</option>
                        </optgroup>
                    </select>
                    <span>>=</span>
                    <input 
                        type="number" 
                        :value="req.min_count"
                        class="small-input"
                        @input="updateReq(index, 'min_count', Number(($event.target as HTMLInputElement).value))"
                    >
                    <button class="danger small" @click="removeReq(index)">x</button>
                </div>
            </div>

            <!-- Operator between requirements -->
            <div v-if="index < modelValue.length - 1" class="operator-row">
                 <div class="operator-toggle">
                    <button 
                        :class="['operator-btn', { active: req.operator === 'AND' || !req.operator }]"
                        @click="updateReq(index, 'operator', 'AND')"
                    >
                        AND
                    </button>
                    <button 
                        :class="['operator-btn', { active: req.operator === 'OR' }]"
                        @click="updateReq(index, 'operator', 'OR')"
                    >
                        OR
                    </button>
                </div>
                <div class="connector-line"></div>
            </div>

        </div>

        <div class="add-buttons">
            <button class="secondary small" @click="addReq">+ Requirement</button>
            <button class="secondary small" @click="addSubGroup">+ ( Group )</button>
        </div>
    </div>
</template>

<style scoped>
.rule-group-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.rule-group-container.nested {
    margin-left: 20px;
    padding: 10px;
    border-left: 2px solid var(--border-color);
    background: rgba(0, 0, 0, 0.1);
    border-radius: 4px;
}

.req-item {
    display: flex;
    flex-direction: column;
}

.single-req {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.05);
    padding: 6px;
    border-radius: 4px;
}

.nested-group {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 4px;
}

.nested-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 8px;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 4px 4px 0 0;
    font-size: 0.8em;
    color: var(--text-secondary);
}

.operator-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 4px 0 4px 20px;
}

.connector-line {
    flex-grow: 1;
    height: 1px;
    background: var(--border-color);
    opacity: 0.3;
}

.operator-toggle {
    display: flex;
    gap: 4px;
}

.operator-btn {
    padding: 2px 8px;
    font-size: 0.7rem;
    font-weight: bold;
    border: 1px solid var(--border-color);
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-secondary);
    border-radius: 4px;
    cursor: pointer;
}

.operator-btn.active {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
}

.small-input {
    width: 50px;
}

.add-buttons {
    display: flex;
    gap: 8px;
    margin-top: 8px;
}

.secondary.small {
    font-size: 0.8rem;
    padding: 4px 8px;
}

.danger.small {
    padding: 2px 6px;
    font-size: 0.8rem;
}
</style>
