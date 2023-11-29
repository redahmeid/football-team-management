# Define a state-change map using a dictionary

from enum import Enum

class MatchState(str, Enum):
    created = "created"
    draft = "draft"
    starting_lineup_set = "starting_lineup_set"
    substitutions = "substitutions"
    plan_confirmed = "plan_confirmed"
    actual_match_started = "match_started"
    actual_match_ended = "match_ended"
    plan="plan"
    started="started"
    paused="paused"
    restarted="restarted"
    ended="ended"

state_change_map = {
    MatchState.created: [MatchState.plan],
    MatchState.plan: [MatchState.plan_confirmed],
    MatchState.plan_confirmed:[MatchState.started],
    MatchState.started: [MatchState.ended]
}

# Function to perform a state transition
def perform_state_transition(current_state:MatchState):
    next_states = state_change_map.get(current_state)
    return next_states


