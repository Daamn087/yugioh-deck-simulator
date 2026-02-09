
import unittest
import sys
import os

# Add src and backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from deck_sim import Deck, Simulator, req
from models import Requirement

class TestOperatorLogic(unittest.TestCase):
    """Test the AND/OR operator functionality in success conditions"""

    def setUp(self):
        """Set up a basic deck for testing"""
        self.deck = Deck(40, {"Starter": 10, "Extender": 10, "Handtrap": 10})
        self.sim = Simulator(self.deck)

    def test_and_operator_basic(self):
        """Test basic AND operator: Starter >= 1 AND Extender >= 1"""
        rule = (req("Starter") >= 1) & (req("Extender") >= 1)
        
        # Should succeed with both
        success, _ = self.sim.check_success(["Starter", "Extender", "Other"], [rule])
        self.assertTrue(success)
        
        # Should fail with only Starter
        success, _ = self.sim.check_success(["Starter", "Other", "Other"], [rule])
        self.assertFalse(success)
        
        # Should fail with only Extender
        success, _ = self.sim.check_success(["Extender", "Other", "Other"], [rule])
        self.assertFalse(success)

    def test_or_operator_basic(self):
        """Test basic OR operator: Starter >= 1 OR Extender >= 1"""
        rule = (req("Starter") >= 1) | (req("Extender") >= 1)
        
        # Should succeed with both
        success, _ = self.sim.check_success(["Starter", "Extender", "Other"], [rule])
        self.assertTrue(success)
        
        # Should succeed with only Starter
        success, _ = self.sim.check_success(["Starter", "Other", "Other"], [rule])
        self.assertTrue(success)
        
        # Should succeed with only Extender
        success, _ = self.sim.check_success(["Extender", "Other", "Other"], [rule])
        self.assertTrue(success)
        
        # Should fail with neither
        success, _ = self.sim.check_success(["Other", "Other", "Other"], [rule])
        self.assertFalse(success)

    def test_mixed_and_or_operators(self):
        """Test mixed operators: Starter >= 1 AND (Extender >= 1 OR Handtrap >= 1)"""
        # This requires Starter AND at least one of (Extender OR Handtrap)
        rule = (req("Starter") >= 1) & ((req("Extender") >= 1) | (req("Handtrap") >= 1))
        
        # Should succeed with Starter + Extender
        success, _ = self.sim.check_success(["Starter", "Extender", "Other"], [rule])
        self.assertTrue(success)
        
        # Should succeed with Starter + Handtrap
        success, _ = self.sim.check_success(["Starter", "Handtrap", "Other"], [rule])
        self.assertTrue(success)
        
        # Should succeed with all three
        success, _ = self.sim.check_success(["Starter", "Extender", "Handtrap"], [rule])
        self.assertTrue(success)
        
        # Should fail with only Starter
        success, _ = self.sim.check_success(["Starter", "Other", "Other"], [rule])
        self.assertFalse(success)
        
        # Should fail with only Extender and Handtrap (no Starter)
        success, _ = self.sim.check_success(["Extender", "Handtrap", "Other"], [rule])
        self.assertFalse(success)

    def test_complex_or_chain(self):
        """Test chaining multiple OR operators: A >= 1 OR B >= 1 OR C >= 1"""
        rule = (req("Starter") >= 1) | (req("Extender") >= 1) | (req("Handtrap") >= 1)
        
        # Should succeed with any one
        success, _ = self.sim.check_success(["Starter", "Other", "Other"], [rule])
        self.assertTrue(success)
        success, _ = self.sim.check_success(["Extender", "Other", "Other"], [rule])
        self.assertTrue(success)
        success, _ = self.sim.check_success(["Handtrap", "Other", "Other"], [rule])
        self.assertTrue(success)
        
        # Should fail with none
        success, _ = self.sim.check_success(["Other", "Other", "Other"], [rule])
        self.assertFalse(success)

    def test_backend_requirement_model(self):
        """Test that Requirement model defaults to AND operator"""
        req1 = Requirement(card_name="Starter", min_count=1)
        self.assertEqual(req1.operator, 'AND')
        
        req2 = Requirement(card_name="Extender", min_count=1, operator='OR')
        self.assertEqual(req2.operator, 'OR')

    def test_simulation_with_or_operator(self):
        """Test full simulation with OR operator has higher success rate than AND"""
        # Create a deck with limited cards
        deck = Deck(40, {"Starter": 3, "Extender": 3})
        sim = Simulator(deck)
        
        # AND condition: both required (lower success rate)
        and_rule = (req("Starter") >= 1) & (req("Extender") >= 1)
        and_result = sim.run(10000, 5, [and_rule])
        
        # OR condition: either one works (higher success rate)
        or_rule = (req("Starter") >= 1) | (req("Extender") >= 1)
        or_result = sim.run(10000, 5, [or_rule])
        
        # OR should have significantly higher success rate
        self.assertGreater(or_result.success_rate, and_result.success_rate)
        print(f"\n[Test] AND success rate: {and_result.success_rate:.2f}%")
        print(f"[Test] OR success rate: {or_result.success_rate:.2f}%")

    def test_backward_compatibility(self):
        """Test that missing operator field defaults to AND"""
        # Simulate old config without operator field
        req1 = Requirement(card_name="Starter", min_count=1)
        req2 = Requirement(card_name="Extender", min_count=1)
        
        # Both should default to AND
        self.assertEqual(req1.operator, 'AND')
        self.assertEqual(req2.operator, 'AND')


if __name__ == '__main__':
    unittest.main()
