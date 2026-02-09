
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class Requirement(BaseModel):
    card_name: str
    min_count: int
    operator: str = 'AND'  # Operator to use after this requirement (AND/OR)

# A SuccessCondition is a list of Requirements (AND logic)
# E.g. [Req(A), Req(B)] means "A AND B"
class SuccessCondition(BaseModel):
    requirements: List[Requirement]

class CardCategory(BaseModel):
    """Represents a card category with optional subcategories/tags"""
    name: str
    count: int
    subcategories: List[str] = []  # Tags like "Lunarlight Monster", "Fusion Material"

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

class SimulationResult(BaseModel):
    success_rate: float
    brick_rate: float
    success_count: int
    brick_count: int
    time_taken: float
    max_depth_reached_count: int = 0  # How many simulations hit max effect depth
    warnings: List[str] = []  # User-facing warnings
