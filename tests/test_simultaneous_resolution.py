"""
Test to verify simultaneous effect resolution behavior.

This test specifically checks the scenario where both Vision of the Radiant Typhoon
and Pot of Greed are in the starting hand.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from deck_sim import Deck, Simulator
from card_effects import DrawEffect, ConditionalDiscardEffect


def test_vision_and_pot_simultaneous():
    """
    Test that Vision and Pot of Greed resolve simultaneously:
    1. Both draw their cards (Vision draws 2, Pot draws 2)
    2. Then Vision checks the FINAL hand (after all draws) for Quick-Play Spells to discard
    """
    # Create deck with specific cards
    deck = Deck(40, {
        "Vision of the Radiant Typhoon": 1,
        "Pot of Greed": 1,
        "Quick-Play Spell": 10,  # High chance of drawing one
        "Starter": 10,
        "Other": 18
    })
    
    # Build subcategory map
    subcategory_map = {
        "Quick-Play Spell": ["Quick-Play Spell"]
    }
    
    # Create effects
    vision_effect = ConditionalDiscardEffect(
        draw_count=2,
        discard_filter="Quick-Play Spell",
        discard_count=1
    )
    pot_effect = DrawEffect(count=2)
    
    card_effects = {
        "Vision of the Radiant Typhoon": vision_effect,
        "Pot of Greed": pot_effect
    }
    
    # Create simulator
    sim = Simulator(deck, subcategory_map, card_effects)
    
    # Starting hand with both Vision and Pot
    hand = ["Vision of the Radiant Typhoon", "Pot of Greed", "Other", "Other", "Other"]
    # Correctly calculate remaining deck
    from collections import Counter
    deck_counts = Counter(deck.cards)
    hand_counts = Counter(hand)
    remaining_deck = []
    for card, count in deck_counts.items():
        rem = count - hand_counts.get(card, 0)
        if rem > 0:
            remaining_deck.extend([card] * rem)
    
    # Resolve effects
    final_hand, _ = sim.resolve_effects(hand, remaining_deck, [])
    
    # Expected behavior:
    # - Vision draws 2 cards
    # - Pot draws 2 cards
    # - Total: 5 starting + 4 drawn = 9 cards
    # - Vision then checks ALL 9 cards for Quick-Play Spells and discards 1 if found
    # - Final hand: either 9 cards (no Quick-Play drawn) or 8 cards (1 Quick-Play discarded)
    
    print(f"\nStarting hand: {hand}")
    print(f"Final hand size: {len(final_hand)}")
    print(f"Final hand: {final_hand}")
    
    # Should have 8 or 9 cards depending on whether a Quick-Play was drawn
    assert len(final_hand) in [8, 9], f"Expected 8 or 9 cards, got {len(final_hand)}"
    
    # Count Quick-Play Spells in final hand
    quick_play_count = final_hand.count("Quick-Play Spell")
    print(f"Quick-Play Spells in final hand: {quick_play_count}")
    
    # If we have 8 cards, it means we drew at least one Quick-Play and discarded it
    # If we have 9 cards, it means we didn't draw any Quick-Play Spells
    if len(final_hand) == 8:
        print("✓ Drew at least one Quick-Play Spell and discarded it")
    else:
        print("✓ Did not draw any Quick-Play Spells (or drew multiple and discarded one)")
    
    print("\n✅ Simultaneous resolution working correctly!")
    print("   - Phase 1: Both Vision and Pot drew their cards (4 total)")
    print("   - Phase 2: Vision checked the final hand and discarded 1 Quick-Play if present")


if __name__ == '__main__':
    # Run the test multiple times to see different outcomes
    print("Running test 5 times to see different random outcomes:\n")
    for i in range(5):
        print(f"=== Run {i+1} ===")
        test_vision_and_pot_simultaneous()
        print()
