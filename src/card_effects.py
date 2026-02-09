"""
Card Effect System for Yu-Gi-Oh Deck Simulator

This module defines the card effect type system and base classes for implementing
dynamic card effects that can draw additional cards, discard cards, and modify
the game state during simulation.

All cards are treated as once-per-turn (OPT) for simplicity.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
from collections import Counter


@dataclass
class EffectContext:
    """Context information available to card effects during resolution"""
    subcategory_map: Dict[str, List[str]]  # Maps subcategory names to card names
    success_conditions: List[Any]  # Success condition functions
    max_depth: int = 10  # Maximum effect resolution depth
    current_depth: int = 0  # Current recursion depth


@dataclass
class EffectResult:
    """Result of applying a card effect"""
    hand: List[str]  # Modified hand after effect
    remaining_deck: List[str]  # Remaining deck after drawing
    depth_exceeded: bool = False  # Whether max depth was reached
    cards_drawn: List[str] = None  # Cards that were drawn by this effect
    
    def __post_init__(self):
        if self.cards_drawn is None:
            self.cards_drawn = []


class CardEffect(ABC):
    """
    Abstract base class for card effects.
    All cards are treated as once-per-turn (OPT) for simplicity.
    """
    
    @abstractmethod
    def apply(self, hand: List[str], remaining_deck: List[str], context: EffectContext) -> EffectResult:
        """
        Apply the card effect.
        
        Args:
            hand: Current hand of cards
            remaining_deck: Cards still in the deck
            context: Effect context with additional information
            
        Returns:
            EffectResult with updated hand and deck
        """
        pass
    
    def can_activate(self, hand: List[str], remaining_deck: List[str]) -> bool:
        """
        Check if this effect can be activated given the current game state.
        Default implementation always returns True.
        
        Args:
            hand: Current hand
            remaining_deck: Remaining deck
            
        Returns:
            True if the effect can activate, False otherwise
        """
        return True


class DrawEffect(CardEffect):
    """
    Effect that draws a specified number of cards from the deck.
    Example: Pot of Greed (draw 2 cards)
    """
    
    def __init__(self, count: int):
        """
        Initialize a draw effect.
        
        Args:
            count: Number of cards to draw
        """
        self.count = count
    
    def can_activate(self, hand: List[str], remaining_deck: List[str]) -> bool:
        """Check if we have enough cards in deck to draw"""
        return len(remaining_deck) >= self.count
    
    def apply(self, hand: List[str], remaining_deck: List[str], context: EffectContext) -> EffectResult:
        """
        Draw cards from the deck and add them to the hand.
        
        Args:
            hand: Current hand of cards
            remaining_deck: Cards still in the deck
            context: Effect context
            
        Returns:
            EffectResult with updated hand and deck
        """
        # Check if we can draw
        if not self.can_activate(hand, remaining_deck):
            # Can't draw enough cards, return unchanged state
            return EffectResult(
                hand=hand.copy(),
                remaining_deck=remaining_deck.copy(),
                cards_drawn=[]
            )
        
        # Draw cards from the deck
        new_hand = hand.copy()
        new_deck = remaining_deck.copy()
        drawn_cards = []
        
        for _ in range(self.count):
            if new_deck:
                # Draw a random card (simulate drawing from shuffled deck)
                import random
                card_index = random.randint(0, len(new_deck) - 1)
                drawn_card = new_deck.pop(card_index)
                new_hand.append(drawn_card)
                drawn_cards.append(drawn_card)
        
        return EffectResult(
            hand=new_hand,
            remaining_deck=new_deck,
            cards_drawn=drawn_cards
        )


class ConditionalDiscardEffect(CardEffect):
    """
    Effect that draws cards and then discards cards matching a filter.
    Example: Vision of the Radiant Typhoon (draw 2, discard 1 Quick-Play Spell if drawn)
    """
    
    def __init__(self, draw_count: int, discard_filter: str, discard_count: int = 1):
        """
        Initialize a conditional discard effect.
        
        Args:
            draw_count: Number of cards to draw
            discard_filter: Subcategory name to filter for discard (e.g., "Quick-Play Spell")
            discard_count: Number of matching cards to discard
        """
        self.draw_count = draw_count
        self.discard_filter = discard_filter
        self.discard_count = discard_count
    
    def can_activate(self, hand: List[str], remaining_deck: List[str]) -> bool:
        """Check if we have enough cards in deck to draw"""
        return len(remaining_deck) >= self.draw_count
    
    def apply(self, hand: List[str], remaining_deck: List[str], context: EffectContext) -> EffectResult:
        """
        Draw cards, then discard cards matching the filter.
        
        Args:
            hand: Current hand of cards
            remaining_deck: Cards still in the deck
            context: Effect context (contains subcategory_map)
            
        Returns:
            EffectResult with updated hand and deck
        """
        # First, draw cards using DrawEffect
        draw_effect = DrawEffect(self.draw_count)
        draw_result = draw_effect.apply(hand, remaining_deck, context)
        
        # Now check if any drawn cards match the discard filter
        new_hand = draw_result.hand.copy()
        
        # Get cards that match the discard filter (subcategory)
        matching_cards = []
        if self.discard_filter in context.subcategory_map:
            # Cards in this subcategory
            filter_cards = context.subcategory_map[self.discard_filter]
            # Find which of these are in our hand
            matching_cards = [card for card in new_hand if card in filter_cards]
        
        # Discard up to discard_count matching cards
        discarded = 0
        for card in matching_cards:
            if discarded >= self.discard_count:
                break
            if card in new_hand:
                new_hand.remove(card)
                discarded += 1
        
        # If we failed to discard the required number of cards, the effect fails
        # We revert to the state before drawing (simulating that the condition could not be met)
        if discarded < self.discard_count:
            return EffectResult(
                hand=hand,
                remaining_deck=remaining_deck,
                cards_drawn=[]
            )
            
        return EffectResult(
            hand=new_hand,
            remaining_deck=draw_result.remaining_deck,
            cards_drawn=draw_result.cards_drawn
        )


def create_effect_from_definition(effect_def: Dict[str, Any]) -> CardEffect:
    """
    Factory function to create CardEffect instances from dictionary definitions.
    All cards are treated as once-per-turn (OPT).
    
    Args:
        effect_def: Dictionary with 'effect_type' and 'parameters' keys
        
    Returns:
        CardEffect instance
        
    Raises:
        ValueError: If effect_type is unknown
    """
    effect_type = effect_def.get('effect_type')
    params = effect_def.get('parameters', {})
    
    if effect_type == 'draw':
        return DrawEffect(count=params.get('count', 1))
    elif effect_type == 'conditional_discard':
        return ConditionalDiscardEffect(
            draw_count=params.get('draw_count', 1),
            discard_filter=params.get('discard_filter', ''),
            discard_count=params.get('discard_count', 1)
        )
    else:
        raise ValueError(f"Unknown effect type: {effect_type}")
