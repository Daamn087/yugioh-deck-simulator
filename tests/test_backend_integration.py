
import unittest
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from models import SimulationConfig, Requirement
from main import build_rule

class TestBackendIntegration(unittest.TestCase):
    """Test the backend API integration with AND/OR operators"""

    def test_requirement_serialization_with_and(self):
        """Test that Requirement with AND operator serializes correctly"""
        req = Requirement(card_name="Starter", min_count=1, operator='AND')
        data = req.model_dump()
        
        self.assertEqual(data['card_name'], 'Starter')
        self.assertEqual(data['min_count'], 1)
        self.assertEqual(data['operator'], 'AND')

    def test_requirement_serialization_with_or(self):
        """Test that Requirement with OR operator serializes correctly"""
        req = Requirement(card_name="Starter", min_count=1, operator='OR')
        data = req.model_dump()
        
        self.assertEqual(data['operator'], 'OR')

    def test_requirement_default_operator(self):
        """Test that Requirement defaults to AND when operator not specified"""
        req = Requirement(card_name="Starter", min_count=1)
        data = req.model_dump()
        
        self.assertEqual(data['operator'], 'AND')

    def test_simulation_config_with_operators(self):
        """Test SimulationConfig with mixed AND/OR operators"""
        config = SimulationConfig(
            deck_size=40,
            deck_contents={"Starter": 10, "Extender": 10},
            hand_size=5,
            simulations=1000,
            rules=[
                [
                    Requirement(card_name="Starter", min_count=1, operator='AND'),
                    Requirement(card_name="Extender", min_count=1, operator='OR')
                ]
            ]
        )
        
        # Verify the config is valid
        self.assertEqual(len(config.rules), 1)
        self.assertEqual(len(config.rules[0]), 2)
        self.assertEqual(config.rules[0][0].operator, 'AND')
        self.assertEqual(config.rules[0][1].operator, 'OR')

    def test_json_serialization_roundtrip(self):
        """Test that config with operators can be serialized to JSON and back"""
        original_config = {
            "deck_size": 40,
            "deck_contents": {"Starter": 10, "Extender": 10},
            "hand_size": 5,
            "simulations": 1000,
            "rules": [
                [
                    {"card_name": "Starter", "min_count": 1, "operator": "AND"},
                    {"card_name": "Extender", "min_count": 1, "operator": "OR"}
                ]
            ]
        }
        
        # Serialize to JSON
        json_str = json.dumps(original_config)
        
        # Deserialize back
        loaded_config = json.loads(json_str)
        
        # Verify operators are preserved
        self.assertEqual(loaded_config['rules'][0][0]['operator'], 'AND')
        self.assertEqual(loaded_config['rules'][0][1]['operator'], 'OR')

    def test_backward_compatibility_missing_operator(self):
        """Test that old configs without operator field still work"""
        old_config_dict = {
            "deck_size": 40,
            "deck_contents": {"Starter": 10},
            "hand_size": 5,
            "simulations": 1000,
            "rules": [
                [
                    {"card_name": "Starter", "min_count": 1}
                ]
            ]
        }
        
        # Create config from old format
        config = SimulationConfig(**old_config_dict)
        
        # Should default to AND
        self.assertEqual(config.rules[0][0].operator, 'AND')

    def test_requirement_nested_structure(self):
        """Test recursive Requirement structure can be created and dumped"""
        # (A OR B)
        nested_group = [
            Requirement(card_name="A", min_count=1, operator='OR'),
            Requirement(card_name="B", min_count=1)
        ]
        
        # Wrapper that contains the group: AND (A OR B)
        wrapper_req = Requirement(operator='AND', sub_requirements=nested_group)
        
        data = wrapper_req.model_dump()
        
        self.assertIsNone(data.get('card_name'))
        self.assertEqual(len(data['sub_requirements']), 2)
        self.assertEqual(len(data['sub_requirements']), 2)
        self.assertEqual(data['sub_requirements'][0]['card_name'], 'A')

    def test_simulation_config_validation_recursive(self):
        """Test SimulationConfig validation with nested structure from dict"""
        config_data = {
            "deck_size": 40,
            "deck_contents": {"Starter": 10},
            "hand_size": 5,
            "simulations": 100,
            "rules": [
                [
                    {"operator": "AND", "sub_requirements": [
                        {"card_name": "Starter", "min_count": 1, "operator": "AND"},
                        {"operator": "OR", "sub_requirements": [
                            {"card_name": "Extender", "min_count": 1}
                        ]}
                    ]}
                ]
            ]
        }
        config = SimulationConfig(**config_data)
        
        # Verify structure
        req = config.rules[0][0]
        self.assertIsNone(req.card_name)
        self.assertIsNotNone(req.sub_requirements)
        self.assertEqual(len(req.sub_requirements), 2)
        
        inner_group = req.sub_requirements[1]
        self.assertEqual(inner_group.operator, "OR")
        self.assertIsNotNone(inner_group.sub_requirements)

    def test_build_rule_empty_group(self):
        """Test build_rule handles empty/None correctly (returns AlwaysTrue)"""
        from collections import Counter
        rule = build_rule([])
        self.assertTrue(rule(Counter())) # Always True
        
        rule = build_rule(None)
        self.assertTrue(rule(Counter())) # Always True

        # Test nested empty group
        # A AND (Empty Group) => A AND True => A
        reqs = [
            Requirement(card_name="A", min_count=1, operator="AND"),
            Requirement(sub_requirements=[])
        ]
        rule = build_rule(reqs)
        # Should behave like A
        from collections import Counter
        self.assertTrue(rule(Counter({"A": 1})))
        self.assertFalse(rule(Counter({"B": 1})))


if __name__ == '__main__':
    unittest.main()
