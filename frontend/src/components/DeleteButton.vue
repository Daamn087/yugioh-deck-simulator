<script setup lang="ts">
defineProps<{
  label?: string;
}>();

defineEmits<{
  (e: 'click'): void;
}>();
</script>

<template>
  <button 
    class="bg-red-500 hover:bg-red-600 text-white font-bold px-3 py-2 sm:p-1 rounded-lg sm:rounded min-w-[32px] sm:min-w-[28px] text-xs transition-colors shadow-lg active:scale-90" 
    @click="$emit('click')"
  >
    {{ label || 'X' }}
  </button>
</template>
