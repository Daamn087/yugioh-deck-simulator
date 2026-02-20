"""
Test comparison operators for success conditions.
Tests both >= (at least) and = (exactly) operators.
"""
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '../src')
sys.path.append(src_path)

from deck_sim import Deck, Simulator, Rule, req
from collections import Counter


def test_greater_than_or_equal_operator():
    """Test >= operator (at least X copies)"""
    # Create a rule: at least 1 Starter
    rule = Rule("Starter", 1, '>=')
    
    # Test with 0 Starters - should fail
    hand = Counter({"Extender": 2, "Brick": 1})
    assert rule(hand) == False, "Should fail with 0 Starters"
    
    # Test with 1 Starter - should pass
    hand = Counter({"Starter": 1, "Extender": 1})
    assert rule(hand) == True, "Should pass with 1 Starter"
    
    # Test with 2 Starters - should pass
    hand = Counter({"Starter": 2, "Extender": 1})
    assert rule(hand) == True, "Should pass with 2 Starters"
    
    print("✓ >= operator works correctly")


def test_exactly_equal_operator():
    """Test = operator (exactly X copies)"""
    # Create a rule: exactly 1 Starter
    rule = Rule("Starter", 1, '==')
    
    # Test with 0 Starters - should fail
    hand = Counter({"Extender": 2, "Brick": 1})
    assert rule(hand) == False, "Should fail with 0 Starters"
    
    # Test with 1 Starter - should pass
    hand = Counter({"Starter": 1, "Extender": 1})
    assert rule(hand) == True, "Should pass with exactly 1 Starter"
    
    # Test with 2 Starters - should fail
    hand = Counter({"Starter": 2, "Extender": 1})
    assert rule(hand) == False, "Should fail with 2 Starters (need exactly 1)"
    
    print("✓ == operator works correctly")


def test_exactly_zero_anti_combo():
    """Test exactly 0 copies (anti-combo scenario)"""
    # Create a rule: exactly 0 Brick
    rule = Rule("Brick", 0, '==')
    
    # Test with 0 Bricks - should pass
    hand = Counter({"Starter": 2, "Extender": 1})
    assert rule(hand) == True, "Should pass with 0 Bricks"
    
    # Test with 1 Brick - should fail
    hand = Counter({"Starter": 1, "Brick": 1})
    assert rule(hand) == False, "Should fail with 1 Brick"
    
    # Test with 2 Bricks - should fail
    hand = Counter({"Brick": 2, "Starter": 1})
    assert rule(hand) == False, "Should fail with 2 Bricks"
    
    print("✓ Exactly 0 (anti-combo) works correctly")


def test_brilliant_fusion_garnet_scenario():
    """Test the user's specific scenario: Brilliant Fusion + Garnet"""
    # Deck: 3 Brilliant Fusion, 1 Garnet, 36 Filler
    deck = Deck(40, {
        "Brilliant Fusion": 3,
        "Garnet": 1,
        "Filler": 36
    })
    
    # Success condition: at least 1 Brilliant Fusion AND exactly 2 Garnets
    # This should be IMPOSSIBLE since there's only 1 Garnet in the deck
    rule_brilliant = Rule("Brilliant Fusion", 1, '>=')
    rule_garnet = Rule("Garnet", 2, '==')
    combined_rule = rule_brilliant & rule_garnet
    
    # Run simulation
    sim = Simulator(deck)
    result = sim.run(10000, 5, [combined_rule])
    
    # Should be 0% success rate (impossible to draw 2 Garnets when only 1 exists)
    assert result.success_rate == 0.0, f"Expected 0% success rate, got {result.success_rate}%"
    assert result.success_count == 0, f"Expected 0 successes, got {result.success_count}"
    
    print(f"✓ Brilliant Fusion + Garnet scenario: {result.success_rate}% success rate (expected 0%)")


def test_anti_combo_with_and_operator():
    """Test anti-combo: at least 1 Card A AND exactly 0 Card B"""
    # Deck: 10 Card A, 10 Card B, 20 Filler
    deck = Deck(40, {
        "Card A": 10,
        "Card B": 10,
        "Filler": 20
    })
    
    # Success condition: at least 1 Card A AND exactly 0 Card B
    rule_a = Rule("Card A", 1, '>=')
    rule_b = Rule("Card B", 0, '==')
    combined_rule = rule_a & rule_b
    
    # Run simulation
    sim = Simulator(deck)
    result = sim.run(10000, 5, [combined_rule])
    
    # Should have some success rate (hands with Card A but no Card B)
    # But not 100% (some hands will have both)
    assert 0 < result.success_rate < 100, f"Expected success rate between 0-100%, got {result.success_rate}%"
    
    print(f"✓ Anti-combo scenario: {result.success_rate:.2f}% success rate (Card A without Card B)")


def test_exactly_one_card():
    """Test exactly 1 copy of a card"""
    # Deck: 10 Starter, 30 Filler
    deck = Deck(40, {
        "Starter": 10,
        "Filler": 30
    })
    
    # Success condition: exactly 1 Starter
    rule = Rule("Starter", 1, '==')
    
    # Run simulation
    sim = Simulator(deck)
    result = sim.run(10000, 5, [rule])
    
    # Should have some success rate (not 0, not 100)
    assert 0 < result.success_rate < 100, f"Expected success rate between 0-100%, got {result.success_rate}%"
    
    print(f"✓ Exactly 1 Starter: {result.success_rate:.2f}% success rate")


if __name__ == "__main__":
    print("Testing comparison operators...\n")
    
    test_greater_than_or_equal_operator()
    test_exactly_equal_operator()
    test_exactly_zero_anti_combo()
    test_brilliant_fusion_garnet_scenario()
    test_anti_combo_with_and_operator()
    test_exactly_one_card()
    
    print("\n✅ All tests passed!")
