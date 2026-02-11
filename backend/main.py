
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from models import SimulationConfig, SimulationResult, CardEffectDefinition
from xml_deck_parser import parse_xml_deck
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
from card_effects import create_effect_from_definition

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # Explicitly allow localhost and 127.0.0.1 for both Vite default port and others
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add headers for Private Network Access (PNA) support
# This prevents Chrome's "device on your local network" popup
@app.middleware("http")
async def add_pna_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response

def build_rule(requirements):
    """Recursively build a Rule object from a list of requirements."""
    if not requirements:
        return req(None) >= 0 # Always True (empty group)
        
    # Process the first requirement
    first_req = requirements[0]
    
    if first_req.sub_requirements is not None:
        # It's a group! Recursively build the inner rule
        current_rule = build_rule(first_req.sub_requirements)
    else:
        # It's a standard card requirement
        current_rule = req(first_req.card_name) >= first_req.min_count

    # Combine with rest based on operator
    for i, r in enumerate(requirements[1:], start=0):
        if r.sub_requirements is not None:
            next_rule = build_rule(r.sub_requirements)
        else:
            next_rule = req(r.card_name) >= r.min_count
            
        # Use the operator from the PREVIOUS requirement (at index i)
        # Requirement[0] has operator that applies between [0] and [1]
        operator = requirements[i].operator if requirements[i].operator else 'AND'
        
        if operator == 'OR':
            current_rule = current_rule | next_rule
        else:  # Default to AND
            current_rule = current_rule & next_rule
            
    return current_rule


@app.post("/simulate", response_model=SimulationResult)
def run_simulation(config: SimulationConfig):
    try:
        # 1. Build Deck - support both old and new formats
        if config.card_categories:
            # New format: use card_categories with subcategories
            deck_contents = {cat.name: cat.count for cat in config.card_categories}
            deck = Deck(config.deck_size, deck_contents)
            
            # Build subcategory map: subcategory -> list of card names
            subcategory_map = {}
            for cat in config.card_categories:
                for subcat in cat.subcategories:
                    if subcat not in subcategory_map:
                        subcategory_map[subcat] = []
                    subcategory_map[subcat].append(cat.name)
        else:
            # Old format: use deck_contents (backward compatibility)
            deck = Deck(config.deck_size, config.deck_contents)
            subcategory_map = {}
        
        # 2. Build Rules
        # config.rules is List[List[Requirement]] (OR logic of AND clauses)
        # [[A], [B, C]] -> (Rule(A)) OR (Rule(B) & Rule(C))
        sim_conditions = []
        for condition_group in config.rules:
            sim_conditions.append(build_rule(condition_group))
            
        if not sim_conditions:
             # If no rules, assume everything is a success? Or failure? 
             # Usually failure if no success condition defined.
             # But let's handle empty case gracefully
             pass 

        # 3. Build Card Effects Registry
        card_effects = {}
        if config.card_effects:
            for effect_def in config.card_effects:
                try:
                    # Convert CardEffectDefinition to dict for factory function
                    effect_dict = {
                        'effect_type': effect_def.effect_type,
                        'parameters': effect_def.parameters
                    }
                    effect = create_effect_from_definition(effect_dict)
                    card_effects[effect_def.card_name] = effect
                except Exception as e:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Invalid effect definition for '{effect_def.card_name}': {str(e)}"
                    )

        # 4. Run Simulation with subcategory and effect support
        sim = Simulator(deck, subcategory_map, card_effects)
        start_time = time.time()
        result = sim.run(config.simulations, config.hand_size, sim_conditions)
        elapsed = time.time() - start_time
        
        return SimulationResult(
            success_rate=result.success_rate,
            brick_rate=result.brick_rate,
            success_count=result.success_count,
            brick_count=result.brick_count,
            time_taken=elapsed,
            max_depth_reached_count=result.max_depth_reached_count,
            warnings=result.warnings
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/import-deck")
async def import_deck(file: UploadFile = File(...)):
    """
    Import a deck from an XML file.
    
    Args:
        file: Uploaded XML deck file
        
    Returns:
        Dictionary mapping card names to counts for the main deck
    """
    if not file.filename or not file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail="File must be an XML file")
    
    try:
        # Read file contents
        xml_content = await file.read()
        
        # Parse the XML deck
        deck_contents = parse_xml_deck(xml_content)
        
        return {
            "deck_contents": deck_contents,
            "deck_size": sum(deck_contents.values())
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import deck: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
