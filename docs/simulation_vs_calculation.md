# Simulation vs. Calculation: Why Monte Carlo?

## 1. Mathematical Calculation (Hypergeometric Distribution)

This method calculates the exact probability of drawing $k$ successes in $n$ draws from a population of $N$ size.

### Pros:
- **Instant Results**: Takes milliseconds to calculate.
- **Exact Precision**: Returns $33.7552\%$ exactly, not $\approx 33.76\%$.

### Cons:
- **Explodes with Complexity**: Calculating "Open 1 Starter" is easy. Calculating "Open 1 Starter OR (1 Tuner AND 1 Non-Tuner)" is harder.
- **Cannot Handle "State"**: This is the dealbreaker. When you activate *Pot of Greed*, the probability of drawing a specific card *changes* because the deck size decreased and you removed cards from the pool.
- **Conditional Logic is Nightmare**: To calculate *Vision of the Radiant Typhoon* (Draw 2, then discard 1 Quick-Play if able) mathematically, you would need to sum the probabilities of:
    1. Drawing Vision + Quick-Play + X + Y + Z
    2. Drawing Vision + No Quick-Play + A + B + C -> Then drawing Quick-Play off effect
    3. Drawing Vision + No Quick-Play -> Then NOT drawing Quick-Play off effect
    
    This becomes a branching tree of thousands of equations very quickly.

## 2. Monte Carlo Simulation (Our Approach)

This method just "plays the game" millions of times and counts how many times you won.

### Pros:
- **Handles Any Logic**: If you can code it, you can simulate it.
    - "Draw 2 cards." -> Easy.
    - "If you drew a Monster, draw 1 more." -> Easy.
    - "If you have 3 Spells in grave..." -> Easy.
- **Scalable**: Adding a new feature (like Garnets or nibiru-proofing) doesn't require rewriting complex formulas, just adding a check in the `check_success` function.
- **Easy to Verify**: You can look at a specific "Hand #405" and see exactly why it failed.

### Cons:
- **Slower**: Running 1,000,000 simulations takes a few seconds (vs milliseconds).
- **Approximate**: It might say $33.76\%$ one run and $33.74\%$ the next (margin of error), though 1M simulations makes this margin tiny (~0.1%).

## Summary

We chose **Simulation** because Yu-Gi-Oh card effects drastically change the game state (deck thinning, drawing, discarding). Capturing that dynamic behavior with static math formulas is nearly impossible for a general-purpose tool.
