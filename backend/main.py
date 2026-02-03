
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import SimulationConfig, SimulationResult
import sys
import os
import time

# Add src to path to import deck_sim
# Assuming structure:
# yugioh_sim/
#   backend/
#     main.py
#   src/
#     deck_sim.py
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from deck_sim import Deck, Simulator, req, Rule, CompositeRule

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/simulate", response_model=SimulationResult)
def run_simulation(config: SimulationConfig):
    try:
        # 1. Build Deck
        deck = Deck(config.deck_size, config.deck_contents)
        
        # 2. Build Rules
        # config.rules is List[List[Requirement]] (OR logic of AND clauses)
        # [[A], [B, C]] -> (Rule(A)) OR (Rule(B) & Rule(C))
        
        sim_conditions = []
        for condition_group in config.rules:
            # logic: AND together all requirements in this group
            if not condition_group:
                continue
                
            # Create first rule
            current_rule = req(condition_group[0].card_name) >= condition_group[0].min_count
            
            # AND with rest
            for r in condition_group[1:]:
                next_rule = req(r.card_name) >= r.min_count
                current_rule = current_rule & next_rule
            
            sim_conditions.append(current_rule)
            
        if not sim_conditions:
             # If no rules, assume everything is a success? Or failure? 
             # Usually failure if no success condition defined.
             # But let's handle empty case gracefully
             pass 

        # 3. Run Simulation
        sim = Simulator(deck)
        start_time = time.time()
        result = sim.run(config.simulations, config.hand_size, sim_conditions)
        elapsed = time.time() - start_time
        
        return SimulationResult(
            success_rate=result.success_rate,
            brick_rate=result.brick_rate,
            success_count=result.success_count,
            brick_count=result.brick_count,
            time_taken=elapsed
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
