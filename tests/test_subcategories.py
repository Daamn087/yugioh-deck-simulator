
import unittest
import sys
import os

# Add src and backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from deck_sim import Deck, Simulator, req
from models import CardCategory

class TestSubcategories(unittest.TestCase):
    """Test the subcategory/tagging functionality"""

    def test_basic_subcategory_matching(self):
        """Test that a card with a subcategory matches requirements for that subcategory"""
        # Create deck with cards that have subcategories
        deck = Deck(40, {"Lunalight Gold Leo": 3, "Lunalight Tiger": 3, "Polymerization": 2})
        
        # Build subcategory map: "Lunalight Monster" includes both Gold Leo and Tiger
        subcategory_map = {
            "Lunalight Monster": ["Lunalight Gold Leo", "Lunalight Tiger"]
        }
        
        sim = Simulator(deck, subcategory_map)
        
        # Test: Hand with 2 Lunalight monsters should match requirement for "Lunalight Monster >= 2"
        hand = ["Lunalight Gold Leo", "Lunalight Tiger", "Other", "Other", "Other"]
        rule = req("Lunalight Monster") >= 2
        success, _ = sim.check_success(hand, [rule])
        self.assertTrue(success)
        
        # Test: Hand with only 1 Lunalight monster should not match
        hand = ["Lunalight Gold Leo", "Other", "Other", "Other", "Other"]
        success, _ = sim.check_success(hand, [rule])
        self.assertFalse(success)

    def test_multiple_subcategories_per_card(self):
        """Test that a card can belong to multiple subcategories"""
        deck = Deck(40, {"Lunalight Gold Leo": 3})
        
        # Gold Leo belongs to both "Starter" and "Lunalight Monster" subcategories
        subcategory_map = {
            "Starter": ["Lunalight Gold Leo"],
            "Lunalight Monster": ["Lunalight Gold Leo"]
        }
        
        sim = Simulator(deck, subcategory_map)
        
        # Test: One Gold Leo should match both subcategory requirements
        hand = ["Lunalight Gold Leo", "Other", "Other", "Other", "Other"]
        
        starter_rule = req("Starter") >= 1
        lunalight_rule = req("Lunalight Monster") >= 1
        
        success1, _ = sim.check_success(hand, [starter_rule])
        self.assertTrue(success1)
        success2, _ = sim.check_success(hand, [lunalight_rule])
        self.assertTrue(success2)

    def test_subcategory_count_aggregation(self):
        """Test that multiple different cards with the same subcategory are counted together"""
        deck = Deck(40, {
            "Lunalight Gold Leo": 3,
            "Lunalight Tiger": 3,
            "Lunalight Wolf": 3
        })
        
        subcategory_map = {
            "Lunalight Monster": ["Lunalight Gold Leo", "Lunalight Tiger", "Lunalight Wolf"]
        }
        
        sim = Simulator(deck, subcategory_map)
        
        # Test: 3 different Lunalight cards should count as 3 for the subcategory
        hand = ["Lunalight Gold Leo", "Lunalight Tiger", "Lunalight Wolf", "Other", "Other"]
        rule = req("Lunalight Monster") >= 3
        success, _ = sim.check_success(hand, [rule])
        self.assertTrue(success)

    def test_mixed_category_and_subcategory_conditions(self):
        """Test conditions that mix regular categories and subcategories"""
        deck = Deck(40, {
            "Polymerization": 2,
            "Lunalight Gold Leo": 3,
            "Lunalight Tiger": 3
        })
        
        subcategory_map = {
            "Lunalight Monster": ["Lunalight Gold Leo", "Lunalight Tiger"]
        }
        
        sim = Simulator(deck, subcategory_map)
        
        # Test: "1 Polymerization AND 2 Lunalight Monster"
        rule = (req("Polymerization") >= 1) & (req("Lunalight Monster") >= 2)
        
        # Should succeed with Poly + 2 Lunalight cards
        hand = ["Polymerization", "Lunalight Gold Leo", "Lunalight Tiger", "Other", "Other"]
        success, _ = sim.check_success(hand, [rule])
        self.assertTrue(success)
        
        # Should fail with only Poly
        hand = ["Polymerization", "Other", "Other", "Other", "Other"]
        success, _ = sim.check_success(hand, [rule])
        self.assertFalse(success)
        
        # Should fail with only Lunalight cards
        hand = ["Lunalight Gold Leo", "Lunalight Tiger", "Other", "Other", "Other"]
        success, _ = sim.check_success(hand, [rule])
        self.assertFalse(success)

    def test_subcategory_with_or_operator(self):
        """Test OR operator with subcategories"""
        deck = Deck(40, {
            "Lunalight Gold Leo": 3,
            "Lunalight Tiger": 3,
            "Handtrap": 3
        })
        
        subcategory_map = {
            "Lunalight Monster": ["Lunalight Gold Leo", "Lunalight Tiger"]
        }
        
        sim = Simulator(deck, subcategory_map)
        
        # Test: "1 Lunalight Monster OR 1 Handtrap"
        rule = (req("Lunalight Monster") >= 1) | (req("Handtrap") >= 1)
        
        # Should succeed with Lunalight
        hand = ["Lunalight Gold Leo", "Other", "Other", "Other", "Other"]
        success, _ = sim.check_success(hand, [rule])
        self.assertTrue(success)
        
        # Should succeed with Handtrap
        hand = ["Handtrap", "Other", "Other", "Other", "Other"]
        success, _ = sim.check_success(hand, [rule])
        self.assertTrue(success)
        
        # Should succeed with both
        hand = ["Lunalight Gold Leo", "Handtrap", "Other", "Other", "Other"]
        success, _ = sim.check_success(hand, [rule])
        self.assertTrue(success)

    def test_empty_subcategory_map(self):
        """Test that simulator works correctly with no subcategories (backward compatibility)"""
        deck = Deck(40, {"Starter": 10, "Extender": 10})
        sim = Simulator(deck, {})  # Empty subcategory map
        
        # Regular category matching should still work
        hand = ["Starter", "Extender", "Other", "Other", "Other"]
        rule = (req("Starter") >= 1) & (req("Extender") >= 1)
        success, _ = sim.check_success(hand, [rule])
        self.assertTrue(success)

    def test_subcategory_simulation_probability(self):
        """Test that subcategories work correctly in full simulations"""
        deck = Deck(40, {
            "Lunalight Gold Leo": 3,
            "Lunalight Tiger": 3,
            "Polymerization": 2
        })
        
        subcategory_map = {
            "Lunalight Monster": ["Lunalight Gold Leo", "Lunalight Tiger"]
        }
        
        sim = Simulator(deck, subcategory_map)
        
        # Run simulation: "1 Polymerization AND 2 Lunalight Monster"
        rule = (req("Polymerization") >= 1) & (req("Lunalight Monster") >= 2)
        result = sim.run(10000, 5, [rule])
        
        # Should have some success rate (not 0% or 100%)
        self.assertGreater(result.success_rate, 0)
        self.assertLess(result.success_rate, 100)
        print(f"\n[Test] Poly + 2 Lunalight success rate: {result.success_rate:.2f}%")

    def test_card_category_model(self):
        """Test the CardCategory model from backend"""
        # Test with subcategories
        cat1 = CardCategory(name="Lunalight Gold Leo", count=3, subcategories=["Starter", "Lunalight Monster"])
        self.assertEqual(cat1.name, "Lunalight Gold Leo")
        self.assertEqual(cat1.count, 3)
        self.assertEqual(len(cat1.subcategories), 2)
        
        # Test with empty subcategories (default)
        cat2 = CardCategory(name="Polymerization", count=2)
        self.assertEqual(len(cat2.subcategories), 0)


if __name__ == '__main__':
    unittest.main()
