# Automaton 

This repository provides an implementation for solving parity games. It includes functionality for loading HOA files, computing attractors, subgames and model checking and exporting automata in DOT format for visualization.

## Classes

### 1. `trans_set`
A helper class for managing and representing transitions in an automaton.

- **Attributes**:
  - `set`: A set to store transitions as tuples `(source, guard, destination)`.
  - `dict`: A dictionary for encoding Boolean formulas.

- **Methods**:
  - `add_trans(src, guard, dst)`: Adds a transition to the set.
  - `str_trans(src, guard, dst)`: Converts a transition into a readable string format using `spot.bdd_format_formula`.
  - `__str__()`: Returns all transitions in a string format.

---

### 2. `Automaton`
Represents an automaton with states, transitions, and additional metadata.

- **Attributes**:
  - `state_based`: Indicates if acceptance conditions are state-based.
  - `transition_based`: Indicates if acceptance conditions are transition-based.
  - `states`: A dictionary mapping state IDs to their attributes.
  - `transitions`: A `trans_set` instance for managing transitions.
  - `acceptance_condition`: Stores the acceptance condition.
  - `is_deterministic`: Indicates if the automaton is deterministic.
  - `accepting_states`: A set of accepting states.
  - `player_assignment`: A mapping of states to players.
  - `controllable_aps`: List of controllable atomic propositions.
  - `transitions_with_acceptance`: A list of transitions with associated acceptance sets.
  - `initial_states`: A set of initial states.

- **Methods**:
  - `add_state(state_id, acc_set=None)`: Adds a state with an optional acceptance set.
  - `add_initial_state(state_id)`: Marks a state as initial.
  - `get_initial_states()`: Returns the set of initial states.
  - `add_transition(from_state, to_state, label, accepting_sets)`: Adds a transition with a label and acceptance sets.
  - `set_acceptance_condition(condition)`: Sets the acceptance condition.
  - `set_determinism(is_deterministic)`: Marks the automaton as deterministic or not.
  - `add_accepting_state(state_id)`: Adds a state to the set of accepting states.
  - `set_player(state_id, player)`: Assigns a player to a state.
  - `get_player(state_id)`: Retrieves the player assigned to a state.
  - `set_controllable_aps(controllable_aps)`: Sets controllable atomic propositions.
  - `get_controllable_aps()`: Returns the controllable atomic propositions.
  - `compute_attractor(target_states, player)`: Computes the attractor set for a given player.
  - `create_subgame(excluded_states)`: Creates a subgame excluding specific states.
  - `zielonka()`: Solves the parity game using Zielonka's algorithm.

---

## Functions

### 1. `load_hoa(filename)`
Loads an HOA (Higher-Order Automaton) file into an `Automaton` instance. It extracts states, transitions, acceptance conditions, and other metadata.

### 2. `assign_and_set_players_based_on_parity(spot_automaton, hoa_file)`
Assigns players to states based on parity acceptance conditions.

### 3. `parse_player_assignments(hoa_file)`
Parses player assignments from the HOA file if specified.

### 4. `to_dot(automaton)`
Generates a DOT format string representing the automaton for visualization.

### 5. `write_dot_file(automaton, filename)`
Writes the DOT representation of an automaton to a file.

### 6. `parse_controllable_ap(hoa_file)`
Extracts controllable atomic propositions from the HOA file.

### 7. `process_all_files_in_directory(directory)`
Processes all `.ehoa` files in a directory, applies the Zielonka algorithm, and generates results and DOT files for visualization.

---


## Installation

1. Clone the repository:
   ```bash
    https://github.com/NarjissYouyou/V-Smodelchecker   
    cd V-Smodelchecker
2. Run script:
   ```bash
    ./run.sh
