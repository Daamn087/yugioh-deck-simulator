"""
Debug test to see what's happening with the exactly operator
"""
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '../src')
sys.path.append(src_path)

from deck_sim import Deck, Simulator, Rule
from collections import Counter


def test_rule_directly():
    """Test the Rule class directly with sample hands"""
    print("Testing Rule class directly:\n")
    
    # Create rules
    rule_at_least = Rule("Brilliant Fusion", 1, '>=')
    rule_exactly = Rule("Brilliant Fusion", 1, '==')
    
    # Test with different hand scenarios
    test_hands = [
        Counter({"Brilliant Fusion": 0, "Filler": 5}),
        Counter({"Brilliant Fusion": 1, "Filler": 4}),
        Counter({"Brilliant Fusion": 2, "Filler": 3}),
        Counter({"Brilliant Fusion": 3, "Filler": 2}),
    ]
    
    for hand in test_hands:
        bf_count = hand["Brilliant Fusion"]
        at_least_result = rule_at_least(hand)
        exactly_result = rule_exactly(hand)
        
        print(f"Hand with {bf_count} Brilliant Fusion:")
        print(f"  >= 1: {at_least_result}")
        print(f"  == 1: {exactly_result}")
        print(f"  Rule comparison attribute: '{rule_exactly.comparison}'")
        print()


def test_simulation_with_logging():
    """Run simulation and check what rules are being created"""
    print("\nTesting simulation with rule inspection:\n")
    
    deck = Deck(40, {
        "Brilliant Fusion": 3,
        "Filler": 37
    })
    
    # Create rules
    rule_at_least = Rule("Brilliant Fusion", 1, '>=')
    rule_exactly = Rule("Brilliant Fusion", 1, '==')
    
    print(f"At least rule: {rule_at_least}")
    print(f"Exactly rule: {rule_exactly}")
    print(f"At least comparison: '{rule_at_least.comparison}'")
    print(f"Exactly comparison: '{rule_exactly.comparison}'")
    print()
    
    # Run simulations
    sim = Simulator(deck)
    result_at_least = sim.run(10000, 5, [rule_at_least])
    result_exactly = sim.run(10000, 5, [rule_exactly])
    
    print(f"At least 1: {result_at_least.success_rate:.2f}%")
    print(f"Exactly 1:  {result_exactly.success_rate:.2f}%")
    print(f"Difference: {result_at_least.success_rate - result_exactly.success_rate:.2f}%")
    print()
    
    # Expected from hypergeometric: at least 33.76%, exactly 30.11%
    # Difference should be ~3.65%
    expected_diff = 3.65
    actual_diff = result_at_least.success_rate - result_exactly.success_rate
    
    if abs(actual_diff - expected_diff) > 1.0:
        print(f"⚠️  WARNING: Difference is {actual_diff:.2f}%, expected ~{expected_diff}%")
        return False
    else:
        print(f"✓ Difference is correct: {actual_diff:.2f}% (expected ~{expected_diff}%)")
        return True


if __name__ == "__main__":
    test_rule_directly()
    success = test_simulation_with_logging()
    
    if not success:
        print("\n❌ Test failed - exactly operator is not working correctly")
        sys.exit(1)
    else:
        print("\n✅ Test passed!")
