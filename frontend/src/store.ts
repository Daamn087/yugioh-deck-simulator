
import { defineStore } from 'pinia';
import type { Requirement } from './api';

export const useSimulationStore = defineStore('simulation', {
    state: () => ({
        deckSize: 40,
        handSize: 5,
        simulations: 1000000,
        deckContents: {
        } as Record<string, number>,
        rules: [
            [{ card_name: "Starter", min_count: 1 }]
        ] as Requirement[][]
    }),
    persist: true,
    actions: {
        deleteCategory(name: string) {
            // 1. Determine fallback
            const categories = Object.keys(this.deckContents);
            const remaining = categories.filter(c => c !== name);
            const fallback = remaining.length > 0 ? remaining[0] : null;

            // 2. Remove category
            const newContents = { ...this.deckContents };
            delete newContents[name];
            this.deckContents = newContents;

            // 3. Update rules
            if (fallback) {
                this.rules = this.rules.map(group =>
                    group.map(req => {
                        if (req.card_name === name) {
                            return { ...req, card_name: fallback };
                        }
                        return req;
                    })
                );
            } else {
                // If no categories left, remove rules that use the deleted category
                this.rules = this.rules.map(group =>
                    group.filter(req => req.card_name !== name)
                ).filter(group => group.length > 0);
            }
        }
    }
});
