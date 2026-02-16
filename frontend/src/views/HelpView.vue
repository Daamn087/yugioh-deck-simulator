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
  <div class="max-w-4xl mx-auto bg-surface-card rounded-2xl border border-border-primary overflow-hidden shadow-2xl animate-fade-in">
    <!-- Header -->
    <div class="px-8 py-6 bg-gradient-to-r from-bg-dark to-surface-card border-b border-border-primary flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold bg-gradient-to-r from-primary to-blue-400 bg-clip-text text-transparent">
          Documentation & FAQ
        </h2>
        <p class="text-text-secondary text-sm mt-1">Everything you need to know about the simulator</p>
      </div>
      <router-link 
        to="/"
        class="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm font-semibold transition-all border border-border-primary hover:border-text-secondary"
      >
        <span>←</span> Back to Simulator
      </router-link>
    </div>

    <div class="flex flex-col md:flex-row min-h-[600px]">
      <!-- Sidebar Navigation -->
      <nav class="w-full md:w-64 bg-bg-dark/50 border-r border-border-primary p-4 shrink-0">
        <div class="sticky top-6 flex flex-col gap-1">
          <button 
            v-for="section in sections" 
            :key="section.id"
            @click="scrollTo(section.id)"
            class="text-left px-4 py-3 rounded-lg text-sm font-medium transition-all"
            :class="activeSection === section.id ? 'bg-primary/20 text-primary border-l-4 border-primary' : 'text-text-secondary hover:text-white hover:bg-white/5'"
          >
            {{ section.title }}
          </button>
        </div>
      </nav>

      <!-- Content Area -->
      <div class="flex-1 p-8 overflow-y-auto max-h-[800px] scroll-smooth custom-scrollbar">
        <div class="space-y-12">
          
          <!-- Introduction -->
          <section id="introduction" class="scroll-mt-8">
            <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
              <span class="text-primary">01.</span> Introduction
            </h3>
            <div class="prose prose-invert max-w-none text-text-secondary leading-relaxed space-y-4">
              <p>
                The Yu-Gi-Oh! Deck Simulator is a powerful tool designed to help players calculate the consistency of their decks. Unlike static calculators that use pure math (Hypergeometric Distribution), this tool uses <strong>Monte Carlo Simulation</strong>.
              </p>
              <div class="bg-blue-500/10 border-l-4 border-blue-500 p-4 rounded-r-lg">
                <p class="text-sm italic">
                  "Why Simulation?" - Because Yu-Gi-Oh is complex. Static math struggles when you add effects like 'Pot of Greed' or 'Draw until you have 3'. Simulation simply 'plays' thousands of hands to see what actually happens.
                </p>
              </div>
            </div>
          </section>

          <!-- How to Use -->
          <section id="how-to-use" class="scroll-mt-8">
            <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
              <span class="text-primary">02.</span> How to Use
            </h3>
            <div class="prose prose-invert max-w-none text-text-secondary leading-relaxed">
              <ol class="list-decimal list-inside space-y-3">
                <li><span class="text-white font-medium">Build your Deck:</span> Enter card names or tags (e.g., "Starter") and their counts. You can also import XML files from DuelingBook. (See FAQ section for details)</li>
                <li><span class="text-white font-medium">Define Rules:</span> Set up what counts as a "Success". For example: <code>Starter >= 1</code>.</li>
                <li><span class="text-white font-medium">Add Effects:</span> (Optional) Add cards that draw or discard during the simulation.</li>
                <li><span class="text-white font-medium">Simulate:</span> Choose the number of simulations (default is 1 million, but can be manually adjusted) and click Run!</li>
              </ol>
            </div>
          </section>

          <!-- Success Conditions -->
          <section id="success-conditions" class="scroll-mt-8">
            <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
              <span class="text-primary">03.</span> Defining Success Conditions
            </h3>
            <div class="prose prose-invert max-w-none text-text-secondary leading-relaxed space-y-4">
              <p>
                Success conditions determine if a hand is "good". You can use <strong>AND</strong> and <strong>OR</strong> logic to create complex requirements.
              </p>
              <div class="bg-blue-500/10 border-l-4 border-blue-500 p-4 rounded-r-lg mb-6">
                <p class="text-sm font-semibold text-blue-400 mb-1 italic">Logic Restriction:</p>
                <p class="text-sm text-text-secondary leading-tight">
                  Top-level requirements within a Success Option are always connected with <strong>AND</strong>. To use <strong>OR</strong>, you must place your requirements inside a <strong>Parentheses Group</strong>.
                </p>
              </div>
              <h4 class="text-white font-semibold flex items-center gap-2 mt-6">
                <span class="w-1.5 h-1.5 rounded-full bg-primary"></span> Nesting Logic:
              </h4>
              <p>
                You can nest conditions within groups. For example:
              </p>
              <div class="bg-bg-dark p-4 rounded-xl border border-border-primary font-mono text-sm">
                (Starter >= 1) <span class="text-primary">AND</span><br/>
                &nbsp;&nbsp;(<br/>
                &nbsp;&nbsp;&nbsp;&nbsp;(Extender >= 1) <span class="text-blue-400">OR</span><br/>
                &nbsp;&nbsp;&nbsp;&nbsp;(Draw Card >= 1)<br/>
                &nbsp;&nbsp;)
              </div>
              <p>
                This rule means you need at least one Starter AND (either an Extender OR a Draw Card).
              </p>
            </div>
          </section>

          <!-- Card Effects -->
          <section id="card-effects" class="scroll-mt-8">
            <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
              <span class="text-primary">04.</span> Adding Effects
            </h3>
            <div class="prose prose-invert max-w-none text-text-secondary leading-relaxed space-y-4">
              <p>
                Card effects allow the simulator to "play" consistency cards.
              </p>
              <ul class="list-disc list-inside space-y-2">
                <li><span class="text-white">Draw:</span> Adds cards from the deck to the hand.</li>
                <li><span class="text-white">Discard:</span> Removes cards from the hand.</li>
                <li><span class="text-white">Once Per Turn (OPT):</span> Ensures the effect only triggers once per hand.</li>
              </ul>
              <div class="bg-yellow-500/10 border-l-4 border-yellow-500 p-4 rounded-r-lg mt-4">
                <p class="text-sm font-semibold text-yellow-500 mb-1">Important Implementation Details:</p>
                <ul class="text-sm list-disc list-inside space-y-1">
                  <li><strong>Resolution Order:</strong> All "Draw" effects in the initial hand are resolved first, followed by "Conditional Discard" effects. Among the same type, they resolve in the order they were defined.</li>
                  <li><strong>Initial Hand Only:</strong> Only cards in the <em>starting hand</em> trigger their effects. For example, if you use 'Pot of Greed' and draw into a second 'Pot of Greed', that second one will <strong>not</strong> resolve.</li>
                  <li><strong>No Complex Priority:</strong> The simulator does not yet prioritize specific deck-thinning orders (like searching before drawing). It simply applies effects in a single pass.</li>
                  <li><strong>Revert on Failure:</strong> If an effect requires a discard but you have no matching cards, the effect reverts (simulating that it couldn't be activated).</li>
                </ul>
              </div>
            </div>
          </section>

          <!-- FAQ -->
          <section id="faq" class="scroll-mt-8">
            <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
              <span class="text-primary">05.</span> FAQ
            </h3>
            <div class="space-y-4">
              <div v-for="(q, i) in faqs" :key="i" :id="`faq-${i}`" class="bg-bg-dark/30 rounded-xl p-5 border border-border-primary hover:border-primary/30 transition-colors scroll-mt-8">
                <h4 class="text-white font-semibold mb-2">Q: {{ q.question }}</h4>
                <p class="text-text-secondary text-sm">A: {{ q.answer }}</p>
              </div>
            </div>
          </section>

          <!-- Contact -->
          <section id="contact" class="scroll-mt-8">
            <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
              <span class="text-primary">06.</span> Contact & Feedback
            </h3>
            <div class="bg-gradient-to-br from-primary/10 to-blue-500/10 rounded-2xl p-6 border border-primary/20">
              <p class="text-text-secondary mb-6">
                Want to propose changes, report a bug, or just give feedback? Reach out to me:
              </p>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <a href="mailto:philgastberger@gmail.com" class="flex items-center gap-3 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors border border-white/10 group">
                  <span class="text-xl group-hover:scale-110 transition-transform">📧</span>
                  <div>
                    <div class="text-xs text-text-secondary">Email</div>
                    <div class="text-sm font-medium">philgastberger@gmail.com</div>
                  </div>
                </a>
                <div class="flex items-center gap-3 p-3 bg-white/5 rounded-lg border border-white/10 group">
                  <span class="text-xl group-hover:scale-110 transition-transform">💬</span>
                  <div>
                    <div class="text-xs text-text-secondary">Discord</div>
                    <div class="text-sm font-medium">daamn_it</div>
                  </div>
                </div>
                <div class="flex items-center gap-3 p-3 bg-white/5 rounded-lg border border-white/10 group">
                  <span class="text-xl group-hover:scale-110 transition-transform">🎮</span>
                  <div>
                    <div class="text-xs text-text-secondary">DuelingBook</div>
                    <div class="text-sm font-medium">Daamn</div>
                  </div>
                </div>
                <a href="https://instagram.com/phillicheese_" target="_blank" class="flex items-center gap-3 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors border border-white/10 group">
                  <span class="text-xl group-hover:scale-110 transition-transform">📸</span>
                  <div>
                    <div class="text-xs text-text-secondary">Instagram</div>
                    <div class="text-sm font-medium">@phillicheese_</div>
                  </div>
                </a>
              </div>
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
    answer: "On DuelingBook, click 'Export Deck', then 'Download Link'. Open that link and click 'Download XML File'. You can then upload that file here."
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
