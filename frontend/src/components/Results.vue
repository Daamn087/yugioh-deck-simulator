
<script setup lang="ts">
import type { SimulationResult } from '../api';

defineProps<{
  result: SimulationResult | null;
  loading: boolean;
}>();
</script>

<template>
  <div class="results-panel card">
    <h2>Simulation Results</h2>
    
    <div v-if="loading" class="loading">
      Simulating...
    </div>
    
    <div v-else-if="result" class="result-content">
      <div class="main-stat">
        <div class="percentage success">{{ result.success_rate.toFixed(2) }}%</div>
        <div class="label">Success Rate</div>
      </div>
      
      <div class="progress-bar-bg">
        <div 
            class="progress-bar-fill" 
            :style="{ width: result.success_rate + '%' }"
        ></div>
      </div>

      <div class="details">
        <div class="detail-item">
          <span class="val">{{ result.success_count.toLocaleString() }}</span>
          <span class="lbl">Successes</span>
        </div>
        <div class="detail-item">
            <span class="val brick">{{ result.brick_rate.toFixed(2) }}%</span>
            <span class="lbl">Brick Rate</span>
        </div>
        <div class="detail-item">
            <span class="val">{{ result.time_taken.toFixed(3) }}s</span>
            <span class="lbl">Time Taken</span>
        </div>
      </div>
    </div>
    
    <div v-else class="placeholder">
      Run simulation to see results.
    </div>
  </div>
</template>

<style scoped>
.results-panel {
    padding: 1.5rem;
    background: var(--surface-card);
    border-radius: 8px;
    border: 1px solid var(--border-color);
    text-align: center;
}

.main-stat {
    margin: 1rem 0;
}

.percentage {
    font-size: 3rem;
    font-weight: 800;
    line-height: 1;
}

.percentage.success {
    background: linear-gradient(45deg, #00ff88, #00b8ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.progress-bar-bg {
    background: rgba(255, 255, 255, 0.1);
    height: 10px;
    border-radius: 5px;
    overflow: hidden;
    margin: 1.5rem 0;
}

.progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #00ff88, #00b8ff);
    box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
}

.details {
    display: flex;
    justify-content: space-around;
    padding-top: 1rem;
    border-top: 1px solid var(--border-color);
}

.detail-item {
    display: flex;
    flex-direction: column;
}

.val {
    font-size: 1.2rem;
    font-weight: bold;
}

.val.brick {
    color: #ff4444;
}

.lbl {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.loading {
    font-size: 1.2rem;
    color: var(--text-secondary);
    padding: 2rem;
}

.placeholder {
    color: var(--text-secondary);
    font-style: italic;
    padding: 2rem;
}
</style>
