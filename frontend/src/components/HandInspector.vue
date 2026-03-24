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
      // Count required copies from filters
      const filterCounts: Record<string, number> = {};
      for (const card of selectedFilters.value) {
        filterCounts[card] = (filterCounts[card] || 0) + 1;
      }

      // Count copies in the initial hand
      const handCounts: Record<string, number> = {};
      for (const card of record.initial_hand) {
        handCounts[card] = (handCounts[card] || 0) + 1;
      }

      // Ensure hand has at least the required amount of each filtered card
      for (const [card, requiredCount] of Object.entries(filterCounts)) {
        if ((handCounts[card] || 0) < requiredCount) return false;
      }
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
    '#60a5fa', '#a78bfa', '#f472b6', '#fbbf24',
    '#34d399', '#f87171', '#22d3ee', '#c084fc',
    '#fb923c', '#2dd4bf',
  ];
  const map: Record<string, string> = {};
  props.availableCards.forEach((card, i) => {
    map[card] = palette[i % palette.length] ?? '#555';
  });
  // Fallback for cards not in availableCards (e.g. Blank)
  map['Blank'] = '#555';
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
          <div class="flex items-center justify-between px-6 py-5 bg-surface-card border-b border-white/10 shadow-lg">
            <div class="flex items-center gap-4">
              <span class="text-2xl drop-shadow-md">🔍</span>
              <h2 class="font-bold text-white text-xl tracking-tight">Hand Inspector</h2>
              <span class="hidden sm:inline-block text-[10px] font-black uppercase tracking-widest text-white/40 bg-white/5 px-3 py-1.5 rounded-full border border-white/10 shadow-inner">
                {{ handRecords.length.toLocaleString() }} SAMPLES
              </span>
            </div>

            <div class="flex items-center gap-6">
              <div class="hidden sm:flex gap-6 text-sm font-bold selection-none">
                <span class="flex items-center gap-2 text-emerald-400 drop-shadow-[0_0_8px_rgba(52,211,153,0.3)]">
                  <span class="text-xs">✅</span> {{ successCount.toLocaleString() }}
                </span>
                <span class="flex items-center gap-2 text-red-400 drop-shadow-[0_0_8px_rgba(248,113,113,0.3)]">
                  <span class="text-xs">❌</span> {{ brickCount.toLocaleString() }}
                </span>
              </div>
              <div class="h-6 w-px bg-white/10 mx-1"></div>
              <button
                @click="close"
                class="text-white/50 hover:text-white p-2.5 hover:bg-white/10 rounded-xl transition-all leading-none border border-transparent hover:border-white/10 active:scale-95"
                title="Close"
              >✕</button>
            </div>
          </div>

          <!-- ── Body ─────────────────────────────────────────────── -->
          <div class="flex flex-col flex-1 overflow-hidden bg-bg-dark">

        <!-- Filter bar -->
        <div class="px-6 py-2.5 flex flex-wrap items-center gap-3 bg-white/[0.03] border-b border-white/5 shadow-sm">
          <!-- Status Filter -->
          <div class="flex items-center gap-3 pr-4 border-r border-white/10">
            <span class="text-[10px] font-black uppercase tracking-widest text-white/50">Status</span>
            <select
              v-model="statusFilter"
              class="text-[10px] font-bold bg-[#2a2a2a] border border-white/10 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:ring-2 focus:ring-primary/50 cursor-pointer w-[105px] shadow-sm hover:border-white/20 transition-all"
            >
              <option value="all">All Hands</option>
              <option value="success">✅ Success</option>
              <option value="fail">❌ Fail</option>
            </select>
          </div>

          <!-- Card Filters -->
          <div class="flex items-center gap-3">
            <span class="text-[10px] font-black uppercase tracking-widest text-white/50">Card Filters</span>

            <div
              v-for="(filter, idx) in selectedFilters"
              :key="idx"
              class="flex items-center gap-1 bg-primary/10 border border-primary/20 rounded-full pl-3 pr-1 py-0.5 shadow-sm animate-in fade-in zoom-in duration-200"
            >
              <select
                :value="filter"
                @change="e => selectedFilters[idx] = (e.target as HTMLSelectElement).value"
                class="text-[10px] font-black uppercase tracking-tight bg-transparent border-none text-white focus:outline-none focus:ring-0 py-0 px-0 cursor-pointer min-w-[100px]"
              >
                <option
                  v-for="card in availableForFilter"
                  :key="card"
                  :value="card"
                >{{ card }}</option>
              </select>
              <button
                @click="removeFilter(idx)"
                class="w-5 h-5 flex items-center justify-center hover:bg-white/10 rounded-full transition-all ml-1 text-white/40 hover:text-red-400"
                title="Remove filter"
              >
                <span class="text-[10px] leading-none pb-[2px]">✕</span>
              </button>
            </div>

            <button
              v-if="availableForFilter.length > 0"
              @click="addFilter"
              class="text-[10px] text-primary border border-primary/30 bg-primary/10 hover:bg-primary/20 px-3 py-1.5 rounded-full transition-all font-bold shadow-sm active:scale-95"
            >+ Add Condition</button>
          </div>

          <div class="ml-auto flex items-center gap-6">
            <label class="flex items-center gap-2.5 text-xs font-bold text-white/50 cursor-pointer hover:text-white transition-all group">
              <div class="relative flex items-center justify-center">
                <input type="checkbox" v-model="showInitialHands" class="peer appearance-none w-5 h-5 rounded-md border-2 border-white/20 bg-black/40 checked:bg-primary checked:border-primary transition-all cursor-pointer" />
                <span class="absolute text-[10px] text-black font-black opacity-0 peer-checked:opacity-100 transition-opacity">✓</span>
              </div>
              <span class="group-hover:translate-x-0.5 transition-transform uppercase tracking-wider text-[10px]">Show Effect Flow</span>
            </label>

            <button
              v-if="selectedFilters.length > 0 || statusFilter !== 'all'"
              @click="clearFilters"
              class="text-[10px] text-white/70 hover:text-white border border-white/10 bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-full transition-all font-bold shadow-sm active:scale-95"
            >Clear All</button>
          </div>
        </div>

        <!-- Summary + pagination -->
        <div class="px-6 py-3 flex items-center justify-between bg-black/20 border-b border-white/5">
          <span class="text-[10px] font-bold uppercase tracking-widest text-white/40">
            Showing <span class="text-white">{{ filteredHands.length.toLocaleString() }}</span>
            of <span class="text-white">{{ handRecords.length.toLocaleString() }}</span> samples
            <span v-if="handRecords.length >= 10_000" class="text-yellow-500/80 ml-1">(capped at 10 000)</span>
          </span>
          <div class="flex items-center gap-3">
            <button
              @click="prevPage"
              :disabled="currentPage === 1"
              class="w-8 h-8 flex items-center justify-center rounded-lg bg-white/5 hover:bg-white/10 disabled:opacity-20 transition-all border border-white/10 active:scale-90"
            >◀</button>
            <span class="text-[10px] font-black text-white/60 min-w-[60px] text-center">{{ currentPage }} / {{ totalPages }}</span>
            <button
              @click="nextPage"
              :disabled="currentPage === totalPages"
              class="w-8 h-8 flex items-center justify-center rounded-lg bg-white/5 hover:bg-white/10 disabled:opacity-20 transition-all border border-white/10 active:scale-90"
            >▶</button>
          </div>
        </div>

        <!-- Hand list -->
        <div v-if="filteredHands.length === 0" class="flex-1 px-8 py-20 flex flex-col items-center justify-center text-center">
          <div class="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-6 border border-white/10 shadow-inner">
            <span class="text-5xl drop-shadow-lg">📭</span>
          </div>
          <p class="text-xl font-black text-white mb-2 uppercase tracking-tight">No Matching Hands</p>
          <p class="text-sm text-white/50 max-w-xs leading-relaxed font-medium">
            Your current filters are too restrictive. Try removing some card requirements or changing the status filter.
          </p>
        </div>

        <ul v-else class="flex-1 overflow-y-auto divide-y divide-white/5">
          <li
            v-for="(record, idx) in pagedHands"
            :key="idx"
            class="px-6 py-5 flex items-center gap-6 transition-all duration-200 border-l-4"
            :class="[
              record.success 
                ? 'bg-emerald-500/[0.02] hover:bg-emerald-500/[0.05] border-l-emerald-500/50' 
                : 'bg-red-500/[0.02] hover:bg-red-500/[0.05] border-l-red-500/50'
            ]"
          >
            <!-- Result badge -->
            <div
              class="shrink-0 flex items-center justify-center w-10 h-10 rounded-xl border shadow-sm"
              :class="record.success 
                ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300' 
                : 'bg-red-500/20 border-red-500/40 text-red-300'"
              :title="record.success ? 'Success' : 'Brick'"
            >
              <span class="text-lg font-bold">{{ record.success ? '✓' : '✕' }}</span>
            </div>

            <!-- Card chips/Images -->
            <div class="flex flex-col gap-3 flex-1 min-w-0">
              <div class="flex flex-wrap gap-2.5">
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
                      class="h-[140px] w-auto rounded-lg border border-white/20 shadow-md bg-black/40 transition-all group-hover/card:scale-105 group-hover/card:z-10 group-hover/card:border-white/40"
                      :class="selectedFilters.includes(card) ? 'ring-2 ring-primary scale-105 z-10 border-primary/50' : ''"
                    />
                  </div>
                  <!-- Fallback Name Chip -->
                  <span
                    v-else
                    class="text-xs px-3.5 py-2 rounded-lg font-bold truncate max-w-[280px] border shadow-sm transition-colors h-fit"
                    :class="selectedFilters.includes(card) ? 'ring-2 ring-primary border-primary/50' : 'border-white/10'"
                    :style="{ 
                      backgroundColor: colorForCard(card) + '15', 
                      color: colorForCard(card),
                      borderColor: colorForCard(card) + '30'
                    }"
                    :title="card"
                  >{{ card }}</span>
                </template>
              </div>

              
              <!-- Effect Flow: only shown when effects actually resolved -->
              <div 
                v-if="showInitialHands && (record.cards_drawn.length > 0 || record.cards_discarded.length > 0)" 
                class="flex flex-col gap-4 mt-2 p-5 rounded-2xl bg-black/20 border border-white/5 shadow-inner"
              >
                <!-- Initial hand (before effects) -->
                <div class="flex items-center gap-4">
                  <span class="text-[10px] uppercase tracking-[0.15em] text-white/40 font-black w-24">Initial Hand</span>
                  <div class="flex flex-wrap gap-2">
                    <template v-for="(card, ci) in record.initial_hand" :key="'init-'+ci">
                      <img v-if="imageForCard(card)" :src="imageForCard(card)!" class="h-12 w-auto rounded border border-white/15 opacity-60 grayscale-[0.5] hover:opacity-100 hover:grayscale-0 transition-all" :title="card" :alt="card" />
                      <span v-else class="text-[10px] px-2.5 py-1 rounded-md border border-white/10 opacity-60 bg-white/5 text-white/80" :title="card">{{ card }}</span>
                    </template>
                  </div>
                </div>

                <!-- Cards drawn by the effect -->
                <div v-if="record.cards_drawn.length > 0" class="flex items-center gap-4">
                  <span class="text-[10px] uppercase tracking-[0.15em] text-emerald-400 font-black w-24">Drawn</span>
                  <div class="flex flex-wrap gap-2">
                    <template v-for="(card, ci) in record.cards_drawn" :key="'drawn-'+ci">
                      <img v-if="imageForCard(card)" :src="imageForCard(card)!" class="h-12 w-auto rounded border-2 border-emerald-500/40 shadow-lg shadow-emerald-500/10" :title="card" :alt="card" />
                      <span v-else class="text-[10px] px-2.5 py-1 rounded-md border border-emerald-500/30 bg-emerald-500/15 text-emerald-300 font-bold shadow-sm shadow-emerald-500/5">{{ card }}</span>
                    </template>
                  </div>
                </div>

                <!-- Cards discarded by the effect -->
                <div v-if="record.cards_discarded.length > 0" class="flex items-center gap-4">
                  <span class="text-[10px] uppercase tracking-[0.15em] text-red-400 font-black w-24">Discarded</span>
                  <div class="flex flex-wrap gap-2">
                    <template v-for="(card, ci) in record.cards_discarded" :key="'disc-'+ci">
                      <img v-if="imageForCard(card)" :src="imageForCard(card)!" class="h-12 w-auto rounded border border-red-500/20 grayscale opacity-30 shadow-sm" :title="card" :alt="card" />
                      <span v-else class="text-[10px] px-2.5 py-1 rounded-md border border-red-500/20 bg-red-500/10 text-red-400/70 font-medium" :title="card">{{ card }}</span>
                    </template>
                  </div>
                </div>
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
