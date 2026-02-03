
from pydantic import BaseModel
from typing import List, Dict

class Requirement(BaseModel):
    card_name: str
    min_count: int

# A SuccessCondition is a list of Requirements (AND logic)
# E.g. [Req(A), Req(B)] means "A AND B"
class SuccessCondition(BaseModel):
    requirements: List[Requirement]

class SimulationConfig(BaseModel):
    deck_size: int
    deck_contents: Dict[str, int]
    hand_size: int
    simulations: int
    # A list of conditions (OR logic). Ideally "SuccessCondition" objects.
    # [[A], [B, C]] means (A) OR (B AND C)
    rules: List[List[Requirement]] 

class SimulationResult(BaseModel):
    success_rate: float
    brick_rate: float
    success_count: int
    brick_count: int
    time_taken: float
