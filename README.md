# Yu-Gi-Oh! Deck Consistency Simulator

A powerful, Monte Carlo-based tool to simulate Yu-Gi-Oh! starting hands and calculate consistency probabilities. It features a high-performance Python backend and a modern Vue.js frontend, now with support for advanced card effects and external deck imports.

## 🚀 Key Features

### 🃏 Deck Building & Logic
- **Smart Category Management**: Define custom tags like "Starter", "Extender", "Handtrap", or specific engines.
- **Advanced Rule Engine**: Build complex success conditions using a visual builder (e.g., `"Starter" >= 1 AND ("Extender" >= 1 OR "Pot of Greed" >= 1)`).
- **DuelingBook Import**: Directly import decks from DuelingBook using the URL.
- **Config Management**: Export and Import your entire simulation setup (deck, rules, effects) to JSON/File.

### ✨ Card Effects System (New!)
Simulate the actual gameplay impact of draw power and consistency cards.
- **Draw Effects**: Simulate cards like *Pot of Greed* (Draw 2).
- **Conditional Effects**: Simulate complex cards like *Vision of the Radiant Typhoon* (Draw 2, then discard 1 "Quick-Play Spell" if possible).
- **Simultaneous Resolution**: Effects resolve in a single pass with intelligent ordering (Draws trigger first, then Discards), preventing infinite loops while capturing true hand quality.
- **Strict Logic**: If a discard cost cannot be paid (e.g., no target in hand), the effect reverts, ensuring accurate probabilities.

### ⚡ Performance & Accuracy
- **Monte Carlo Simulation**: Runs 100,000 to 1,000,000 hands in seconds to handle dynamic game states that static math cannot model. [Read why we use Simulation vs Calculation here](docs/simulation_vs_calculation.md).
- **Optimized Backend**: Core logic ignores effect overhead when no effects are active, maintaining blazing fast speeds (~2.7s per million hands).
- **Detailed Analytics**: View Success Rates, Brick Rates, and specific breakdown of which rules failed/passed.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.13+)
- **Frontend**: Vue.js 3 + TypeScript + Vite + Pinia
- **Simulation**: Python standard library (optimized with `collections.Counter`)
- **Testing**: `unittest` with comprehensive regression suites

## 🏁 Getting Started

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Daamn087/yugioh-deck-simulator.git
    cd yugioh-deck-simulator
    ```

2.  **Backend Setup:**
    ```bash
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    pip install fastapi uvicorn selenium webdriver-manager
    ```

3.  **Frontend Setup:**
    ```bash
    cd frontend
    npm install
    ```

### Running the Application

1.  **Start the Backend:**
    ```bash
    # From project root with venv activated
    python backend/main.py
    ```
    The API runs at `http://localhost:8000`.

2.  **Start the Frontend:**
    ```bash
    # From frontend/ directory
    npm run dev
    ```
    Open `http://localhost:5173` in your browser.

## 🧪 Testing

The project is robustly tested to ensure simulation accuracy.

### Running All Tests
```bash
# From project root
python -m unittest discover tests -v
```

### Key Test Suites
- **`tests/test_card_effects.py`**: Verifies draw/discard logic, regression fixes, and OPT constraints.
- **`tests/test_simultaneous_resolution.py`**: Verifies complex interactions (e.g., Drawing + Discarding happening in correct phases).
- **`tests/test_mechanics.py`**: Verifies core probability logic.

## 📝 License

MIT
