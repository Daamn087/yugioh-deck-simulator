<script setup lang="ts">
import type { SimulationResult } from '../api';

defineProps<{
  result: SimulationResult | null;
  loading: boolean;
}>();
</script>

<template>
  <div class="card p-6 text-center">
    <h2 class="text-xl font-bold text-white mb-6">Simulation Results</h2>
    
    <div v-if="loading" class="py-12 flex flex-col items-center gap-4">
      <div class="w-10 h-10 border-4 border-primary/30 border-t-primary rounded-full animate-spin"></div>
      <span class="text-text-secondary font-medium italic animate-pulse">Simulating...</span>
    </div>
    
    <div v-else-if="result" class="animate-in fade-in zoom-in duration-500">
      <div class="mb-6">
        <div class="text-6xl font-black bg-gradient-to-br from-[#00ff88] to-primary bg-clip-text text-transparent drop-shadow-[0_0_15px_rgba(0,255,136,0.3)]">
          {{ result.success_rate.toFixed(2) }}%
        </div>
        <div class="text-xs font-bold text-text-secondary uppercase tracking-[0.3em] mt-2">Success Rate</div>
      </div>
      
      <div class="w-full bg-white/10 h-3 rounded-full overflow-hidden mb-8 p-0.5 shadow-inner">
        <div 
            class="h-full bg-gradient-to-r from-[#00ff88] to-primary rounded-full shadow-[0_0_12px_rgba(0,255,136,0.6)] transition-all duration-1000 ease-out" 
            :style="{ width: (result.success_rate || 0) + '%' }"
        ></div>
      </div>

      <div class="grid grid-cols-3 gap-4 py-6 border-t border-border-primary">
        <div class="flex flex-col">
          <span class="text-lg font-bold text-white">{{ result.success_count.toLocaleString() }}</span>
          <span class="text-[10px] uppercase font-black tracking-widest text-text-secondary">Successes</span>
        </div>
        <div class="flex flex-col">
            <span class="text-lg font-bold text-red-500">{{ result.brick_rate.toFixed(2) }}%</span>
            <span class="text-[10px] uppercase font-black tracking-widest text-text-secondary">Brick Rate</span>
        </div>
        <div class="flex flex-col">
            <span class="text-lg font-bold text-blue-400">{{ result.time_taken.toFixed(3) }}s</span>
            <span class="text-[10px] uppercase font-black tracking-widest text-text-secondary">Time Taken</span>
        </div>
      </div>

      <!-- Warnings -->
      <div v-if="result.warnings && result.warnings.length > 0" class="mt-6 pt-6 border-t border-border-primary flex flex-col gap-2">
        <div v-for="(warning, idx) in result.warnings" :key="idx" class="bg-yellow-500/10 text-yellow-500 p-3 rounded-lg text-xs font-semibold text-left border border-yellow-500/20 shadow-inner flex items-start gap-2">
          <span>⚠️</span>
          <span>{{ warning }}</span>
        </div>
      </div>
    </div>
    
    <div v-else class="py-12 border-2 border-dashed border-white/5 rounded-xl">
      <p class="text-text-secondary/50 italic font-medium">
        Run simulation to see results.
      </p>
    </div>
  </div>
</template>

<style scoped>
/* Scoped styles removed in favor of Tailwind CSS */
</style>
