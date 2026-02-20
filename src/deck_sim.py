
import random
from typing import List, Dict, Callable, Any, Optional
from dataclasses import dataclass, field
from collections import Counter
from card_effects import CardEffect, EffectContext, create_effect_from_definition

@dataclass
class SimulationResult:
    total_simulations: int
    success_count: int
    brick_count: int
    success_rate: float
    brick_rate: float
    max_depth_reached_count: int = 0  # How many simulations hit max effect depth
    warnings: List[str] = field(default_factory=list)  # User-facing warnings

class Deck:
    def __init__(self, deck_size: int, contents: Dict[str, int]):
        """
        Initializes a deck.
        
        Args:
            deck_size: Total number of cards in the deck.
            contents: Dictionary mapping card category names to their counts.
                      Example: {"Starter": 5, "Extender": 3}
        """
        self.contents = contents
        self.cards = self._build_deck()
        
        if len(self.cards) != deck_size:
            # If card counts exceed deck_size, use actual count as deck_size
            if len(self.cards) > deck_size:
                self.deck_size = len(self.cards)
            else:
                # Fill remainder with "Empty" or similar if needed, or assume 'Other'
                # For this sim, typically we care about named categories. 
                # Anything not named is just "Other".
                remaining = deck_size - len(self.cards)
                self.cards.extend(["_Generic_"] * remaining)
                self.deck_size = deck_size
        else:
            self.deck_size = deck_size

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
        Rule("Starter", 0, '==')  # Exactly 0 (anti-combo) - created by build_rule
        req("Starter") & req("Extender")
    """
    def __init__(self, card_name: str, min_count: int = 1, comparison: str = '>='):
        self.card_name = card_name
        self.min_count = min_count
        self.comparison = comparison

    def __ge__(self, count: int) -> 'Rule':
        """Allows syntax like: req('Starter') >= 2"""
        return Rule(self.card_name, count, '>=')

    def __call__(self, hand: Counter) -> bool:
        if self.comparison == '==':
            return hand[self.card_name] == self.min_count
        else:  # Default to '>='
            return hand[self.card_name] >= self.min_count

    def __and__(self, other: Callable[[Counter], bool]) -> 'CompositeRule':
        """Allows syntax like: req('A') & req('B')"""
        return CompositeRule(self, other, operator='AND')
    
    def __or__(self, other: Callable[[Counter], bool]) -> 'CompositeRule':
        """Allows syntax like: req('A') | req('B')"""
        return CompositeRule(self, other, operator='OR')

    def __repr__(self):
        return f"req('{self.card_name}') {self.comparison} {self.min_count}"
    
    def __hash__(self):
        """Make Rule hashable to avoid equality comparison issues"""
        return hash((self.card_name, self.min_count, self.comparison))

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
    def __init__(self, deck: Deck, subcategory_map: Dict[str, List[str]] = None, 
                 card_effects: Dict[str, CardEffect] = None):
        """
        Initialize the simulator.
        
        Args:
            deck: The deck to simulate
            subcategory_map: Maps subcategory names to list of card names
                            e.g., {"Lunalight Monster": ["Lunalight Gold Leo", "Lunalight Tiger"]}
            card_effects: Maps card names to their effects
                         e.g., {"Pot of Greed": DrawEffect(count=2, once_per_turn=False)}
        """
        self.deck = deck
        self.subcategory_map = subcategory_map or {}
        self.card_effects = card_effects or {}
        # Pre-calculate deck counts for performance
        self.deck_counts = Counter(self.deck.cards)

    def resolve_effects(self, hand: List[str], remaining_deck: List[str], 
                       conditions: List[Callable[[Counter], bool]], max_depth: int = 10) -> tuple[List[str], bool]:
        """
        Resolve all card effects in the starting hand (single pass only).
        Cards drawn by effects do NOT activate their effects.
        All cards are treated as once-per-turn (OPT).
        
        Args:
            hand: Initial hand drawn
            remaining_deck: Cards still in deck (for drawing)
            conditions: Success conditions (for context)
            max_depth: Unused, kept for API compatibility
        
        Returns:
            Tuple of (final_hand, depth_exceeded) - depth_exceeded is always False
        """
        current_hand = hand.copy()
        current_deck = remaining_deck.copy()
        
        # Track which cards have already activated (OPT)
        activated_cards = set()
        
        # Find all cards with effects in the STARTING hand only
        cards_with_effects = [card for card in hand if card in self.card_effects]
        
        # PHASE 1: Apply all draw effects first (simultaneous resolution)
        # This ensures all cards are drawn before any conditional effects check the hand
        for card_name in set(cards_with_effects):
            # Skip if already activated (OPT)
            if card_name in activated_cards:
                continue
            
            effect = self.card_effects[card_name]
            
            # Only process DrawEffect in this phase
            from card_effects import DrawEffect
            if not isinstance(effect, DrawEffect):
                continue
            
            # Create effect context
            context = EffectContext(
                subcategory_map=self.subcategory_map,
                success_conditions=conditions,
                max_depth=max_depth,
                current_depth=0
            )
            
            # Check if effect can activate
            if not effect.can_activate(current_hand, current_deck):
                continue
            
            # Apply the draw effect
            result = effect.apply(current_hand, current_deck, context)
            current_hand = result.hand
            current_deck = result.remaining_deck
            activated_cards.add(card_name)
        
        # PHASE 2: Apply all conditional/discard effects on the final hand
        # This ensures discards check the hand AFTER all draws are complete
        for card_name in set(cards_with_effects):
            # Skip if already activated (OPT)
            if card_name in activated_cards:
                continue
            
            effect = self.card_effects[card_name]
            
            # Only process non-DrawEffect in this phase
            from card_effects import DrawEffect
            if isinstance(effect, DrawEffect):
                continue
            
            # Create effect context
            context = EffectContext(
                subcategory_map=self.subcategory_map,
                success_conditions=conditions,
                max_depth=max_depth,
                current_depth=0
            )
            
            # Check if effect can activate
            if not effect.can_activate(current_hand, current_deck):
                continue
            
            # Apply the conditional effect
            result = effect.apply(current_hand, current_deck, context)
            current_hand = result.hand
            current_deck = result.remaining_deck
            activated_cards.add(card_name)
        
        # Never exceed depth with single-pass resolution
        return current_hand, False

    def check_success(self, hand: List[str], conditions: List[Callable[[Counter], bool]], 
                     remaining_deck: Optional[List[str]] = None) -> tuple[bool, bool]:
        """
        Checks if a hand meets ANY of the success conditions.
        Enhanced to support subcategory matching and card effects.
        
        Args:
            hand: The list of cards drawn.
            conditions: A list of functions. Each function takes a Counter of the hand 
                        and returns True if that specific condition is met.
            remaining_deck: Cards still in deck (for effect resolution). If None, no effects are resolved.
        
        Returns:
            Tuple of (success, depth_exceeded)
        """
        # Resolve effects if we have a deck and effects are defined
        depth_exceeded = False
        final_hand = hand
        
        if remaining_deck is not None and self.card_effects:
            final_hand, depth_exceeded = self.resolve_effects(hand, remaining_deck, conditions)
        
        # Count cards in final hand
        hand_counts = Counter(final_hand)
        
        # Add subcategory counts
        # For each subcategory, count how many cards in hand belong to it
        for subcat, card_names in self.subcategory_map.items():
            hand_counts[subcat] = sum(hand_counts[card] for card in card_names)
        
        # Check conditions
        success = False
        for condition in conditions:
            if condition(hand_counts):
                success = True
                break
        
        return success, depth_exceeded

    def run(self, simulations: int, hand_size: int, conditions: List[Callable[[Counter], bool]]) -> SimulationResult:
        successes = 0
        max_depth_count = 0
        
        for _ in range(simulations):
            hand = self.deck.draw_hand(hand_size)
            
            # Only calculate remaining deck if we actually have effects to resolve
            remaining_deck = None
            if self.card_effects:
                # Calculate remaining deck correctly by subtracting hand counts
                hand_counts = Counter(hand)
                remaining_deck = []
                for card, count in self.deck_counts.items():
                    rem = count - hand_counts.get(card, 0)
                    if rem > 0:
                        remaining_deck.extend([card] * rem)
            
            # Check success with effect resolution
            success, depth_exceeded = self.check_success(hand, conditions, remaining_deck)
            
            if success:
                successes += 1
            
            if depth_exceeded:
                max_depth_count += 1
        
        # Build warnings
        warnings = []
        if max_depth_count > 0:
            warnings.append(f"Max effect depth reached in {max_depth_count} simulation(s). "
                          f"This may indicate infinite loops in your card effect definitions.")
        
        return SimulationResult(
            total_simulations=simulations,
            success_count=successes,
            brick_count=simulations - successes,
            success_rate=(successes / simulations) * 100.0,
            brick_rate=((simulations - successes) / simulations) * 100.0,
            max_depth_reached_count=max_depth_count,
            warnings=warnings
        )
