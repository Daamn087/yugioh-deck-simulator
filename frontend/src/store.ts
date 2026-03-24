import { defineStore } from 'pinia';
import type { Requirement, CardCategory, CardEffectDefinition } from './api';
import { resolveCards } from './api';
import { CardCache, type CardCacheEntry } from './utils/cardCache';
import { optimizeImage, blobToDataURL } from './utils/imageOptimizer';
import { parseYDK } from './utils/ydkParser';

export const useSimulationStore = defineStore('simulation', {
    state: () => ({
        deckSize: 40,
        handSize: 5,
        simulations: 1000000,
        deckContents: {
        } as Record<string, number>,  // Keep for backward compatibility
        cardCategories: [] as CardCategory[],  // New field with subcategory support
        imageMap: {} as Record<string, string>, // Persistent cache for card images
        lastSeenChangelogVersion: null as string | null, // Track the last seen changelog version
        rules: [
            [{ card_name: "", min_count: 1, operator: 'AND' }]
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
        async importFromYDK(file: File) {
            const content = await file.text();
            const passcodes = parseYDK(content);
            const uniquePasscodes = [...new Set(passcodes)];
            
            const cachedData = await CardCache.getCards(uniquePasscodes);
            const missingPasscodes = uniquePasscodes.filter(p => !cachedData[p]);
            
            const allResolved: Record<string, { name: string, imageUrl?: string }> = {};
            
            // Load cached items
            for (const passcode of uniquePasscodes) {
                const entry = cachedData[passcode];
                if (entry) {
                    allResolved[passcode] = {
                        name: entry.name,
                        imageUrl: entry.imageBlob ? await blobToDataURL(entry.imageBlob) : undefined
                    };
                }
            }
            
            // Resolve missing cards via API
            if (missingPasscodes.length > 0) {
                try {
                    const apiResult = await resolveCards(missingPasscodes);
                    const newCacheEntries: Record<string, CardCacheEntry> = {};
                    
                    for (const [passcode, info] of Object.entries(apiResult.resolved_cards)) {
                        let imageBlob: Blob | undefined;
                        let displayUrl = info.image_url;
                        
                        if (info.image_url) {
                            try {
                                // Fetch and optimize the image
                                imageBlob = await optimizeImage(info.image_url);
                                displayUrl = await blobToDataURL(imageBlob);
                            } catch (e) {
                                console.warn(`Failed to optimize image for ${info.name}:`, e);
                            }
                        }
                        
                        allResolved[passcode] = {
                            name: info.name,
                            imageUrl: displayUrl
                        };
                        
                        newCacheEntries[passcode] = {
                            name: info.name,
                            imageBlob,
                            timestamp: Date.now()
                        };
                    }
                    
                    // Save new resolutions to persistent cache
                    await CardCache.saveCards(newCacheEntries);
                } catch (error) {
                    console.error('Failed to resolve missing cards:', error);
                    throw error;
                }
            }
            
            // Build the final deck structure
            const counts: Record<string, number> = {};
            const imageMap: Record<string, string> = {};
            
            for (const passcode of passcodes) {
                const info = allResolved[passcode];
                if (info) {
                    counts[info.name] = (counts[info.name] || 0) + 1;
                    if (info.imageUrl) {
                        imageMap[info.name] = info.imageUrl;
                    }
                }
            }
            
            // To properly track remote URLs, we need to know what they were before optimization
            const finalizedCategories: CardCategory[] = Object.entries(counts).map(([name, count]) => {
                // Find a passcode associated with this name
                const passcode = Object.keys(allResolved).find(pc => allResolved[pc]?.name === name);
                return {
                    name,
                    count: count as number,
                    subcategories: [],
                    imageUrl: imageMap[name],
                    passcode: passcode,
                };
            });

            // Update store state
            this.imageMap = { ...this.imageMap, ...imageMap };
            this.cardCategories = finalizedCategories;
            
            this.syncDeckContents();
            this.deckSize = passcodes.length;
        },
        async hydrateDecks() {
            // Restore images for categories that have a passcode but no local imageUrl (or binary blob)
            const missingImageCategories = this.cardCategories.filter(cat => cat.passcode && !this.imageMap[cat.name]);
            
            if (missingImageCategories.length === 0) return;
            
            const passcodes = missingImageCategories.map(cat => cat.passcode!);
            const cachedData = await CardCache.getCards(passcodes);
            
            const newImageMap: Record<string, string> = {};
            const newCacheEntries: Record<string, CardCacheEntry> = {};
            
            // Check cache first
            for (const cat of missingImageCategories) {
                const entry = cachedData[cat.passcode!];
                if (entry?.imageBlob) {
                    newImageMap[cat.name] = await blobToDataURL(entry.imageBlob);
                }
            }
            
            // For those still missing, we might need to re-resolve
            const stillMissing = missingImageCategories.filter(cat => !newImageMap[cat.name]);
            
            if (stillMissing.length > 0) {
                try {
                    const missingPasscodes = stillMissing.map(cat => cat.passcode!);
                    const apiResult = await resolveCards(missingPasscodes);
                    
                    for (const cat of stillMissing) {
                        const info = apiResult.resolved_cards[cat.passcode!];
                        if (info?.image_url) {
                            try {
                                const imageBlob = await optimizeImage(info.image_url);
                                const displayUrl = await blobToDataURL(imageBlob);
                                newImageMap[cat.name] = displayUrl;
                                
                                newCacheEntries[cat.passcode!] = {
                                    name: info.name,
                                    imageBlob,
                                    timestamp: Date.now()
                                };
                            } catch (e) {
                                console.warn(`Hydration failed for ${cat.name}:`, e);
                            }
                        }
                    }
                    
                    if (Object.keys(newCacheEntries).length > 0) {
                        await CardCache.saveCards(newCacheEntries);
                    }
                } catch (error) {
                    console.error('Hydration API call failed:', error);
                }
            }
            
            // Update state
            this.imageMap = { ...this.imageMap, ...newImageMap };
            // Update the categories with the new imageUrls
            this.cardCategories = this.cardCategories.map(cat => ({
                ...cat,
                imageUrl: this.imageMap[cat.name] || cat.imageUrl
            }));
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
        async importConfig(file: File): Promise<void> {
            const content = await file.text();
            try {
                const config = JSON.parse(content);

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
                    this.rules = config.rules.map((group: any[]) =>
                        group.map((req: any) => ({
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

                // Hydrate images after import
                await this.hydrateDecks();
            } catch (error) {
                console.error('Failed to import config:', error);
                throw new Error('Invalid configuration file');
            }
        },
        resetToDefaults() {
            this.deckSize = 40;
            this.handSize = 5;
            this.simulations = 1000000;
            this.deckContents = {};
            this.cardCategories = [];
            this.imageMap = {};
            this.rules = [[{ card_name: "", min_count: 1, operator: 'AND' }]];
            this.cardEffects = [];
        }
    },
    getters: {
        validationError: (state) => {
            if (state.cardCategories.length === 0) {
                return "Deck cannot be empty. Please add some cards or import a deck.";
            }

            if (state.rules.length === 0) {
                return "At least one success condition is required to run the simulation.";
            }

            // Get all valid names once for performance
            const validNames = new Set(state.cardCategories.map(c => c.name));
            state.cardCategories.forEach(cat => {
                cat.subcategories.forEach(sub => validNames.add(sub));
            });

            for (let i = 0; i < state.rules.length; i++) {
                const group = state.rules[i];
                if (!group || group.length === 0) {
                    return `Success Condition #${i + 1} is empty.`;
                }

                // Recursive check for requirements
                const checkRequirements = (reqs: Requirement[]): string | null => {
                    for (const req of reqs) {
                        if (req.sub_requirements && req.sub_requirements.length > 0) {
                            const error = checkRequirements(req.sub_requirements);
                            if (error) return error;
                        } else if (!req.sub_requirements) {
                            // Only check card_name if it's a leaf requirement
                            if (!req.card_name || req.card_name.trim() === '') {
                                return `A requirement in Success Condition #${i + 1} is missing a card or tag selection.`;
                            }
                            if (!validNames.has(req.card_name)) {
                                return `Success Condition #${i + 1} references "${req.card_name}", which is not in your deck.`;
                            }
                        }
                    }
                    return null;
                };

                const error = checkRequirements(group);
                if (error) return error;
            }

            return null;
        },
        availableCategories: (state) => [...new Set(state.cardCategories.map(c => c.name))]
    }
});
