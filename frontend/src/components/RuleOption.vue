<script setup lang="ts">
import type { Requirement } from '../api';
import RuleGroup from './RuleGroup.vue';
import DeleteButton from './DeleteButton.vue';

const props = defineProps<{
    group: Requirement[];
    index: number;
    allOptions: {
        categories: string[];
        subcategories: string[];
    };
}>();

const emit = defineEmits<{
    (e: 'update:group', newGroup: Requirement[]): void;
    (e: 'remove'): void;
}>();
</script>

<template>
    <div class="bg-surface-card border-l-4 border-primary rounded-r-lg p-3 sm:p-5 shadow-inner relative group/item">
        <div class="flex justify-between items-center mb-4 gap-2">
            <span class="text-[10px] sm:text-sm font-bold text-primary uppercase tracking-widest flex items-center gap-2">
                <span class="w-5 h-5 sm:w-6 sm:h-6 flex items-center justify-center bg-primary text-white rounded-full text-[10px]">#{{ index + 1 }}</span>
                Option {{ index + 1 }}
            </span>
            <DeleteButton label="Remove" @click="emit('remove')" />
        </div>
        
        <RuleGroup 
            :model-value="group"
            :all-options="allOptions"
            @update:model-value="emit('update:group', $event)"
        />
    </div>
</template>
