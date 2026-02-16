<script setup lang="ts">
defineProps<{
  count: number;
}>();

defineEmits<{
  (e: 'click'): void;
}>();
</script>

<template>
  <button 
    class="bg-transparent border border-primary/40 hover:border-primary text-primary/80 hover:text-primary text-xs px-3 py-2 sm:py-1 rounded-lg transition-all active:scale-90 flex items-center gap-2 font-bold" 
    @click="$emit('click')" 
    title="Manage tags"
  >
    <span class="mt-[1px]">🏷️</span> {{ count }}
  </button>
</template>
