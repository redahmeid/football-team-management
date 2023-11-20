

import sys

from match_day_data import retrieveNextPlanned,retrieveAllPlannedLineups,retrieveCurrentActual,retrieveStartingLineup,save_goals_for,save_assists_for,save_opposition_goal,retrieveNextPlannedByMinute
from player_data import retrieve_players_by_team
import api_helper
from matches_data import retrieve_match_by_id
from typing import Dict
import matches_state_machine

import match_responses

baseUrl = "/teams/%s/matches/%s"



def getMatchCreated(team_id,match):
    playersList = retrieve_players_by_team(team_id)  
    url = match_responses.getMatchUrl(team_id,match.id)
    submit_first_subs = match_responses.Link(link=f'{url}/players/submit_lineup',method="post")
    confirm_plan = match_responses.Link(link=f'{url}/{matches_state_machine.MatchState.plan.value}',method="post")

    links = {"submit_lineup":submit_first_subs,"confirm_plan":confirm_plan }
    match_day_response = match_responses.MatchResponse(match=match,squad=playersList,links=createMatchLinks(url,links)).model_dump()
    match_day_responses = [match_day_response]

    response = api_helper.make_api_response(200,match_day_responses)
    print("match_detail_screnn.py.enter_set_lineup %s"%response)
    return response


def getMatchConfirmedPlanReadyToStart(team_id,match):
    selected_players = retrieveStartingLineup(match_id=match.id)
    next_players = retrieveNextPlannedByMinute(match_id=match.id,minutes=0)
    url = match_responses.getMatchUrl(team_id,match.id)
    submit_first_subs = match_responses.Link(link=f'{url}/players/submit_lineup',method="post")
    end_match = match_responses.Link(link=f'{url}/{matches_state_machine.MatchState.ended.value}',method="post")
    links = {"submit_lineup":submit_first_subs,"end_match":end_match }
    match_day_response = match_responses.ActualMatchResponse(match=match,current_players=selected_players,next_players= next_players, links=createMatchLinks(url,links)).model_dump()
    match_day_responses = []
    match_day_responses.append(match_day_response)

    response = api_helper.make_api_response(200,match_day_responses)
    print("match_planning_backend.getMatchConfirmedPlan %s"%response)
    return response

def getMatchPlanning(team_id,match):
    selected_players = retrieveAllPlannedLineups(match_id=match.id)
    
    url = match_responses.getMatchUrl(team_id,match.id)
    submit_first_subs = match_responses.Link(link=f'{url}/players/submit_lineup',method="post")
    confirm_plan = match_responses.Link(link=f'{url}/{matches_state_machine.MatchState.plan_confirmed.value}',method="post")
    links = {"submit_lineup":submit_first_subs,"confirm_plan":confirm_plan }
    match_day_response = match_responses.PlannedMatchResponse(match=match,planned_lineups=selected_players,links=createMatchLinks(url,links)).model_dump()
    match_day_responses = []
    match_day_responses.append(match_day_response)

    response = api_helper.make_api_response(200,match_day_responses)
    print("\n\nmatch_detail_screnn.py.getMatchPlanning %s"%response)
    return response

def getMatchStarted(team_id,match):
    next_lineup = retrieveNextPlanned(match_id=match.id)
    print("#########################NEXT LINEUP###################################")
    print(next_lineup)
    print("#########################NEXT LINEUP###################################")
    current_lineup = retrieveCurrentActual(match_id=match.id)
    print(current_lineup)
    url = match_responses.getMatchUrl(team_id,match.id)
    submit_first_subs = match_responses.Link(link=f'{url}/players/submit_lineup',method="post")
    confirm_plan = match_responses.Link(link=f'{url}/{matches_state_machine.MatchState.plan_confirmed.value}',method="post")
    links = {"submit_lineup":submit_first_subs,"confirm_plan":confirm_plan }
    match_day_response = match_responses.ActualMatchResponse(match=match,current_players=current_lineup,next_players=next_lineup,links=createMatchLinks(url,links)).model_dump()
    match_day_responses = []
    match_day_responses.append(match_day_response)

    response = api_helper.make_api_response(200,match_day_responses)
    print("match_planning_backend.py.getMatchStarted %s"%response)
    return response

def setStats(match_id,oppo_scorer_number,goal_scorer,assister):
     if(oppo_scorer_number is not None):
        save_opposition_goal(match_id,oppo_scorer_number)
     else:
        save_assists_for(match_id,goal_scorer)
        save_goals_for(match_id,assister)

def createMatchLinks(url, links:Dict[str,match_responses.Link]):
    self = match_responses.Link(link=url,method="get")
    print(links)
    links["self"] = self
    print(links)
    return links


if __name__ == "__main__":
    if(sys.argv[1]=="getMatchCreated"):
        match = retrieve_match_by_id(sys.argv[3])[0]
        getMatchCreated(sys.argv[2],match )
    if(sys.argv[1]=="getMatchStarted"):
        match = retrieve_match_by_id(sys.argv[3])[0]
        getMatchStarted(sys.argv[2],match)
    if(sys.argv[1]=="getMatchConfirmedPlan"):
        match = retrieve_match_by_id(sys.argv[3])[0]
        getMatchConfirmedPlanReadyToStart(sys.argv[2],match)