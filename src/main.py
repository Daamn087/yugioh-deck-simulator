from deck_sim import Deck, Simulator, req
from collections import Counter
import time

def main():
    # ==========================================
    #           USER CONFIGURATION
    # ==========================================
    
    # 1. Deck Settings
    DECK_TOTAL = 40
    
    # Dictionary of Card Category: Quantity
    # Any remaining space in the deck will be filled with undefined "Other" cards
    DECK_CONTENTS = {
        "Starter": 3,       # e.g., Aluber, Opening
        "Extender": 8,       # e.g., Lubellion
        "HandTrap": 12,      # e.g., Ash, Imperm
        "Garnet": 2          # Cards you don't want to draw
    }
    
    # 2. Simulation Settings
    NUM_SIMULATIONS = 1_000_000
    HAND_SIZE = 5  # 5 for going first, 6 for going second
    
    # 3. Success Conditions
    # A hand is successful if it meets AT LEAST ONE of these conditions.
    # Use req("Name") to define requirements.
    #   req("Starter")          -> At least 1 Starter
    #   req("Starter") >= 2     -> At least 2 Starters
    #   req("A") & req("B")     -> A AND B
    
    success_rules = [
        # Example 1: Open at least one Starter
        req("Starter"),
        
        # Example 2: Open "Extender" AND "HandTrap"
        # req("Extender") & req("HandTrap"),
        
        # Example 3: Two Starters
        # req("Starter") >= 2,
    ]
    
    # ==========================================
    #        END CONFIGURATION
    # ==========================================

    print(f"--- Yu-Gi-Oh! Deck Consistency Simulator ---")
    print(f"Deck Size: {DECK_TOTAL}")
    print(f"Hand Size: {HAND_SIZE}")
    print(f"Simulations: {NUM_SIMULATIONS:,}")
    print(f"Deck Contents: {DECK_CONTENTS}")
    print(f"Calculating...")

    start_time = time.time()
    
    # Initialize
    try:
        deck = Deck(DECK_TOTAL, DECK_CONTENTS)
    except ValueError as e:
        print(f"Error in deck configuration: {e}")
        return

    sim = Simulator(deck)
    
    # Run
    result = sim.run(NUM_SIMULATIONS, HAND_SIZE, success_rules)
    
    elapsed = time.time() - start_time
    
    # Output
    print(f"\n--- Results ---")
    print(f"Time Taken: {elapsed:.2f} seconds")
    print(f"Successful Hands: {result.success_count:,} ({result.success_rate:.2f}%)")
    print(f"Bricks (Failures): {result.brick_count:,} ({result.brick_rate:.2f}%)")

if __name__ == "__main__":
    main()
