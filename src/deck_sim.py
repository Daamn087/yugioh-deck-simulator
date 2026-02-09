
import random
from typing import List, Dict, Callable, Any
from dataclasses import dataclass
from collections import Counter

@dataclass
class SimulationResult:
    total_simulations: int
    success_count: int
    brick_count: int
    success_rate: float
    brick_rate: float

class Deck:
    def __init__(self, deck_size: int, contents: Dict[str, int]):
        """
        Initializes a deck.
        
        Args:
            deck_size: Total number of cards in the deck.
            contents: Dictionary mapping card category names to their counts.
                      Example: {"Starter": 5, "Extender": 3}
        """
        self.deck_size = deck_size
        self.contents = contents
        self.cards = self._build_deck()
        
        if len(self.cards) != deck_size:
            # We fill the rest with "blank" cards if the counts don't add up to deck_size
            # Or raise error if they exceed.
            if len(self.cards) > deck_size:
                raise ValueError(f"Card counts ({len(self.cards)}) exceed deck size ({deck_size})")
            
            # Fill remainder with "Empty" or similar if needed, or assume 'Other'
            # For this sim, typically we care about named categories. 
            # Anything not named is just "Other".
            remaining = deck_size - len(self.cards)
            self.cards.extend(["_Generic_"] * remaining)

    def _build_deck(self) -> List[str]:
        deck = []
        for name, count in self.contents.items():
            deck.extend([name] * count)
        return deck

    def draw_hand(self, hand_size: int) -> List[str]:
        """Draws a random hand of size n without replacement."""
        return random.sample(self.cards, hand_size)

class Rule:
    """
    A helper class to define success conditions naturally.
    Usage:
        req("Starter") >= 1
        req("Starter") & req("Extender")
    """
    def __init__(self, card_name: str, min_count: int = 1):
        self.card_name = card_name
        self.min_count = min_count

    def __ge__(self, count: int) -> 'Rule':
        """Allows syntax like: req('Starter') >= 2"""
        return Rule(self.card_name, count)

    def __call__(self, hand: Counter) -> bool:
        return hand[self.card_name] >= self.min_count

    def __and__(self, other: Callable[[Counter], bool]) -> 'CompositeRule':
        """Allows syntax like: req('A') & req('B')"""
        return CompositeRule(self, other, operator='AND')
    
    def __or__(self, other: Callable[[Counter], bool]) -> 'CompositeRule':
        """Allows syntax like: req('A') | req('B')"""
        return CompositeRule(self, other, operator='OR')

    def __repr__(self):
        return f"req('{self.card_name}') >= {self.min_count}"

class CompositeRule:
    def __init__(self, left, right, operator='AND'):
        self.left = left
        self.right = right
        self.operator = operator

    def __call__(self, hand: Counter) -> bool:
        if self.operator == 'OR':
            return self.left(hand) or self.right(hand)
        else:  # Default to AND
            return self.left(hand) and self.right(hand)
    
    def __and__(self, other):
        return CompositeRule(self, other, operator='AND')
    
    def __or__(self, other):
        return CompositeRule(self, other, operator='OR')

def req(card_name: str) -> Rule:
    """Short helper to create a Rule."""
    return Rule(card_name)

class Simulator:
    def __init__(self, deck: Deck, subcategory_map: Dict[str, List[str]] = None):
        """
        Initialize the simulator.
        
        Args:
            deck: The deck to simulate
            subcategory_map: Maps subcategory names to list of card names
                            e.g., {"Lunarlight Monster": ["Lunarlight Gold Leo", "Lunarlight Tiger"]}
        """
        self.deck = deck
        self.subcategory_map = subcategory_map or {}

    def check_success(self, hand: List[str], conditions: List[Callable[[Counter], bool]]) -> bool:
        """
        Checks if a hand meets ANY of the success conditions.
        Enhanced to support subcategory matching.
        
        Args:
            hand: The list of cards drawn.
            conditions: A list of functions. Each function takes a Counter of the hand 
                        and returns True if that specific condition is met.
        """
        hand_counts = Counter(hand)
        
        # Add subcategory counts
        # For each subcategory, count how many cards in hand belong to it
        for subcat, card_names in self.subcategory_map.items():
            hand_counts[subcat] = sum(hand_counts[card] for card in card_names)
        
        for condition in conditions:
            if condition(hand_counts):
                return True
        return False

    def run(self, simulations: int, hand_size: int, conditions: List[Callable[[Counter], bool]]) -> SimulationResult:
        successes = 0
        
        for _ in range(simulations):
            hand = self.deck.draw_hand(hand_size)
            if self.check_success(hand, conditions):
                successes += 1
        
        return SimulationResult(
            total_simulations=simulations,
            success_count=successes,
            brick_count=simulations - successes,
            success_rate=(successes / simulations) * 100.0,
            brick_rate=((simulations - successes) / simulations) * 100.0
        )
