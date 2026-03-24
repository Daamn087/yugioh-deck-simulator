<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import type { HandRecord } from '../api';
import { useSimulationStore } from '../store';

const store = useSimulationStore();

const props = withDefaults(defineProps<{
  handRecords?: HandRecord[];
  availableCards?: string[];
  isOpen: boolean;
}>(), {
  handRecords: () => [],
  availableCards: () => [],
  isOpen: false
});

const emit = defineEmits<{
  (e: 'close'): void;
}>();

// ── State ────────────────────────────────────────────────────────────────────
const selectedFilters = ref<string[]>([]);
const statusFilter = ref<'all' | 'success' | 'fail'>('all');
const showInitialHands = ref(false);
const currentPage = ref(1);
const PAGE_SIZE = 20;

// Reset to page 1 whenever filters or records change
watch([selectedFilters, statusFilter, () => props.handRecords], () => { currentPage.value = 1; }, { deep: true });

// ── Computed ─────────────────────────────────────────────────────────────────
const successCount = computed(() => props.handRecords.filter(h => h.success).length);
const brickCount   = computed(() => props.handRecords.filter(h => !h.success).length);

const filteredHands = computed(() => {
  return props.handRecords.filter(record => {
    // 1. Status Filter
    if (statusFilter.value === 'success' && !record.success) return false;
    if (statusFilter.value === 'fail' && record.success) return false;
    
    // 2. Card Filters
    if (selectedFilters.value.length > 0) {
      if (!selectedFilters.value.every(card => record.final_hand.includes(card))) return false;
    }
    
    return true;
  });
});

const totalPages = computed(() => Math.max(1, Math.ceil(filteredHands.value.length / PAGE_SIZE)));

const pagedHands = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE;
  return filteredHands.value.slice(start, start + PAGE_SIZE);
});

// Cards not yet selected, to avoid duplicates in filter dropdowns
const availableForFilter = computed(() => [...new Set(props.availableCards)]);

// Assign a stable color per unique card name for the hand chips
const cardColors = computed(() => {
  const palette = [
    '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b',
    '#10b981', '#ef4444', '#06b6d4', '#a78bfa',
    '#f97316', '#14b8a6',
  ];
  const map: Record<string, string> = {};
  props.availableCards.forEach((card, i) => {
    map[card] = palette[i % palette.length] ?? '#555';
  });
  // Fallback for cards not in availableCards (e.g. _Generic_)
  map['_Generic_'] = '#555';
  return map;
});

function colorForCard(card: string): string {
  return cardColors.value[card] ?? '#555';
}

function imageForCard(card: string): string | null {
  return store.imageMap[card] || null;
}

// ── Actions ──────────────────────────────────────────────────────────────────
function addFilter() {
  const next = availableForFilter.value[0];
  if (next) selectedFilters.value.push(next);
}

function removeFilter(idx: number) {
  selectedFilters.value.splice(idx, 1);
}

function clearFilters() {
  selectedFilters.value = [];
  statusFilter.value = 'all';
}

function prevPage() { if (currentPage.value > 1) currentPage.value--; }
function nextPage() { if (currentPage.value < totalPages.value) currentPage.value++; }

function close() {
  emit('close');
}

// Close on escape key
const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && props.isOpen) close();
};

onMounted(() => window.addEventListener('keydown', handleKeydown));
onUnmounted(() => window.removeEventListener('keydown', handleKeydown));
</script>

