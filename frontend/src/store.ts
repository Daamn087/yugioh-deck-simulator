
import { defineStore } from 'pinia';
import type { Requirement, CardCategory, CardEffectDefinition } from './api';
import { importDeckFromDuelingBook } from './api';

export const useSimulationStore = defineStore('simulation', {
    state: () => ({
        deckSize: 40,
        handSize: 5,
        simulations: 1000000,
        deckContents: {
        } as Record<string, number>,  // Keep for backward compatibility
        cardCategories: [] as CardCategory[],  // New field with subcategory support
        rules: [
            [{ card_name: "Starter", min_count: 1, operator: 'AND' }]
        ] as Requirement[][],
        cardEffects: [] as CardEffectDefinition[]
    }),
    persist: true,
    actions: {
        syncDeckContents() {
            // Sync deckContents from cardCategories for backward compatibility
            this.deckContents = this.cardCategories.reduce((acc, cat) => {
                acc[cat.name] = cat.count;
                return acc;
            }, {} as Record<string, number>);
        },
        deleteCategory(name: string) {
            // 1. Determine fallback
            const categories = this.cardCategories.map(c => c.name);
            const remaining = categories.filter(c => c !== name);
            const fallback = remaining.length > 0 ? remaining[0] : null;

            // 2. Remove category from cardCategories
            this.cardCategories = this.cardCategories.filter(c => c.name !== name);
            this.syncDeckContents();

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
        },
        async importFromDuelingBook(url: string) {
            const result = await importDeckFromDuelingBook(url);
            // Convert to cardCategories format
            this.cardCategories = Object.entries(result.deck_contents).map(([name, count]) => ({
                name,
                count,
                subcategories: []
            }));
            this.syncDeckContents();
            this.deckSize = result.deck_size;
        },
        exportConfig() {
            const config = {
                deckSize: this.deckSize,
                handSize: this.handSize,
                simulations: this.simulations,
                deckContents: this.deckContents,  // Keep for backward compatibility
                cardCategories: this.cardCategories,  // New field with subcategories
                rules: this.rules,
                cardEffects: this.cardEffects
            };

            const json = JSON.stringify(config, null, 2);
            const filename = `yugioh-deck-config-${new Date().toISOString().split('T')[0]}.json`;

            // Try to use the File System Access API for better UX (Chrome/Edge)
            if ('showSaveFilePicker' in window) {
                this.exportWithFilePicker(json, filename);
            } else {
                // Fallback for browsers that don't support File System Access API
                this.exportWithDownload(json, filename);
            }
        },
        async exportWithFilePicker(json: string, filename: string) {
            try {
                const handle = await (window as any).showSaveFilePicker({
                    suggestedName: filename,
                    types: [{
                        description: 'JSON Files',
                        accept: { 'application/json': ['.json'] }
                    }]
                });
                const writable = await handle.createWritable();
                await writable.write(json);
                await writable.close();
            } catch (err: any) {
                // User cancelled the dialog or error occurred
                if (err.name !== 'AbortError') {
                    console.error('Error saving file:', err);
                    // Fallback to regular download
                    this.exportWithDownload(json, filename);
                }
            }
        },
        exportWithDownload(json: string, filename: string) {
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            link.click();
            URL.revokeObjectURL(url);
        },
        importConfig(file: File): Promise<void> {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        const config = JSON.parse(e.target?.result as string);

                        // Validate and apply configuration
                        if (config.deckSize !== undefined) this.deckSize = config.deckSize;
                        if (config.handSize !== undefined) this.handSize = config.handSize;
                        if (config.simulations !== undefined) this.simulations = config.simulations;

                        // Handle cardCategories (new format) or deckContents (old format)
                        if (config.cardCategories !== undefined) {
                            this.cardCategories = config.cardCategories;
                            this.syncDeckContents();
                        } else if (config.deckContents !== undefined) {
                            // Migrate from old format
                            this.cardCategories = Object.entries(config.deckContents).map(([name, count]) => ({
                                name,
                                count: count as number,
                                subcategories: []
                            }));
                            this.syncDeckContents();
                        }

                        if (config.rules !== undefined) {
                            // Ensure backward compatibility: add default operator 'AND' if missing
                            this.rules = config.rules.map((group: Requirement[]) =>
                                group.map((req: Requirement) => ({
                                    ...req,
                                    operator: req.operator || 'AND'
                                }))
                            );
                        }

                        if (config.cardEffects !== undefined) {
                            this.cardEffects = config.cardEffects;
                        } else {
                            this.cardEffects = [];
                        }

                        resolve();
                    } catch (error) {
                        reject(new Error('Invalid configuration file'));
                    }
                };
                reader.onerror = () => reject(new Error('Failed to read file'));
                reader.readAsText(file);
            });
        },
        resetToDefaults() {
            this.deckSize = 40;
            this.handSize = 5;
            this.simulations = 1000000;
            this.deckContents = {};
            this.cardCategories = [];
            this.rules = [[{ card_name: "Starter", min_count: 1, operator: 'AND' }]];
            this.cardEffects = [];
        }
    }
});
