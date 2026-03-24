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
        final_hand, depth_exceeded, _, _ = sim.resolve_effects(hand, remaining_deck, [])
        
        # Pot of Greed is consumed (spent to activate), then draws 2:
        # 5 original - 1 activating card + 2 drawn = 6 cards
        self.assertEqual(len(final_hand), 6)
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
        final_hand, _, _, _ = sim.resolve_effects(hand, remaining_deck, [])
        
        # Only one Vision activates (OPT). It is consumed, then draws 2:
        # 5 original - 1 activating card + 2 drawn = 6 cards
        # The second Vision copy remains in the hand but does not activate.
        self.assertEqual(len(final_hand), 6)

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
        final_hand, _, _, _ = sim.resolve_effects(hand, remaining_deck, [])
        
        # Expectation:
        # 1. Vision activates
        # 2. Draws 2 cards, checks for "Quick-Play Spell" — none found
        # 3. Discard condition fails (0 < 1 required)
        # 4. REVERTS effect (fully reverted): hand is restored to 5 cards (Vision is put back)
        # drawn cards are surfaced for display but the hand size remains 5.
        self.assertEqual(len(final_hand), 5, "Should revert to 5 cards when discard condition fails")

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
        final_hand, _, _, _ = sim.resolve_effects(hand, remaining_deck, [])
        
        # Pot of Greed is consumed (8 - 1 = 7), then draws 2 → 9 cards
        self.assertEqual(len(final_hand), 9)

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
        final_hand, depth_exceeded, _, _ = sim.resolve_effects(hand, remaining_deck, [])
        
        # Pot of Greed is consumed (5 - 1 = 4), then draws 2 → 6 cards
        # No chaining: drawn Pots don't activate
        self.assertEqual(len(final_hand), 6)
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

    def test_no_effect_resolution_when_already_success(self):
        """Regression: effects must NOT fire when the initial hand already meets the success condition."""
        from collections import Counter

        # Deck matching the reported scenario
        deck = Deck(40, {"Habakiri": 3, "Aramasa": 3, "Vision": 3, "Blank": 31})

        subcategory_map = {
            "starter": ["Habakiri", "Aramasa"],
            "quick play": ["Vision"],
        }

        vision_effect = ConditionalDiscardEffect(
            draw_count=2,
            discard_filter="quick play",
            discard_count=1,
        )
        card_effects = {"Vision": vision_effect}

        sim = Simulator(deck, subcategory_map, card_effects)

        # Hand that is already a success (has Habakiri) AND contains Vision
        hand = ["Habakiri", "Vision", "Blank", "Blank", "Blank"]
        deck_counts = Counter(deck.cards)
        hand_counts = Counter(hand)
        remaining_deck = []
        for card, count in deck_counts.items():
            rem = count - hand_counts.get(card, 0)
            if rem > 0:
                remaining_deck.extend([card] * rem)

        rule = req("starter") >= 1
        # count subcategory hits
        _orig_evaluate = sim._evaluate_hand

        success, depth_exceeded, final_hand, cards_drawn, cards_discarded = sim.check_success(
            hand, [rule], remaining_deck
        )

        self.assertTrue(success, "Hand with Habakiri should be a success")
        self.assertEqual(cards_drawn, [], "No cards should be drawn when hand is already a success")
        self.assertEqual(cards_discarded, [], "No cards should be discarded when hand is already a success")
        self.assertEqual(final_hand, hand, "final_hand should equal initial hand when effects are skipped")

    def test_vision_discard_only_shows_quickplay(self):
        """Regression: cards_discarded must contain only the filter-matching card, not the activating Vision."""
        from collections import Counter

        # Vision is in a separate 'vision' subcategory — NOT in 'quick play'.
        # Only 'Quick-Play A' is the valid discard target.
        deck = Deck(40, {"Vision": 3, "Quick-Play A": 3, "Blank": 34})

        subcategory_map = {
            "vision": ["Vision"],       # activating card's own label — not the discard filter
            "quick play": ["Quick-Play A"],  # only this type can be discarded
        }

        vision_effect = ConditionalDiscardEffect(
            draw_count=2,
            discard_filter="quick play",  # Vision is NOT in this filter
            discard_count=1,
        )
        card_effects = {"Vision": vision_effect}

        sim = Simulator(deck, subcategory_map, card_effects)

        hand = ["Vision", "Blank", "Blank", "Blank", "Blank"]
        deck_counts = Counter(deck.cards)
        hand_counts = Counter(hand)
        remaining_deck = []
        for card, count in deck_counts.items():
            rem = count - hand_counts.get(card, 0)
            if rem > 0:
                remaining_deck.extend([card] * rem)

        from deck_sim import Rule
        rule = Rule("NonExistentWinCon", 1, ">=")

        # Run many trials to hit a case where Vision draws a Quick-Play A and discards it
        found_discard_case = False
        for _ in range(300):
            final_hand, _, drawn, discarded = sim.resolve_effects(hand, remaining_deck, [rule])
            if discarded:
                found_discard_case = True
                # Vision (activating card) must NOT appear in discards
                self.assertNotIn("Vision", discarded,
                    "Vision (the activating card) must not appear in cards_discarded")
                # Only 'Quick-Play A' is a valid discard target
                for card in discarded:
                    self.assertEqual(card, "Quick-Play A",
                        f"Expected 'Quick-Play A' in discards, got: {card}")
                self.assertEqual(len(discarded), 1,
                    f"Exactly 1 card should be discarded, got: {discarded}")
                break

        self.assertTrue(found_discard_case,
            "Expected Vision to discard a Quick-Play A in at least 1 of 300 trials")
    def test_revert_returns_copies(self):
        """Test that the revert code path returns shallow copies of the original lists"""
        from deck_sim import Deck
        from card_effects import ConditionalDiscardEffect, EffectContext
        
        # Create deck and effect
        deck = Deck(40, {"Vision": 3, "Blank": 37})
        subcategory_map = {"quick play": ["NonExistent"]}
        vision_effect = ConditionalDiscardEffect(draw_count=2, discard_filter="quick play", discard_count=1)
        
        # Original lists
        hand = ["Vision", "Blank", "Blank", "Blank", "Blank"]
        remaining_deck = ["Blank"] * 35
        context = EffectContext(subcategory_map=subcategory_map, success_conditions=[])
        
        # Apply effect - will revert because discard_filter matches nothing
        result = vision_effect.apply(hand, remaining_deck, context)
        
        self.assertTrue(result.fully_reverted)
        
        # Identity check: returned lists should NOT be the same objects as the inputs
        self.assertIsNot(result.hand, hand)
        self.assertIsNot(result.remaining_deck, remaining_deck)
        
        # Mutation check: modifying the returned list should NOT affect the original list
        result.hand.append("New Card")
        self.assertNotIn("New Card", hand)
        
        result.remaining_deck.pop()
        self.assertEqual(len(remaining_deck), 35)
        
        # Verify cards_drawn is also a copy
        self.assertIsInstance(result.cards_drawn, list)
        self.assertEqual(len(result.cards_drawn), 2)
        
        # If we modify it, it shouldn't affect anything else we hold
        original_drawn = result.cards_drawn.copy()
        result.cards_drawn.append("Something Else")
        self.assertNotEqual(result.cards_drawn, original_drawn)


if __name__ == '__main__':
    unittest.main()
