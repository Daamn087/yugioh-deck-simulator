
export interface Requirement {
    card_name?: string;
    min_count?: number;
    operator?: 'AND' | 'OR';  // Operator to use after this requirement
    sub_requirements?: Requirement[];
}

export interface CardCategory {
    name: string;
    count: number;
    subcategories: string[];
}

export interface CardEffectDefinition {
    card_name: string;
    effect_type: 'draw' | 'conditional_discard' | string;
    parameters: Record<string, any>;
}

export interface SimulationConfig {
    deck_size: number;
    deck_contents: Record<string, number>;  // Keep for backward compatibility
    card_categories?: CardCategory[];  // New field with subcategory support
    hand_size: number;
    simulations: number;
    rules: Requirement[][];
    card_effects?: CardEffectDefinition[];
}

export interface SimulationResult {
    success_rate: number;
    brick_rate: number;
    success_count: number;
    brick_count: number;
    time_taken: number;
    max_depth_reached_count: number;
    warnings: string[];
}

// Use environment variable for API URL or fallback to local
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function runSimulation(config: SimulationConfig): Promise<SimulationResult> {
    const response = await fetch(`${API_URL}/simulate`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(config),
    });

    if (!response.ok) {
        const error = await response.json();
        const errorMessage = error.detail
            ? (typeof error.detail === 'string' ? error.detail : JSON.stringify(error.detail))
            : "Simulation failed";
        throw new Error(errorMessage);
    }

    return response.json();
}

export async function importDeckFromXML(file: File): Promise<{ deck_contents: Record<string, number>, deck_size: number }> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_URL}/api/import-deck`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to import deck");
    }

    return response.json();
}
