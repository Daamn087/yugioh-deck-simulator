## [0.5.0] - 2026-03-15

### Added
- **Detailed Effect Tracking**: The Hand Inspector now shows exactly which cards were **drawn** and **discarded** during effect resolution.

### Fixed
- Conditional drawing cards were not correctly included in the simulation

## [0.4.1] - 2026-03-14

### Fixed
- Styling components and layout
- Non-persistent behavior of certain services


## [0.4.0] - 2026-03-14

### Added
- **Card Images**: Full support for card artwork in the Deck Builder and Hand Inspector.
- **Faster Loading**: Improved caching so decks and images load instantly after the first import.
- **Simulation Hints**: Added helpful warnings for incomplete decks or success conditions.

### Changed
- **Performance**: Optimized internal logic for a smoother experience when building decks and validating rules.

## [0.3.0] - 2026-03-13

### Added
- **Test Hand Inspector**: A powerful new modal for reviewing simulated hands.
  - Allows filtering simulated hands by specific drawn cards.
  - Added a Status filter to instantly review only 'Passing' or 'Failing' hands.
  - Added a "Show pre-effect hands" toggle to compare the initially drawn hand against the hand after resolving draw/discard effects.
- **Improved Effect Simulation Engine**:
  - The Simulation Engine now smartly determines if a hand met the success conditions *before* resolving effects.
  - Optimized the **Conditional Discard Effect** to simulate discard choices: The engine will now always prioritize discarding useless cards over dropping critical combo pieces to resolve effects.

## [0.2.1] - 2026-02-20

### Changed
- Improve icon visibility

## [0.2.0] - 2026-02-17

### Added
- Equal operator (`=`) for success conditions, allowing users to specify exact card counts in addition to the existing "equal or more" (`>=`) operator. Solves "brilliant fusion without garnet in hand" problem

## [0.1.0] - 2026-02-16

### Added
- Initial release of Yu-Gi-Oh Deck Simulator
- Deck building with card categories and subcategories
- Success condition rules with comparison operators
- Card effects simulation
- YDK file import functionality
- Deck configuration export/import
- Simulation results visualization
- AND/OR operators for success conditions
