
export interface Requirement {
    card_name: string;
    min_count: number;
}

export interface SimulationConfig {
    deck_size: number;
    deck_contents: Record<string, number>;
    hand_size: number;
    simulations: number;
    rules: Requirement[][];
}

export interface SimulationResult {
    success_rate: number;
    brick_rate: number;
    success_count: number;
    brick_count: number;
    time_taken: number;
}

const API_URL = "http://localhost:8000";

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
        throw new Error(error.detail || "Simulation failed");
    }

    return response.json();
}