<template>
  <Teleport defer to="body">
    <Transition name="fade">
      <!-- Backdrop -->
      <div v-if="isOpen && handRecords.length > 0" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 lg:p-12 bg-black/80 backdrop-blur-sm" @click.self="close">
        
        <!-- Modal Dialog -->
        <div class="card p-0 overflow-hidden w-full max-w-6xl max-h-full h-full flex flex-col shadow-2xl border-white/10" role="dialog" aria-modal="true">
          
          <!-- ── Header ───────────────────────────────────────────────── -->
          <div class="flex items-center justify-between px-6 py-5 bg-surface-card border-b border-border-primary">
            <div class="flex items-center gap-4">
              <span class="text-2xl">🔍</span>
              <h2 class="font-bold text-white text-lg tracking-wide">Test Hand Inspector</h2>
              <span class="hidden sm:inline-block text-xs text-text-secondary bg-white/5 px-3 py-1 rounded-full border border-white/10">
                {{ handRecords.length.toLocaleString() }} recorded details
              </span>
            </div>

            <div class="flex items-center gap-6">
              <div class="hidden sm:flex gap-4 text-sm font-semibold selection-none">
                <span class="text-emerald-400">✅ {{ successCount.toLocaleString() }}</span>
                <span class="text-red-400">❌ {{ brickCount.toLocaleString() }}</span>
              </div>
              <button
                @click="close"
                class="text-text-secondary hover:text-white p-2 hover:bg-white/10 rounded-full transition-colors leading-none"
                title="Close"
              >✕</button>
            </div>
          </div>

          <!-- ── Body ─────────────────────────────────────────────── -->
          <div class="flex flex-col flex-1 overflow-hidden bg-bg-dark">

        <!-- Filter bar -->
        <div class="px-5 py-4 flex flex-wrap items-center gap-2 bg-white/[0.02] border-b border-border-primary">
          <!-- Status Filter -->
          <div class="flex items-center gap-2 border-r border-[#444] pr-4 mr-2">
            <span class="text-xs font-bold uppercase tracking-wider text-text-secondary">Status:</span>
            <select
              v-model="statusFilter"
              class="text-xs font-semibold bg-[#2a2a2a] border border-[#444] rounded px-2 py-1 text-white focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer w-[110px]"
            >
              <option value="all">All Hands</option>
              <option value="success">✅ Success</option>
              <option value="fail">❌ Fail</option>
            </select>
          </div>

          <!-- Card Filters -->
          <span class="text-xs font-bold uppercase tracking-wider text-text-secondary mr-1">Cards:</span>

          <div
            v-for="(filter, idx) in selectedFilters"
            :key="idx"
            class="flex items-center gap-1 bg-primary/10 border border-primary/30 rounded-lg px-1 py-0.5"
          >
            <select
              :value="filter"
              @change="e => selectedFilters[idx] = (e.target as HTMLSelectElement).value"
              class="text-xs bg-transparent border-none text-white focus:outline-none focus:ring-0 py-0 px-1 cursor-pointer min-w-[120px]"
            >
              <option
                v-for="card in availableForFilter"
                :key="card"
                :value="card"
              >{{ card }}</option>
            </select>
            <button
              @click="removeFilter(idx)"
              class="text-red-400 hover:text-red-300 text-xs leading-none px-0.5 py-0 bg-transparent border-none"
              title="Remove filter"
            >✕</button>
          </div>

          <button
            v-if="availableForFilter.length > 0"
            @click="addFilter"
            class="text-xs text-primary border border-primary/30 bg-primary/5 hover:bg-primary/15 px-3 py-1.5 rounded-lg transition-colors font-semibold"
          >+ Add card</button>

          <div class="ml-auto flex items-center gap-4">
            <label class="flex items-center gap-2 text-xs font-semibold text-text-secondary cursor-pointer hover:text-white transition-colors">
              <input type="checkbox" v-model="showInitialHands" class="rounded border-white/20 bg-black/30 text-primary accent-primary w-4 h-4 cursor-pointer" />
              Show pre-effect hands
            </label>

            <button
              v-if="selectedFilters.length > 0 || statusFilter !== 'all'"
              @click="clearFilters"
              class="text-xs text-text-secondary hover:text-white border border-white/10 bg-white/5 px-3 py-1.5 rounded-lg transition-colors font-semibold"
            >Clear all</button>
          </div>
        </div>

        <!-- Summary + pagination -->
        <div class="px-5 py-3 flex items-center justify-between bg-white/[0.01]">
          <span class="text-xs text-text-secondary">
            Showing <span class="text-white font-semibold">{{ filteredHands.length.toLocaleString() }}</span>
            of <span class="font-semibold">{{ handRecords.length.toLocaleString() }}</span> hands
            <span v-if="handRecords.length >= 10_000" class="text-yellow-500/80 ml-1">(capped at 10 000)</span>
          </span>
          <div class="flex items-center gap-2">
            <button
              @click="prevPage"
              :disabled="currentPage === 1"
              class="px-2 py-1 text-xs rounded bg-white/5 hover:bg-white/10 disabled:opacity-30 transition-colors border border-white/10"
            >◀</button>
            <span class="text-xs text-text-secondary">{{ currentPage }} / {{ totalPages }}</span>
            <button
              @click="nextPage"
              :disabled="currentPage === totalPages"
              class="px-2 py-1 text-xs rounded bg-white/5 hover:bg-white/10 disabled:opacity-30 transition-colors border border-white/10"
            >▶</button>
          </div>
        </div>

        <!-- Hand list -->
        <div v-if="filteredHands.length === 0" class="flex-1 px-6 py-16 flex flex-col items-center justify-center text-text-secondary">
          <span class="text-4xl mb-3 opacity-50">📭</span>
          <p class="text-lg font-medium">No hands match the selected filters.</p>
          <p class="text-sm opacity-70">Try removing some card requirements.</p>
        </div>

        <ul v-else class="flex-1 overflow-y-auto divide-y divide-border-primary/60">
          <li
            v-for="(record, idx) in pagedHands"
            :key="idx"
            class="px-6 py-4 flex items-center gap-4 hover:bg-white/[0.03] transition-colors"
          >
            <!-- Result badge -->
            <div
              class="shrink-0 flex items-center justify-center w-8 h-8 rounded-full border"
              :class="record.success ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-red-500/10 border-red-500/30'"
              :title="record.success ? 'Success' : 'Brick'"
            >
              <span class="text-sm">{{ record.success ? '✅' : '❌' }}</span>
            </div>

            <!-- Card chips/Images -->
            <div class="flex flex-col gap-2 flex-1 min-w-0">
              <div class="flex flex-wrap gap-2">
                <template v-for="(card, ci) in record.final_hand" :key="ci">
                  <!-- Image thumbnail -->
                  <div 
                    v-if="imageForCard(card)"
                    class="relative group/card"
                    :title="card"
                  >
                    <img 
                      :src="imageForCard(card)!" 
                      :alt="card"
                      class="h-[130px] w-auto rounded border border-white/20 shadow-sm bg-black/40"
                      :class="selectedFilters.includes(card) ? 'ring-2 ring-white/80 drop-shadow-[0_0_8px_rgba(255,255,255,0.4)]' : ''"
                    />
                  </div>
                  <!-- Fallback Name Chip -->
                  <span
                    v-else
                    class="text-sm px-3 py-1.5 rounded-full font-semibold truncate max-w-[300px] border border-white/10 shadow-sm"
                    :class="selectedFilters.includes(card) ? 'ring-2 ring-white/60 drop-shadow-md' : ''"
                    :style="{ backgroundColor: colorForCard(card) + '33', color: colorForCard(card) }"
                    :title="card"
                  >{{ card }}</span>
                </template>
              </div>
              
              <!-- Initial Hand (pre-effects) if different -->
              <div 
                v-if="showInitialHands && record.initial_hand.join(',') !== record.final_hand.join(',')" 
                class="flex flex-wrap gap-1.5 items-center mt-0.5 pl-3 border-l-2 border-white/10"
              >
                <span class="text-[11px] uppercase tracking-wider text-text-secondary font-bold mr-1">Initial Draw:</span>
                <template v-for="(card, ci) in record.initial_hand" :key="'init-'+ci">
                  <img 
                    v-if="imageForCard(card)"
                    :src="imageForCard(card)!" 
                    :alt="card"
                    class="h-10 w-auto rounded border border-white/10 opacity-70 grayscale-[0.3]"
                    :title="card"
                  />
                  <span
                    v-else
                    class="text-xs px-2 py-1 rounded-full font-medium truncate max-w-[160px] border border-white/5 opacity-70"
                    :style="{ backgroundColor: colorForCard(card) + '22', color: colorForCard(card) }"
                    :title="card"
                  >{{ card }}</span>
                </template>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
  </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-active .card,
.fade-leave-active .card {
  transition: transform 0.2s cubic-bezier(0.18, 0.89, 0.32, 1.28);
}

.fade-enter-from .card,
.fade-leave-to .card {
  transform: scale(0.95) translateY(10px);
}

select option {
  background: #1e1e1e;
  color: white;
}
</style>
