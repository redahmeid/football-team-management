# Define a state-change map using a dictionary

from enum import Enum

class MatchState(str, Enum):
    created = "created"
    draft = "draft"
    substitutions = "substitutions"
    plan_confirmed = "plan_confirmed"
    starting_lineup_confirmed = "starting_lineup_confirmed"
    plan="plan"
    started="started"
    paused="paused"
    restarted="restarted"
    ended="ended"
    postponed="postponed"
    cancelled="cancelled"

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


