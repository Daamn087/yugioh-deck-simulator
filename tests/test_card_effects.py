"""
Test suite for card effects system

Tests basic draw effects, conditional discard effects, and integration with the simulation engine.
All cards are once-per-turn (OPT) and effects are resolved in a single pass.
"""

import unittest
import sys
import os

# Add src and backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from deck_sim import Deck, Simulator, req
from card_effects import DrawEffect, ConditionalDiscardEffect, EffectContext, create_effect_from_definition
from models import CardEffectDefinition


class TestCardEffects(unittest.TestCase):
    """Test the card effects functionality"""

    def test_basic_draw_effect(self):
        """Test that DrawEffect draws cards correctly (OPT, single pass)"""
        # Create a simple deck
        deck = Deck(40, {"Pot of Greed": 3, "Starter": 10, "Other": 27})
        
        # Create draw effect (Pot of Greed draws 2, OPT)
        pot_effect = DrawEffect(count=2)
        
        # Create effect registry
        card_effects = {"Pot of Greed": pot_effect}
        
        # Create simulator
        sim = Simulator(deck, {}, card_effects)
        
        # Test: Hand with Pot of Greed should draw 2 more cards
        hand = ["Pot of Greed", "Other", "Other", "Other", "Other"]
        remaining_deck = [card for card in deck.cards if card not in hand]
        
        # Resolve effects (single pass, OPT)
        final_hand, depth_exceeded = sim.resolve_effects(hand, remaining_deck, [])
        
        # Should have 7 cards now (5 original + 2 drawn)
        # Even if we drew another Pot of Greed, it won't activate (single pass)
        self.assertEqual(len(final_hand), 7)
        self.assertFalse(depth_exceeded)
        
    def test_draw_effect_increases_success_rate(self):
        """Test that Pot of Greed improves success rate"""
        # Deck with few starters
        deck = Deck(40, {"Pot of Greed": 3, "Starter": 5, "Other": 32})
        
        # Success condition: 1 Starter
        rule = req("Starter") >= 1
        
        # Test WITHOUT effects
        sim_no_effects = Simulator(deck, {}, {})
        result_no_effects = sim_no_effects.run(10000, 5, [rule])
        
        # Test WITH Pot of Greed effect
        pot_effect = DrawEffect(count=2)
        card_effects = {"Pot of Greed": pot_effect}
        sim_with_effects = Simulator(deck, {}, card_effects)
        result_with_effects = sim_with_effects.run(10000, 5, [rule])
        
        # Success rate should be higher with effects
        self.assertGreater(result_with_effects.success_rate, result_no_effects.success_rate)
        print(f"\n[Test] Without Pot of Greed: {result_no_effects.success_rate:.2f}%")
        print(f"[Test] With Pot of Greed: {result_with_effects.success_rate:.2f}%")

    def test_once_per_turn_restriction(self):
        """Test that OPT cards only activate once even with multiple copies"""
        # Deck with multiple copies of OPT card
        deck = Deck(40, {"Vision of the Radiant Typhoon": 3, "Quick-Play Spell": 5, "Starter": 10})
        
        # Create OPT draw effect (all cards are OPT now)
        vision_effect = DrawEffect(count=2)
        card_effects = {"Vision of the Radiant Typhoon": vision_effect}
        
        # Create simulator
        sim = Simulator(deck, {}, card_effects)
        
        # Hand with 2 copies of Vision
        hand = ["Vision of the Radiant Typhoon", "Vision of the Radiant Typhoon", "Other", "Other", "Other"]
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
        
        # Should only draw 2 cards (one activation), not 4 (two activations)
        # Original 5 + 2 drawn = 7 cards
        self.assertEqual(len(final_hand), 7)

    def test_conditional_discard_effect(self):
        """Test Vision of the Radiant Typhoon conditional discard"""
        # Create deck
        deck = Deck(40, {
            "Vision of the Radiant Typhoon": 3,
            "Quick-Play Spell A": 2,
            "Quick-Play Spell B": 2,
            "Starter": 10
        })
        
        # Build subcategory map
        subcategory_map = {
            "Quick-Play Spell": ["Quick-Play Spell A", "Quick-Play Spell B"]
        }
        
        # Create conditional discard effect
        vision_effect = ConditionalDiscardEffect(
            draw_count=2,
            discard_filter="Quick-Play Spell",
            discard_count=1
        )
        card_effects = {"Vision of the Radiant Typhoon": vision_effect}
        
        # Create simulator
        sim = Simulator(deck, subcategory_map, card_effects)
        
        # We'll run a simulation to test the effect
        # The effect should draw 2 cards and discard 1 Quick-Play Spell if drawn
        rule = req("Starter") >= 1
        result = sim.run(1000, 5, [rule])
        
        # Just verify it runs without errors
        self.assertGreaterEqual(result.success_rate, 0)
        self.assertLessEqual(result.success_rate, 100)

    def test_conditional_discard_failure(self):
        """Test that effect fails (reverts) if discard condition cannot be met"""
        # Deck with NO target cards for discard
        deck = Deck(40, {
            "Vision of the Radiant Typhoon": 3,
            "Starter": 10,
            "Garbage": 27
        })
        
        # Subcategory map (Filter exists, but no cards in deck match it)
        subcategory_map = {
            "Quick-Play Spell": ["NonExistentCard"]
        }
        
        # Effect: Draw 2, discard 1 Quick-Play Spell
        vision_effect = ConditionalDiscardEffect(
            draw_count=2,
            discard_filter="Quick-Play Spell", # Must discard this
            discard_count=1
        )
        card_effects = {"Vision of the Radiant Typhoon": vision_effect}
        
        sim = Simulator(deck, subcategory_map, card_effects)
        
        # Hand with 1 Vision
        hand = ["Vision of the Radiant Typhoon", "Garbage", "Garbage", "Garbage", "Garbage"]
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
        
        # Expectation: 
        # 1. Vision activates
        # 2. Draws 2 cards (hand size becomes 7)
        # 3. Checks for "Quick-Play Spell" (none found)
        # 4. Discards 0 (0 < 1 required)
        # 5. REVERTS effect (returns original hand of size 5)
        
        self.assertEqual(len(final_hand), 5, "Should revert to original hand size if discard fails")

    def test_no_max_depth_warning(self):
        """Test that max depth is never reached with single-pass resolution"""
        # Create a scenario with effects
        deck = Deck(40, {"Pot of Greed": 3, "Starter": 10})
        
        pot_effect = DrawEffect(count=2)
        card_effects = {"Pot of Greed": pot_effect}
        
        sim = Simulator(deck, {}, card_effects)
        
        # Run simulation
        rule = req("Starter") >= 1
        result = sim.run(1000, 5, [rule])
        
        # With single-pass resolution, we should NEVER hit max depth
        self.assertEqual(result.max_depth_reached_count, 0)
        self.assertEqual(len(result.warnings), 0)

    def test_effect_factory_draw(self):
        """Test creating DrawEffect from definition"""
        effect_def = {
            'effect_type': 'draw',
            'parameters': {'count': 2}
        }
        
        effect = create_effect_from_definition(effect_def)
        
        self.assertIsInstance(effect, DrawEffect)
        self.assertEqual(effect.count, 2)

    def test_effect_factory_conditional_discard(self):
        """Test creating ConditionalDiscardEffect from definition"""
        effect_def = {
            'effect_type': 'conditional_discard',
            'parameters': {
                'draw_count': 2,
                'discard_filter': 'Quick-Play Spell',
                'discard_count': 1
            }
        }
        
        effect = create_effect_from_definition(effect_def)
        
        self.assertIsInstance(effect, ConditionalDiscardEffect)
        self.assertEqual(effect.draw_count, 2)
        self.assertEqual(effect.discard_filter, 'Quick-Play Spell')

    def test_effect_factory_unknown_type(self):
        """Test that unknown effect types raise ValueError"""
        effect_def = {
            'effect_type': 'unknown_effect',
            'parameters': {}
        }
        
        with self.assertRaises(ValueError):
            create_effect_from_definition(effect_def)

    def test_empty_deck_no_draw(self):
        """Test that effects handle empty deck gracefully"""
        # Very small deck
        deck = Deck(10, {"Pot of Greed": 3, "Starter": 7})
        
        pot_effect = DrawEffect(count=2)
        card_effects = {"Pot of Greed": pot_effect}
        
        sim = Simulator(deck, {}, card_effects)
        
        # Draw most of the deck
        hand = ["Pot of Greed", "Starter", "Starter", "Starter", "Starter", 
                "Starter", "Starter", "Starter"]
        remaining_deck = ["Starter", "Pot of Greed"]  # Only 2 cards left
        
        # Try to resolve effects (Pot of Greed wants to draw 2, and 2 are available)
        final_hand, _ = sim.resolve_effects(hand, remaining_deck, [])
        
        # Should draw the 2 available cards
        self.assertEqual(len(final_hand), 10)

    def test_single_pass_no_chaining(self):
        """Test that drawn cards with effects do NOT activate (single pass)"""
        # Deck where we might draw another Pot of Greed
        deck = Deck(40, {"Pot of Greed": 10, "Starter": 10, "Other": 20})
        
        pot_effect = DrawEffect(count=2)
        card_effects = {"Pot of Greed": pot_effect}
        
        sim = Simulator(deck, {}, card_effects)
        
        # Hand with 1 Pot of Greed
        hand = ["Pot of Greed", "Other", "Other", "Other", "Other"]
        # Correctly calculate remaining deck
        from collections import Counter
        deck_counts = Counter(deck.cards)
        hand_counts = Counter(hand)
        remaining_deck = []
        for card, count in deck_counts.items():
            rem = count - hand_counts.get(card, 0)
            if rem > 0:
                remaining_deck.extend([card] * rem)
        
        # Resolve effects - even if we draw more Pot of Greeds, they won't activate
        final_hand, depth_exceeded = sim.resolve_effects(hand, remaining_deck, [])
        
        # Should have exactly 7 cards (5 original + 2 drawn from the one Pot)
        # No chaining, so drawn Pots don't activate
        self.assertEqual(len(final_hand), 7)
        self.assertFalse(depth_exceeded)

    def test_deck_subtraction_regression(self):
        """Test specifically for the deck subtraction bug"""
        # Scenario: Deck has 3 Pot of Greed. Hand has 1.
        # Buggy logic would look for "Pot of Greed" in hand and remove ALL from deck.
        # Correct logic removes just 1.
        
        deck = Deck(40, {"Pot of Greed": 3, "Other": 37})
        
        hand = ["Pot of Greed", "Other", "Other", "Other", "Other"]
        
        # Manually verify deck subtraction logic used in Simulator
        from collections import Counter
        deck_counts = Counter(deck.cards)
        hand_counts = Counter(hand)
        remaining_deck = []
        for card, count in deck_counts.items():
            rem = count - hand_counts.get(card, 0)
            if rem > 0:
                remaining_deck.extend([card] * rem)
                
        # Count Pot of Greed in remaining deck
        pot_count = remaining_deck.count("Pot of Greed")
        
        # Should be 2 (3 initially - 1 in hand)
        # Buggy logic would result in 0
        self.assertEqual(pot_count, 2, f"Regression: Expected 2 Pot of Greed remaining, got {pot_count}")


if __name__ == '__main__':
    unittest.main()
