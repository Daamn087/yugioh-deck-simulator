
import sys
import os
from collections import Counter

# Add src and backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from deck_sim import Deck, Simulator, req
from card_effects import DrawEffect

def test_pot_of_greed_fix():
    print("Testing Pot of Greed fix with verbose logging...")
    # Deck: 1x Leo, 3x Pot, 36x Other
    deck = Deck(40, {"Lunar Light Gold Leo": 1, "Pot of Greed": 3, "Other": 36})
    rule = req("Lunar Light Gold Leo") >= 1
    
    # 1. Without effects
    sim_no = Simulator(deck, {}, {})
    result_no = sim_no.run(10000, 5, [rule])
    print(f"Success rate without effects: {result_no.success_rate}%")

    # 2. With Draw 20 effect
    pot_effect = DrawEffect(count=20)
    sim_yes = Simulator(deck, {}, {"Pot of Greed": pot_effect})
    result_yes = sim_yes.run(10000, 5, [rule])
    print(f"Success rate with Draw 20: {result_yes.success_rate}%")
    
    if result_yes.success_rate > result_no.success_rate + 5:
        print("Test Passed: Success rate increased significantly!")
    else:
        print("Test Failed: Success rate did not increase as expected.")

if __name__ == "__main__":
    test_pot_of_greed_fix()
