<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const activeSection = ref('introduction');

const sections = [
  { id: 'introduction', title: 'Introduction' },
  { id: 'how-to-use', title: 'How to Use' },
  { id: 'success-conditions', title: 'Success Conditions' },
  { id: 'card-effects', title: 'Card Effects' },
  { id: 'hand-inspector', title: 'Hand Inspector' },
  { id: 'faq', title: 'FAQ' },
  { id: 'contact', title: 'Contact' },
];

const scrollTo = (id: string) => {
  activeSection.value = id;
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' });
  }
};

// Handle hash navigation on mount
onMounted(() => {
  if (route.hash) {
    const targetId = route.hash.substring(1); // Remove the '#'
    setTimeout(() => {
      const el = document.getElementById(targetId);
      if (el) {
        // Scroll the element into view within its scrollable container
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        // Update active section if it's a main section
        const section = sections.find(s => s.id === targetId);
        if (section) {
          activeSection.value = targetId;
        } else if (targetId.startsWith('faq-')) {
          activeSection.value = 'faq';
        }
      }
    }, 100); // Small delay to ensure DOM is ready
  }
});
</script>

<template>
  <div class="max-w-5xl mx-auto rounded-3xl overflow-hidden border border-white/5 shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-700">
    <!-- Header -->
    <div class="px-10 py-12 bg-[#0a0a0a] border-b border-white/5 relative overflow-hidden">
      <div class="absolute -top-20 -right-20 w-64 h-64 bg-primary/10 blur-[100px] rounded-full"></div>
      <div class="relative z-10 flex flex-col md:flex-row justify-between items-end gap-6">
        <div>
          <p class="text-sm font-black uppercase tracking-[0.3em] text-primary mb-3">Documentation & resources</p>
          <h1 class="text-4xl font-black tracking-tighter text-white">
            KNOWLEDGE BASE
          </h1>
        </div>
        <router-link 
          to="/"
          class="flex items-center gap-2 px-5 py-2.5 bg-white/5 hover:bg-white/10 rounded-full text-[10px] font-black uppercase tracking-widest text-white transition-all border border-white/10 hover:border-primary/50"
        >
          <span>←</span> Back to Simulator
        </router-link>
      </div>
    </div>

    <div class="flex flex-col md:flex-row min-h-[700px] bg-[#0c0c0c]">
      <!-- Sidebar Navigation -->
      <nav class="w-full md:w-72 border-r border-white/5 p-6 shrink-0 bg-[#0d0d0d]/50">
        <div class="sticky top-10 flex flex-col gap-2">
          <p class="px-4 text-sm font-black uppercase tracking-[0.2em] text-white/30 mb-2">Sections</p>
          <button 
            v-for="section in sections" 
            :key="section.id"
            @click="scrollTo(section.id)"
            class="text-left px-4 py-3 rounded-xl text-xs font-bold transition-all flex items-center justify-between group"
            :class="activeSection === section.id 
              ? 'bg-primary/10 text-primary border border-primary/20 shadow-[0_0_20px_rgba(var(--color-primary),0.05)]' 
              : 'text-white/40 hover:text-white hover:bg-white/5'"
          >
            {{ section.title }}
            <span v-if="activeSection === section.id" class="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(var(--color-primary),1)]"></span>
            <span v-else class="opacity-0 group-hover:opacity-100 transition-opacity">→</span>
          </button>
        </div>
      </nav>

      <!-- Content Area -->
      <div class="flex-1 p-10 overflow-y-auto max-h-[900px] scroll-smooth custom-scrollbar bg-gradient-to-b from-transparent to-black/20">
        <div class="space-y-20">
          
          <!-- Introduction -->
          <section id="introduction" class="scroll-mt-10">
            <div class="flex items-center gap-4 mb-6">
              <span class="text-sm font-black text-primary bg-primary/10 px-2 py-1 rounded border border-primary/20">01</span>
              <h3 class="text-xl font-black tracking-tight text-white uppercase">Introduction</h3>
            </div>
            <div class="prose prose-invert max-w-none text-white/60 leading-relaxed space-y-4">
              <p class="text-lg text-white/80 font-medium">
                The Yu-Gi-Oh! Deck Simulator is a high-performance analytical tool designed to quantify deck consistency through simulation.
              </p>
              <p>
                Unlike static calculators that rely on simplified hypergeometric distribution, this tool employs <strong>Monte Carlo Simulation</strong>. This allows us to account for complex card interactions, varying draw counts, and conditional requirements that mathematical formulas struggle to capture.
              </p>
              <div class="bg-white/5 border border-white/10 p-6 rounded-2xl relative overflow-hidden group">
                <div class="absolute top-0 left-0 w-1 h-full bg-primary/40 group-hover:bg-primary transition-colors"></div>
                <p class="text-xs italic text-white/70 leading-relaxed">
                  "Simulation bridges the gap between theory and actual play. It accounts for every 'Pot of Desires', every 'Upstart Goblin', and every conditional search, providing a realistic consistency percentage based on millions of virtual trials."
                </p>
              </div>
            </div>
          </section>

          <!-- How to Use -->
          <section id="how-to-use" class="scroll-mt-10">
            <div class="flex items-center gap-4 mb-8">
              <span class="text-[10px] font-black text-primary bg-primary/10 px-2 py-1 rounded border border-primary/20">02</span>
              <h3 class="text-xl font-black tracking-tight text-white uppercase">How to Use</h3>
            </div>
            <div class="grid gap-4">
              <div v-for="(step, i) in [
                { t: 'Build Deck', d: 'Enter card names or tags and their counts, or import YDK files directly.' },
                { t: 'Define Rules', d: 'Set up success conditions using AND/OR logic (e.g., Starter >= 1).' },
                { t: 'Add Effects', d: 'Configure cards that draw or discard to simulate realistic resolution.' },
                { t: 'Simulate', d: 'Run up to millions of iterations for statistically significant results.' }
              ]" :key="i" class="flex gap-4 p-5 bg-white/5 rounded-2xl border border-white/10 hover:border-white/20 transition-all group">
                <span class="text-lg font-black text-white/20 group-hover:text-primary/40 transition-colors">0{{i+1}}</span>
                <div>
                  <h4 class="text-sm font-black text-white uppercase tracking-tighter mb-1">{{ step.t }}</h4>
                  <p class="text-xs text-white/50 leading-relaxed">{{ step.d }}</p>
                </div>
              </div>
            </div>
          </section>

          <!-- Success Conditions -->
          <section id="success-conditions" class="scroll-mt-10">
            <div class="flex items-center gap-4 mb-8">
              <span class="text-[10px] font-black text-primary bg-primary/10 px-2 py-1 rounded border border-primary/20">03</span>
              <h3 class="text-xl font-black tracking-tight text-white uppercase">Success Conditions</h3>
            </div>
            <div class="space-y-6">
              <p class="text-white/60 text-sm leading-relaxed">
                Conditions determine the quality of a hand. You can stack multiple requirements using nested logic groups.
              </p>
              
              <div class="bg-primary/5 border border-primary/20 p-5 rounded-2xl">
                <p class="text-sm font-black uppercase tracking-widest text-primary mb-2">Logic Hierarchy</p>
                <p class="text-xs text-white/70 leading-relaxed">
                  Top-level requirements are always connected with <strong>AND</strong>. Use <strong>Parentheses Groups</strong> to implement <strong>OR</strong> logic or complex nesting.
                </p>
              </div>

              <div class="bg-black p-6 rounded-2xl border border-white/5 font-mono text-xs overflow-hidden relative group">
                <div class="absolute top-4 right-4 text-sm font-black text-white/10 uppercase tracking-widest">Example Logic</div>
                <div class="space-y-1">
                  <p class="text-white/40">(Starter >= 1) <span class="text-primary font-bold">AND</span></p>
                  <p class="text-white/40">&nbsp;&nbsp;(<span class="text-white/40"> (Extender >= 1) </span> <span class="text-blue-400 font-bold">OR</span> <span class="text-white/40"> (Draw Card >= 1) </span>)</p>
                </div>
              </div>
            </div>
          </section>

          <!-- Card Effects -->
          <section id="card-effects" class="scroll-mt-10">
            <div class="flex items-center gap-4 mb-8">
              <span class="text-[10px] font-black text-primary bg-primary/10 px-2 py-1 rounded border border-primary/20">04</span>
              <h3 class="text-xl font-black tracking-tight text-white uppercase">Adding Effects</h3>
            </div>
            <div class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-white/5 p-4 rounded-xl border border-white/5">
                  <p class="text-sm font-black text-primary uppercase tracking-widest mb-1">Type A</p>
                  <p class="text-sm font-bold text-white mb-1">Draw</p>
                  <p class="text-[10px] text-white/40">Adds cards from deck to hand.</p>
                </div>
                <div class="bg-white/5 p-4 rounded-xl border border-white/5">
                  <p class="text-[10px] font-black text-primary uppercase tracking-widest mb-1">Type B</p>
                  <p class="text-sm font-bold text-white mb-1">Discard</p>
                  <p class="text-[10px] text-white/40">Removes cards from hand.</p>
                </div>
                <div class="bg-white/5 p-4 rounded-xl border border-white/5">
                  <p class="text-[10px] font-black text-primary uppercase tracking-widest mb-1">Constraint</p>
                  <p class="text-sm font-bold text-white mb-1">Once Per Turn</p>
                  <p class="text-[10px] text-white/40">Restricts trigger count per hand.</p>
                </div>
              </div>

              <div class="bg-amber-500/5 border border-amber-500/20 p-6 rounded-2xl space-y-3">
                <p class="text-sm font-black uppercase tracking-widest text-amber-500">Implementation Details</p>
                <ul class="space-y-2">
                  <li v-for="note in [
                    { t: 'Resolution', d: 'Draw effects resolve first, then conditional discards.' },
                    { t: 'Scope', d: 'Only cards in the initial hand trigger their effects.' },
                    { t: 'Revert', d: 'If an effect requirement isn\'t met, the action is reverted.' }
                  ]" :key="note.t" class="text-xs text-white/60">
                    <strong class="text-white/80">{{ note.t }}:</strong> {{ note.d }}
                  </li>
                </ul>
              </div>
            </div>
          </section>

          <!-- Hand Inspector -->
          <section id="hand-inspector" class="scroll-mt-10">
            <div class="flex items-center gap-4 mb-8">
              <span class="text-[10px] font-black text-primary bg-primary/10 px-2 py-1 rounded border border-primary/20">05</span>
              <h3 class="text-xl font-black tracking-tight text-white uppercase">Hand Inspector</h3>
            </div>
            <div class="space-y-6">
              <p class="text-white/60 text-sm leading-relaxed">
                The Hand Inspector is a powerful debugging and analytical tool that allows you to examine individual simulated hands. Its main purpose is to help you gain a deeper understanding of how the simulator calculates success and how your card effects interact in practice.
              </p>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-white/5 p-5 rounded-2xl border border-white/10 group">
                  <h4 class="text-xs font-black text-primary uppercase tracking-widest mb-3">Granular Filtering</h4>
                  <ul class="space-y-2 text-[11px] text-white/50">
                    <li><strong class="text-white/70">Status Filter:</strong> Isolate "Success" hands to study winning patterns or "Fail" hands to identify weaknesses and bricks.</li>
                    <li><strong class="text-white/70">Card Filters:</strong> Filter records to only show hands that contained specific cards in the initial 5-card opening.</li>
                  </ul>
                </div>
                <div class="bg-white/5 p-5 rounded-2xl border border-white/10 group">
                  <h4 class="text-xs font-black text-primary uppercase tracking-widest mb-3">Effect Flow Analysis</h4>
                  <ul class="space-y-2 text-[11px] text-white/50">
                    <li><strong class="text-white/70">Initial Hand:</strong> See exactly what you started with before any effects triggered.</li>
                    <li><strong class="text-white/70">Draw & Discard:</strong> The flow section highlights exactly which cards were drawn from the deck and which were discarded during simulation.</li>
                  </ul>
                </div>
              </div>

              <div class="bg-primary/5 border border-primary/20 p-5 rounded-2xl flex items-start gap-4">
                <span class="text-xl">💡</span>
                <p class="text-xs text-white/70 leading-relaxed">
                  <strong>Pro Tip:</strong> Use the Hand Inspector when you're seeing unexpected consistency results. Reviewing 10-20 "Fail" hands often reveals missing success conditions or incorrectly configured card effects.
                </p>
              </div>
            </div>
          </section>

          <!-- FAQ -->
          <section id="faq" class="scroll-mt-10">
            <div class="flex items-center gap-4 mb-8">
              <span class="text-[10px] font-black text-primary bg-primary/10 px-2 py-1 rounded border border-primary/20">06</span>
              <h3 class="text-xl font-black tracking-tight text-white uppercase">FAQ</h3>
            </div>
            <div class="grid gap-3">
              <div v-for="(q, i) in faqs" :key="i" :id="`faq-${i}`" class="group bg-white/5 rounded-2xl p-6 border border-white/5 hover:border-primary/20 transition-all hover:bg-white/[0.07] scroll-mt-10">
                <p class="text-sm font-black uppercase tracking-widest text-primary/50 mb-3">Question 0{{i+1}}</p>
                <h4 class="text-white font-bold mb-3 flex justify-between items-start gap-4">
                  {{ q.question }}
                </h4>
                <div class="h-px w-8 bg-white/10 mb-4 group-hover:w-full transition-all duration-500"></div>
                <p class="text-white/50 text-xs leading-relaxed">
                  {{ q.answer }}
                </p>
              </div>
            </div>
          </section>

          <!-- Contact -->
          <section id="contact" class="scroll-mt-10 pb-10">
            <div class="flex items-center gap-4 mb-8">
              <span class="text-[10px] font-black text-primary bg-primary/10 px-2 py-1 rounded border border-primary/20">07</span>
              <h3 class="text-xl font-black tracking-tight text-white uppercase">Contact</h3>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <a v-for="c in [
                { icon: '📧', label: 'Email', value: 'philgastberger@gmail.com', href: 'mailto:philgastberger@gmail.com' },
                { icon: '💬', label: 'Discord', value: 'daamn_it' },
                { icon: '🎮', label: 'DuelingBook', value: 'Daamn' },
                { icon: '📸', label: 'Instagram', value: '@phillicheese_', href: 'https://instagram.com/phillicheese_' }
              ]" :key="c.label" :href="c.href" :target="c.href ? '_blank' : undefined" class="flex items-center gap-4 p-5 bg-white/5 rounded-2xl hover:bg-white/10 transition-all border border-white/5 hover:border-white/20 group">
                <span class="text-2xl grayscale group-hover:grayscale-0 transition-all">{{ c.icon }}</span>
                <div>
                  <p class="text-sm font-black uppercase tracking-widest text-white/30">{{ c.label }}</p>
                  <p class="text-xs font-bold text-white">{{ c.value }}</p>
                </div>
              </a>
            </div>
          </section>

        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
