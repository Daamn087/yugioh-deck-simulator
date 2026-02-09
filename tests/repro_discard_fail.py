
import sys
import unittest
from collections import Counter
sys.path.append('src')

from deck_sim import Deck, Simulator, Rule
from card_effects import ConditionalDiscardEffect

class TestDiscardFailure(unittest.TestCase):
    def test_discard_failure_rate(self):
        # Setup from user report:
        # Deck: 3 Goldleo, 3 Vision, 34 others (Total 40)
        # 0 Droplet (Quick-Play)
        # Goldleo is the goal (>= 1)
        # Vision draws 2, discards 1 Quick-Play
        
        # We need to mock the subcategory map
        # Vision -> needs "Quick-Play"
        # But we will NOT put any "Quick-Play" cards in the deck
        
        deck_size = 40
        contents = {
            "Goldleo": 3,
            "Vision": 3,
            "Garbage": 34
        }
        
        # Subcategories: "Droplet" is "Quick-Play", but "Droplet" is NOT in deck.
        # So "Garbage", "Goldleo", "Vision" are NOT "Quick-Play".
        subcategory_map = {
            "Quick-Play": ["Droplet"] # Droplet is not in deck
        }
        
        # Effect: Vision draws 2, discards 1 "Quick-Play"
        effect = ConditionalDiscardEffect(draw_count=2, discard_filter="Quick-Play", discard_count=1)
        card_effects = {"Vision": effect}
        
        # Create deck
        deck = Deck(deck_size, contents)
        
        # Condition: Goldleo >= 1
        conditions = [Rule("Goldleo", 1)]
        
        # Run Simulation
        sim = Simulator(deck, subcategory_map, card_effects)
        # Hand size 5, 10000 sims
        result = sim.run(10000, 5, conditions)
        
        print(f"Success Rate with Effect (Zero targets): {result.success_rate * 100:.2f}%")
        
        # Baseline: No effect
        sim_baseline = Simulator(deck, subcategory_map, {})
        result_baseline = sim_baseline.run(10000, 5, conditions)
        print(f"Success Rate without Effect: {result_baseline.success_rate * 100:.2f}%")
        
        # The user observes ~37% with effect, ~33% without.
        # We expect them to be roughly equal if the fix is working (or if logic was strict).
        # Currently we expect them to differ.

if __name__ == '__main__':
    unittest.main()
