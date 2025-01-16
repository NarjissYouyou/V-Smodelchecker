import spot
from omega_automaton import Automaton
import os

def load_hoa(filename):
    spot_automaton = spot.automaton(filename)
    internal_automaton = Automaton()
    bdd_dict = spot_automaton.get_dict()
    controllable_aps = parse_controllable_ap(filename)
    internal_automaton.set_controllable_aps(controllable_aps)

    internal_automaton.add_initial_state(spot_automaton.get_init_state_number())

    acceptance_condition = spot_automaton.get_acceptance()
    internal_automaton.set_acceptance_condition(str(acceptance_condition))
    # print("acceptance cond", str(acceptance_condition))

    for state_id in range(spot_automaton.num_states()):
        for edge in spot_automaton.out(state_id):
            accepting_sets = {i for i in range(spot_automaton.num_sets()) if edge.acc.has(i)}
        internal_automaton.add_state(state_id, accepting_sets)

    for state_id in range(spot_automaton.num_states()):
        for edge in spot_automaton.out(state_id):
            from_state = edge.src
            to_state = edge.dst
            condition = spot.bdd_format_formula(bdd_dict, edge.cond)
            if not spot_automaton.prop_state_acc():
                internal_automaton.state_based = False
                internal_automaton.transition_based = True
                accepting_sets = {i for i in range(spot_automaton.num_sets()) if edge.acc.has(i)}
                internal_automaton.add_transition(from_state, to_state, condition, accepting_sets)
            else:
                internal_automaton.state_based = True
                internal_automaton.transition_based = False
                internal_automaton.add_transition(from_state, to_state, condition, None)

    if spot_automaton.prop_state_acc():
        for state_id in range(spot_automaton.num_states()):
            if spot_automaton.state_is_accepting(state_id):
                internal_automaton.add_accepting_state(state_id)

    internal_automaton.set_determinism(spot_automaton.is_deterministic())

    state_players = assign_and_set_players_based_on_parity(spot_automaton, filename)
    for state_id in range(spot_automaton.num_states()):
        if state_id < len(state_players):
            player = state_players[state_id]
            internal_automaton.set_player(state_id, player)
        else:
            internal_automaton.set_player(state_id, 0)

    return internal_automaton, spot_automaton



def assign_and_set_players_based_on_parity(spot_automaton, hoa_file):
    state_players = parse_player_assignments(hoa_file)

    if state_players:
        spot_players = [player == 1 for player in state_players]
    else:
        state_players = []
        num_acceptance_sets = spot_automaton.num_sets()

        for state_id in range(spot_automaton.num_states()):
            associated_acceptance_sets = set()

            for edge in spot_automaton.out(state_id):
                for i in range(num_acceptance_sets):
                    if edge.acc.has(i):
                        associated_acceptance_sets.add(i)

            if any(i % 2 == 0 for i in associated_acceptance_sets):  
                state_players.append(0)  
            else:
                state_players.append(1)  

        spot_players = [player == 1 for player in state_players]

    spot.set_state_players(spot_automaton, spot_players)

    return state_players



def parse_player_assignments(hoa_file):
    with open(hoa_file, 'r') as f:
        for line in f:
            if line.startswith("spot-state-player:") or line.startswith("spot.state-player:"):
                return list(map(int, line.split()[1:])) 
    return []


def to_dot(automaton):
    dot_str = "digraph G {\n"

    dot_str += '    start [shape="none", label=""];\n'
    for initial_state in automaton.get_initial_states():
        dot_str += f'    start -> {initial_state};\n'
    
    for state in automaton.states:
        player = automaton.get_player(state)
        if player == 0 and state in automaton.accepting_states:
            shape = "circle"
            peripheries = 2
        elif player == 0 and state not in automaton.accepting_states:
            shape = "circle"
            peripheries = 1
        elif player == 1 and state in automaton.accepting_states:
            shape = "diamond"
            peripheries = 2
        elif player == 1 and state not in automaton.accepting_states:
            shape = "diamond"
            peripheries = 1
        else:
            shape = "circle"
            peripheries = 2 if state in automaton.accepting_states else 1
        acc_set = automaton.states.get(state, [None])[0]  

        if automaton.state_based and acc_set:
            accepting_str = "{" + ", ".join(map(str, acc_set)) + "}" if acc_set else "∅"
            dot_str += f'    {state} [shape="{shape}", peripheries={peripheries}, style="filled", fillcolor="pink", label="{state}\\n {accepting_str}"];\n'
        else:
            dot_str += f'    {state} [shape="{shape}", peripheries={peripheries}, style="filled", fillcolor="pink"];\n'

    if automaton.transition_based:
        for from_state, to_state, label, accepting_sets in automaton.transitions_with_acceptance:
            accepting_str = "{" + ", ".join(map(str, accepting_sets)) + "}" if accepting_sets else "∅"
            dot_str += f'    {from_state} -> {to_state} [label="{label}\\n {accepting_str}"];\n'
    else:
        for from_state, to_state, label, accepting_sets in automaton.transitions_with_acceptance:
            dot_str += f'    {from_state} -> {to_state} [label="{label}"];\n'

    dot_str += "}\n"
    return dot_str



def write_dot_file(automaton, filename):
    try:
        with open(filename, 'w') as f:
            f.write(to_dot(automaton))
    except Exception as e:
        print(f"Error writing DOT file: {e}")

def parse_controllable_ap(hoa_file):
    with open(hoa_file, 'r') as f:
        for line in f:
            if line.startswith("controllable-AP:"):
                return list(map(int, line.split()[1:])) 
    return []


def process_all_files_in_directory(directory):
    results_file = os.path.join(directory, "../results.txt")
    with open(results_file, "w") as log_file:
        for root, _, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)

                if filename.endswith(".ehoa"):  
                    try:
                        internal_automaton, spot_automaton = load_hoa(filepath)
                        spot_solution = spot.solve_parity_game(spot_automaton)
                        win_0, win_1 = internal_automaton.zielonka()
                        initial_states = internal_automaton.get_initial_states()
                        zielonka_result = any(state in win_0 for state in initial_states)
                        # comparison = "Match" if zielonka_result == spot_solution else "Mismatch"
                        # print(f"{filename}: {zielonka_result}\n win_0: {win_0}")
                        log_file.write(f"{filename}: {zielonka_result}\n")
                        write_dot_file(internal_automaton , f"./dotfiles/{filename}.dot")
                    except Exception as e:
                        log_file.write(f"{filename}: Error - {e}\n")
    print(f"Results written to {results_file}")

if __name__ == "__main__":
    directory_path = "./paritySelection2024/selection2024"
    process_all_files_in_directory(directory_path)