const faqs = [
  {
    question: "Why do my simulation results vary slightly each time?",
    answer: "Since it's a random simulation of millions of hands, there's a tiny margin of error (usually around 0.1%). This is normal for Monte Carlo simulations."
  },
  {
    question: "What's the maximum deck size?",
    answer: "You can set any deck size you want, but typical Yu-Gi-Oh decks are 40-60 cards. The simulator handles any amount."
  },
  {
    question: "How do I import my deck from DuelingBook?",
    answer: "On DuelingBook, go to your deck and click 'Export Deck', then select 'YDK File'. This will download a .ydk file to your computer. You can then upload that file using the Import button in the Deck Builder."
  },
  {
    question: "Can I simulate multiple different kinds of draw effects?",
    answer: "Yes! You can add as many card effects as you like. Note that all draw effects in your opening hand resolve first, then all discard effects resolve."
  },
  {
    question: "How do I calculate logic like 'Brilliant Fusion is a starter, but ONLY if I don't draw Garnet'?",
    answer: "Since you can define success using any tags, use logic to your advantage. You can tag your Garnet as 'Garnet' and every other card in your deck as 'Not Garnet'. Then define success as: (Brilliant Fusion >= 1) AND (Not Garnet >= 4). This ensures the Fusion is only a success if the other 4 slots in your 5-card hand are not your Garnet."
  },
  {
    question: "What does 'Revert on failure' mean for effects?",
    answer: "If a card says 'Discard 1 card to draw 2', and you have no cards in hand to discard, the simulator assumes you couldn't activate the card in the first place."
  }
];
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #333;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #444;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out forwards;
}
</style>
