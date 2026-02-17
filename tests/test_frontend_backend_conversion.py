"""
Test that frontend '=' is correctly converted to backend '==' operator.
"""
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '../src')
backend_path = os.path.join(current_dir, '../backend')
sys.path.append(src_path)
sys.path.append(backend_path)

from deck_sim import Deck, Simulator, Rule
from models import Requirement
from main import build_rule


def test_frontend_equals_conversion():
    """Test that '=' from frontend is converted to '==' in backend"""
    # Simulate frontend sending '=' operator
    req = Requirement(
        card_name="Brilliant Fusion",
        min_count=1,
        comparison_operator='='  # Frontend sends '='
    )
    
    # Build rule (should convert '=' to '==')
    rule = build_rule([req])
    
    # Check that the rule has '==' internally
    assert rule.comparison == '==', f"Expected '==' but got '{rule.comparison}'"
    print(f"✓ Frontend '=' correctly converted to backend '==' (rule.comparison = '{rule.comparison}')")


def test_simulation_with_exactly_one():
    """Test simulation with exactly 1 copy requirement"""
    # Deck: 3 Brilliant Fusion, 37 Filler
    deck = Deck(40, {
        "Brilliant Fusion": 3,
        "Filler": 37
    })
    
    # Test 1: At least 1 Brilliant Fusion
    req_at_least = Requirement(
        card_name="Brilliant Fusion",
        min_count=1,
        comparison_operator='>='
    )
    rule_at_least = build_rule([req_at_least])
    sim = Simulator(deck)
    result_at_least = sim.run(10000, 5, [rule_at_least])
    
    # Test 2: Exactly 1 Brilliant Fusion
    req_exactly = Requirement(
        card_name="Brilliant Fusion",
        min_count=1,
        comparison_operator='='  # Frontend sends '='
    )
    rule_exactly = build_rule([req_exactly])
    sim = Simulator(deck)
    result_exactly = sim.run(10000, 5, [rule_exactly])
    
    print(f"\nDeck: 3 Brilliant Fusion, 37 Filler, Hand size: 5")
    print(f"At least 1 Brilliant Fusion: {result_at_least.success_rate:.2f}%")
    print(f"Exactly 1 Brilliant Fusion:  {result_exactly.success_rate:.2f}%")
    
    # Exactly 1 should be LOWER than at least 1
    # Because "at least 1" includes hands with 2 or 3 copies
    # But "exactly 1" excludes those hands
    assert result_exactly.success_rate < result_at_least.success_rate, \
        f"Exactly 1 ({result_exactly.success_rate}%) should be lower than at least 1 ({result_at_least.success_rate}%)"
    
    print(f"✓ Exactly 1 ({result_exactly.success_rate:.2f}%) < At least 1 ({result_at_least.success_rate:.2f}%)")


if __name__ == "__main__":
    print("Testing frontend '=' to backend '==' conversion...\n")
    
    test_frontend_equals_conversion()
    test_simulation_with_exactly_one()
    
    print("\n✅ All conversion tests passed!")
