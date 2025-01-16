import spot

class trans_set:
    def __init__(self, dict):
        self.set = set()
        self.dict = dict

    def add_trans(self, src, guard, dst):
        self.set.add((src, guard, dst))

    def str_trans(self, src, guard, dst):
        f = spot.bdd_format_formula(self.dict, guard)
        return f"({src},{f},{dst})"

    def __str__(self):
        return '{' + ",".join([self.str_trans(*t) for t in self.set]) + '}'
    
class Automaton:
    def __init__(self):
        self.state_based = False
        self.transition_based =False
        self.states = {}
        self.transitions = trans_set({}) 
        self.acceptance_condition = None
        self.is_deterministic = False
        self.accepting_states = set() 
        self.player_assignment = {}
        self.controllable_aps = []
        self.transitions_with_acceptance = []
        self.initial_states = set() 

    def add_state(self, state_id, acc_set=None):
        self.states[state_id] = [acc_set]
        self.player_assignment[state_id] = None


    def add_initial_state(self, state_id):
        self.initial_states.add(state_id)
    
    def get_initial_states(self):
        return self.initial_states

    def add_transition(self, from_state, to_state, label, accepting_sets):
        if (to_state, label) not in self.states[from_state]:
            self.states[from_state].append((to_state, label)) 
        self.transitions.add_trans(from_state, label, to_state) 
        self.transitions_with_acceptance.append((from_state, to_state, label, accepting_sets)) 

    def set_acceptance_condition(self, condition):
        self.acceptance_condition = condition

    def set_determinism(self, is_deterministic):
        self.is_deterministic = is_deterministic

    def add_accepting_state(self, state_id):
        self.accepting_states.add(state_id)

    def set_player(self, state_id, player):
        if state_id in self.states:
            self.player_assignment[state_id] = player

    def get_player(self, state_id):
        return self.player_assignment.get(state_id, None)

    def set_controllable_aps(self, controllable_aps):
        self.controllable_aps = controllable_aps

    def get_controllable_aps(self):
        return self.controllable_aps

    def __str__(self):
        return (
            f"Automaton(states={self.states}, "
            f"transitions={self.transitions}, "
            f"accepting_states={self.accepting_states}, "
            f"acceptance_condition={self.acceptance_condition})"
        )

    def compute_attractor(self, target_states, player):
        attractor = set(target_states)
        changed = True
        while changed:
            changed = False
            for state in self.states:
                if state in attractor:
                    continue
                for (to_state, label) in self.states[state][1:]:
                    if to_state in attractor and self.get_player(state) == player:
                        attractor.add(state)
                        changed = True
                        break
        return attractor

    def create_subgame(self, excluded_states):
        subgame = Automaton()
        subgame.states = {s: v for s, v in self.states.items() if s not in excluded_states}
        subgame.transitions = trans_set(self.transitions.dict)
        for (from_state, to_state, label, acc_sets) in self.transitions_with_acceptance:
            if from_state not in excluded_states and to_state not in excluded_states:
                subgame.add_transition(from_state, to_state, label, acc_sets)
        subgame.initial_states = self.initial_states - excluded_states
        subgame.accepting_states = self.accepting_states - excluded_states
        subgame.player_assignment = {k: v for k, v in self.player_assignment.items() if k not in excluded_states}
        subgame.acceptance_condition = self.acceptance_condition
        return subgame

    def zielonka(self):
        if not self.states:
            return set(), set()
        
        def extract_priority(state_info):
            if isinstance(state_info[0], (set, list)):
                return max(state_info[0]) if state_info[0] else None
            return state_info[0]

        max_priority = max(
            (extract_priority(state_info) for state_info in self.states.values() if extract_priority(state_info) is not None),
            default=None,
        )

        if max_priority is None:
            return set(), set()  
        player = max_priority % 2
        target_states = [s for s, state_info in self.states.items() if extract_priority(state_info) == max_priority]

        attractor = self.compute_attractor(target_states, player)
        subgame = self.create_subgame(attractor)
        win_0, win_1 = subgame.zielonka()

        if player == 0:
            win_0.update(attractor)
        else:
            win_1.update(attractor)

        return win_0, win_1
