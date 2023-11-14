# Define a state-change map using a dictionary

from enum import Enum

class MatchState(str, Enum):
    created = "created"
    draft = "draft"
    lineup_confirmed = "lineup_confirmed"
    substitutions = "substitutions"
    plan_confirmed = "plan_confirmed"
    start_match = "start_match"
    actual_substitutions = "actual_subs"
    actual_match_started = "match_started"
    actual_match_ended = "match_ended"

state_change_map = {
    MatchState.created: [MatchState.draft],
    MatchState.draft: [MatchState.lineup_confirmed],
    MatchState.lineup_confirmed: [MatchState.draft, MatchState.plan_confirmed],
    MatchState.plan_confirmed: [MatchState.lineup_confirmed, MatchState.start_match],
    MatchState.start_match: ["make_subs","add_scorer","add_oppo_goals","add_assist"]
}

# Function to perform a state transition
def perform_state_transition(current_state:MatchState):
    next_states = state_change_map.get(current_state)
    return next_states


