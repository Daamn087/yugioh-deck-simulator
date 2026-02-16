
import unittest
from collections import Counter
import sys
import os

# Add src to path so we can import deck_sim
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from deck_sim import Deck, Simulator, req

class TestDeckSimulator(unittest.TestCase):

    def test_deck_composition(self):
        contents = {"Starter": 10, "Extender": 5}
        # Total desired 20, so 5 should be empty/other
        deck = Deck(20, contents)
        self.assertEqual(len(deck.cards), 20)
        self.assertEqual(deck.cards.count("Starter"), 10)
        self.assertEqual(deck.cards.count("Extender"), 5)
        self.assertEqual(deck.cards.count("_Generic_"), 5)

    def test_deck_too_many_cards(self):
        # Verify that when cards exceed deck size, the deck size is adjusted
        contents = {"Starter": 41}
        deck = Deck(40, contents)
        # Deck size should be adjusted to 41
        self.assertEqual(deck.deck_size, 41)
        self.assertEqual(len(deck.cards), 41)

    def test_draw_hand_size(self):
        deck = Deck(40, {"Starter": 40})
        hand = deck.draw_hand(5)
        self.assertEqual(len(hand), 5)

    def test_100_percent_consistency(self):
        # 40 cards, all starters. Drawing 5. Should be 100% success for "at least 1 starter"
        deck = Deck(40, {"Starter": 40})
        sim = Simulator(deck)
        result = sim.run(1000, 5, [lambda h: h["Starter"] >= 1])
        self.assertEqual(result.success_rate, 100.0)

    def test_0_percent_consistency(self):
        # 40 cards, 0 starters.
        deck = Deck(40, {"Brick": 40})
        sim = Simulator(deck)
        result = sim.run(1000, 5, [lambda h: h["Starter"] >= 1])
        self.assertEqual(result.success_rate, 0.0)

    def test_complex_condition(self):
        # We manually check the logic function
        deck = Deck(40, {}) # irrelevant for this check
        sim = Simulator(deck)
        
        # Condition: 1 Starter AND 1 Extender
        condition = lambda h: h["Starter"] >= 1 and h["Extender"] >= 1
        
        hand_success = ["Starter", "Extender", "Brick", "Brick", "Brick"]
        success, _ = sim.check_success(hand_success, [condition])
        self.assertTrue(success)
        
        hand_fail = ["Starter", "Starter", "Brick", "Brick", "Brick"]
        success, _ = sim.check_success(hand_fail, [condition])
        self.assertFalse(success)

    def test_dsl_syntax(self):
        # Verify the Rule DSL works as expected
        deck = Deck(40, {})
        sim = Simulator(deck)
        
        # 1. Simple Requirement: req("Starter")
        rule1 = req("Starter")
        success, _ = sim.check_success(["Starter"], [rule1])
        self.assertTrue(success)
        success, _ = sim.check_success(["Other"], [rule1])
        self.assertFalse(success)
        
        # 2. Count Requirement: req("Starter") >= 2
        rule2 = req("Starter") >= 2
        success, _ = sim.check_success(["Starter", "Starter"], [rule2])
        self.assertTrue(success)
        success, _ = sim.check_success(["Starter"], [rule2])
        self.assertFalse(success)

        rule3 = req("A") & req("B")
        success, _ = sim.check_success(["A", "B"], [rule3])
        self.assertTrue(success)
        success, _ = sim.check_success(["A"], [rule3])
        self.assertFalse(success)

    def test_3_of_probability(self):
        """
        Verifies that opening at least 1 copy of a 3-of in a 40 card deck (5 card hand)
        is approximately 33.76%. We test for a range of 33.0% to 34.5%.
        """
        # Dictionary of Card Category: Quantity
        # 3 Ash Blossoms, 37 Others
        contents = {"Ash Blossom": 3} 
        
        deck = Deck(40, contents)
        sim = Simulator(deck)
        
        # Check rule: At least 1 Ash Blossom
        # Run 50,000 simulations for speed/accuracy balance
        result = sim.run(50000, 5, [req("Ash Blossom")])
        
        print(f"\n[Test] 3-of Probability: {result.success_rate:.2f}% (Expected ~33.8%)")
        self.assertTrue(33.0 <= result.success_rate <= 34.5, 
                        f"Expected rate between 33.0 and 34.5, got {result.success_rate}")


if __name__ == '__main__':
    unittest.main()
