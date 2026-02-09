# Yu-Gi-Oh! Deck Consistency Simulator

A powerful tool to simulate Yu-Gi-Oh! starting hands and calculate consistency probabilities. It features a Python backend for fast simulations and a modern Vue.js frontend for a premium user experience.

## Features

- **Deck Building**: Configure deck size and card categories (Starters, Extenders, Handtraps, etc.).
- **Rule Engine**: Define complex success conditions using a visual rule builder (e.g., "Must open 1 Starter AND 1 Extender" OR "1 Starter AND 2 Handtraps").
- **Fast Simulation**: Powered by a Python backend capable of running millions of simulations in seconds.
- **Detailed Results**: View success rates, brick rates, and precise probability breakdowns.
- **User-Friendly Interface**: Modern dark-mode UI with real-time feedback.

## Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **Frontend**: Vue.js 3 + TypeScript + Vite
- **Simulation**: Python standard library (optimized for speed)

## Getting Started

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
    cd yugioh-deck-simulator
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    pip install fastapi uvicorn
    pip install selenium
    ```

3.  **Frontend Setup:**
    ```bash
    # Open a new terminal in the project root
    cd yugioh-deck-simulator/frontend
    npm install
    ```

### Running the Application

1.  **Start the Backend:**
    ```bash
    # From yugioh-deck-simulator/ directory with venv activated
    python backend/main.py
    ```
    The API will run at `http://localhost:8000`.

2.  **Start the Frontend:**
    ```bash
    # From yugioh-deck-simulator/frontend/ directory
    npm run dev
    ```
    Open the link provided by Vite (usually `http://localhost:5173`) in your browser.

## Testing

The project includes comprehensive test suites for both the simulation logic and backend integration.

### Running All Tests

From the project root directory with the virtual environment activated:

```bash
# Activate virtual environment if not already active
source venv/bin/activate

# Run all tests
python -m unittest discover tests -v
```

### Running Specific Test Suites

```bash
# Test operator logic (AND/OR functionality)
python -m unittest tests.test_operator_logic -v

# Test backend integration
python -m unittest tests.test_backend_integration -v

# Test core mechanics
python -m unittest tests.test_mechanics -v
```

### Pre-commit Hook

The repository includes a pre-commit hook that automatically runs all tests before each commit. If any test fails, the commit will be blocked.

The hook is automatically installed in `.git/hooks/pre-commit` and will:
- Run all test suites
- Display test results
- Block the commit if any tests fail
- Allow the commit only if all tests pass

## CLI Usage

You can also run simulations directly from the command line:

```bash
python src/main.py
```
Modify `src/main.py` to change deck parameters and rules.

## License

MIT
