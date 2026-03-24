
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class Requirement(BaseModel):
    card_name: Optional[str] = None # Optional now, for groups
    min_count: int = 1
    operator: str = 'AND'
    comparison_operator: str = '>='  # '>=' (at least) or '=' (exactly)
    sub_requirements: Optional[List['Requirement']] = None

# A SuccessCondition is a list of Requirements (AND logic)
# E.g. [Req(A), Req(B)] means "A AND B"
class SuccessCondition(BaseModel):
    requirements: List[Requirement]

class CardCategory(BaseModel):
    """Represents a card category with optional subcategories/tags"""
    name: str
    count: int
    subcategories: List[str] = []  # Tags like "Lunalight Monster", "Fusion Material"

class CardEffectDefinition(BaseModel):
    """Defines an effect for a specific card. All cards are once-per-turn (OPT)."""
    card_name: str
    effect_type: str  # "draw", "conditional_discard", etc.
    parameters: Dict[str, Any]  # Effect-specific parameters

class SimulationConfig(BaseModel):
    deck_size: int
    deck_contents: Dict[str, int]  # Keep for backward compatibility
    card_categories: Optional[List[CardCategory]] = None  # New field with subcategory support
    hand_size: int
    simulations: int
    # A list of conditions (OR logic). Ideally "SuccessCondition" objects.
    # [[A], [B, C]] means (A) OR (B AND C)
    rules: List[List[Requirement]]
    card_effects: Optional[List[CardEffectDefinition]] = []  # Card effects definitions
    record_hands: bool = False  # Opt-in: store individual hand records (capped at 10 000)

class HandRecord(BaseModel):
    """Record of a single simulated hand - returned when record_hands=True."""
    initial_hand: List[str]  # Cards as originally drawn
    final_hand: List[str]    # Cards after effect resolution
    cards_drawn: List[str]   # Cards added by effects
    cards_discarded: List[str] # Cards removed by effects
    success: bool            # Whether the hand met any success condition

class SimulationResult(BaseModel):
    success_rate: float
    brick_rate: float
    success_count: int
    brick_count: int
    time_taken: float
    max_depth_reached_count: int = 0  # How many simulations hit max effect depth
    warnings: List[str] = []  # User-facing warnings
    hand_records: List[HandRecord] = []  # Individual hand records (only when record_hands=True)

class ResolveCardsRequest(BaseModel):
    passcodes: List[str]

class ResolveCardsResponse(BaseModel):
    # Mapping of passcode to card info
    resolved_cards: Dict[str, Dict[str, Any]]

# For Pydantic v1 compatibility with recursive models
Requirement.update_forward_refs()
