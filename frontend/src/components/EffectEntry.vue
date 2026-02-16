<script setup lang="ts">
import type { CardEffectDefinition } from '../api';
import { getTagBadgeColors } from '../utils/tagColors';
import DeleteButton from './DeleteButton.vue';

const props = defineProps<{
  effect: CardEffectDefinition;
  index: number;
}>();

const emit = defineEmits<{
  (e: 'remove'): void;
}>();
</script>

<template>
  <div class="bg-white/5 border border-border-primary rounded-lg overflow-hidden transition-all hover:border-white/20">
    <div class="flex justify-between items-center px-4 py-2 bg-white/5 border-b border-white/5">
      <span class="text-[10px] font-black text-primary uppercase tracking-widest">{{ effect.card_name }}</span>
      <DeleteButton label="Remove" @click="emit('remove')" />
    </div>
    <div class="p-3 sm:p-4 text-xs sm:text-sm">
      <div v-if="effect.effect_type === 'draw'" class="flex items-center gap-2">
        <span>Draw</span>
        <strong class="text-primary text-base sm:text-lg">{{ effect.parameters.count }}</strong>
        <span>cards.</span>
      </div>
      <div v-else-if="effect.effect_type === 'conditional_discard'" class="flex flex-wrap items-center gap-x-2 gap-y-1">
        <span>Draw</span>
        <strong class="text-primary text-base sm:text-lg">{{ effect.parameters.draw_count }}</strong>
        <span>cards, then discard</span>
        <strong class="text-pink-500 text-base sm:text-lg">{{ effect.parameters.discard_count }}</strong>
        <span>card(s) tagged</span>
        <span 
          class="text-[9px] sm:text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded-full border shadow-sm"
          :style="{ 
            background: getTagBadgeColors(effect.parameters.discard_filter || '').background,
            color: getTagBadgeColors(effect.parameters.discard_filter || '').color,
            borderColor: getTagBadgeColors(effect.parameters.discard_filter || '').border
          }"
        >{{ effect.parameters.discard_filter }}</span> 
        <span>from the final hand.</span>
      </div>
    </div>
  </div>
</template>
