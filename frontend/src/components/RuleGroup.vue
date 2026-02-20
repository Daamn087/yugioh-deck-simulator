<script setup lang="ts">
import { computed } from 'vue';
import type { Requirement } from '../api';
import IconGreaterEqual from './icons/IconGreaterEqual.vue';
import IconEqual from './icons/IconEqual.vue';

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
    newRules.push({ card_name: firstCat, min_count: 1, operator: 'AND', comparison_operator: '>=' });
    emit('update:modelValue', newRules);
};

const addSubGroup = () => {
    const newRules = [...props.modelValue];
    const firstCat = props.allOptions.categories[0] || "Starter";
    // A group is a Requirement with sub_requirements
    // Initialize with one default requirement inside
    newRules.push({ 
        operator: 'AND',
        sub_requirements: [{ card_name: firstCat, min_count: 1, operator: 'AND', comparison_operator: '>=' }]
    });
    emit('update:modelValue', newRules);
};

const removeReq = (index: number) => {
    const newRules = [...props.modelValue];
    newRules.splice(index, 1);
    emit('update:modelValue', newRules);
};

const updateReq = (index: number, field: keyof Requirement, value: any) => {
    // If we're at top level (depth 0), don't allow changing operator to OR
    if (field === 'operator' && value === 'OR' && currentDepth.value === 0) {
        return;
    }
    const newRules = [...props.modelValue];
    let finalValue = value;
    if (field === 'min_count' && typeof value === 'number') {
        finalValue = Math.max(0, value);
    }
    const req = { ...newRules[index], [field]: finalValue } as Requirement;
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
    <div class="flex flex-col gap-3" :class="{ 'ml-3 sm:ml-6 p-2 sm:p-4 border-l-2 border-border-primary bg-black/10 rounded-lg': currentDepth > 0 }">
        <div v-for="(req, index) in modelValue" :key="index" class="flex flex-col">
            
            <div class="flex flex-col">
                <!-- If it has sub_requirements, it's a group -->
                <div v-if="req.sub_requirements" class="bg-white/5 rounded-lg overflow-hidden border border-white/5">
                    <div class="flex justify-between items-center px-3 py-1.5 bg-black/30 text-[10px] font-black uppercase tracking-widest text-text-secondary border-b border-white/5">
                        <span class="flex items-center gap-1.5">
                          <span class="w-1.5 h-1.5 bg-primary rounded-full animate-pulse"></span>
                          Parentheses Group (Depth {{ currentDepth + 1 }})
                        </span>
                        <button class="text-red-500 hover:text-red-400 font-bold px-2 transition-transform hover:scale-125" @click="removeReq(index)">×</button>
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
                <div v-else class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3 bg-white/5 hover:bg-white/10 p-3 sm:p-2 rounded-lg border border-transparent hover:border-white/5 transition-all">
                     <select 
                        :value="req.card_name"
                        class="flex-1 bg-[#2a2a2a] border border-border-primary rounded px-3 py-2 sm:py-1.5 text-sm text-white focus:ring-1 focus:ring-primary outline-none"
                        @change="updateReq(index, 'card_name', ($event.target as HTMLSelectElement).value)"
                    >
                        <optgroup label="Card Names" class="bg-[#1a1a1a]">
                            <option v-for="cat in allOptions.categories" :key="cat" :value="cat">{{ cat }}</option>
                        </optgroup>
                        <optgroup v-if="allOptions.subcategories.length > 0" label="Tags (Subcategories)" class="bg-[#1a1a1a]">
                            <option v-for="subcat in allOptions.subcategories" :key="subcat" :value="subcat">🏷️ {{ subcat }}</option>
                        </optgroup>
                    </select>
                    <div class="flex items-center gap-2 sm:gap-3">
                        <!-- Comparison operator toggle -->
                        <div class="flex gap-0.5 bg-black/30 p-0.5 rounded border border-white/10">
                            <button 
                                class="px-2 py-1 text-xs font-black rounded transition-all"
                                :class="(req.comparison_operator === '>=' || !req.comparison_operator) ? 'bg-primary text-white' : 'text-text-secondary hover:text-white'"
                                @click="updateReq(index, 'comparison_operator', '>=')"
                                title="At least"
                            >

                                <IconGreaterEqual class="w-3 text-white"/>
                            </button>
                            <button 
                                class="px-2 py-1 text-xs font-black rounded transition-all"
                                :class="req.comparison_operator === '=' ? 'bg-pink-600 text-white' : 'text-text-secondary hover:text-white'"
                                @click="updateReq(index, 'comparison_operator', '=')"
                                title="Exactly"
                            >
                                <IconEqual class="w-3 text-white"/>
                            </button>
                        </div>
                        <input 
                            type="number" 
                            :value="req.min_count"
                            min="0"
                            class="flex-1 sm:w-14 bg-[#2a2a2a] border border-border-primary rounded px-2 py-2 sm:py-1.5 text-center text-sm font-bold text-primary text-white"
                            @input="updateReq(index, 'min_count', Number(($event.target as HTMLInputElement).value))"
                        >
                        <button class="bg-red-500/10 hover:bg-red-500 text-red-500 hover:text-white border border-red-500/20 w-10 h-10 sm:w-7 sm:h-7 flex items-center justify-center rounded transition-all active:scale-90" @click="removeReq(index)">×</button>
                    </div>
                </div>
            </div>

            <!-- Operator between requirements -->
            <div v-if="index < modelValue.length - 1" class="flex items-center gap-4 my-2 ml-5">
                 <div class="flex gap-1 bg-black/20 p-1 rounded-md border border-white/5 shadow-inner">
                    <button 
                        class="px-3 py-1 text-[10px] font-black rounded transition-all uppercase tracking-tighter"
                        :class="(req.operator === 'AND' || !req.operator) ? 'bg-primary text-white shadow-lg' : 'text-text-secondary hover:text-white'"
                        @click="updateReq(index, 'operator', 'AND')"
                    >
                        AND
                    </button>
                    <button 
                        v-if="currentDepth > 0"
                        class="px-3 py-1 text-[10px] font-black rounded transition-all uppercase tracking-tighter"
                        :class="req.operator === 'OR' ? 'bg-pink-600 text-white shadow-lg' : 'text-text-secondary hover:text-white'"
                        @click="updateReq(index, 'operator', 'OR')"
                    >
                        OR
                    </button>
                </div>
                <div class="flex-1 h-[1px] bg-white/10"></div>
            </div>

        </div>

        <div class="flex flex-col sm:flex-row gap-2 mt-2">
            <button 
              class="flex-1 text-[10px] font-bold uppercase tracking-wider bg-white/5 hover:bg-white/10 border border-white/10 px-4 py-3 sm:py-2 rounded-md transition-all active:scale-95 text-text-secondary hover:text-white" 
              @click="addReq"
            >
              + Requirement
            </button>
            <button 
              class="flex-1 text-[10px] font-bold uppercase tracking-wider bg-white/5 hover:bg-white/10 border border-white/10 px-4 py-3 sm:py-2 rounded-md transition-all active:scale-95 text-text-secondary hover:text-white" 
              @click="addSubGroup"
            >
              + ( Group )
            </button>
        </div>
    </div>
</template>

<style scoped>
/* Scoped styles removed in favor of Tailwind CSS */
</style>
