import { get, set, setMany } from 'idb-keyval';

export interface CardCacheEntry {
    name: string;
    imageBlob?: Blob;
    timestamp: number;
}

const CACHE_KEY_PREFIX = 'card_';

/**
 * Service to handle persistent card data caching using IndexedDB.
 */
export const CardCache = {
    /**
     * Get a single card from the cache.
     */
    async getCard(passcode: string): Promise<CardCacheEntry | undefined> {
        return await get(`${CACHE_KEY_PREFIX}${passcode.padStart(8, '0')}`);
    },

    /**
     * Get multiple cards from the cache.
     */
    async getCards(passcodes: string[]): Promise<Record<string, CardCacheEntry>> {
        const results: Record<string, CardCacheEntry> = {};
        const normalizedPasscodes = passcodes.map(p => p.padStart(8, '0'));
        
        // This is a bit inefficient for very many cards, but idb-keyval doesn't have a direct getMany that returns keys
        // We can optimize by using entries() if we need to
        for (const passcode of normalizedPasscodes) {
            const entry = await this.getCard(passcode);
            if (entry) {
                results[passcode] = entry;
            }
        }
        
        return results;
    },

    /**
     * Save a single card to the cache.
     */
    async saveCard(passcode: string, entry: CardCacheEntry): Promise<void> {
        await set(`${CACHE_KEY_PREFIX}${passcode.padStart(8, '0')}`, entry);
    },

    /**
     * Save multiple cards to the cache in batch.
     */
    async saveCards(data: Record<string, CardCacheEntry>): Promise<void> {
        const entries: [string, CardCacheEntry][] = Object.entries(data).map(([passcode, entry]) => [
            `${CACHE_KEY_PREFIX}${passcode.padStart(8, '0')}`,
            entry
        ]);
        await setMany(entries);
    },

    /**
     * Clear the cache.
     */
    async clear(): Promise<void> {
        // Implementation for clearing specific prefix would require using the underlying IDB store
        // For simplicity, we can just clear everything if needed, but let's leave it for now
    }
};
