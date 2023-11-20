import json
from pydantic import ValidationError

import exceptions
from typing import List
from player_data import retrieve_players_by_team
import sys
from matches_data import retrieve_match_by_id
import matches_data
from match_day_data import retrieveNextPlanned,retrieveAllPlannedLineups,save_actual_lineup,save_planned_lineup,retrieveCurrentActual, save_assists_for,save_goals_for,save_opposition_goal
from secrets_util import lambda_handler
import api_helper
from auth import check_permissions
from roles import Role
import matches_state_machine
import player_responses
import match_responses
from match_planning_backend import getMatchPlanning,getMatchConfirmedPlanReadyToStart,getMatchStarted,getMatchCreated,setStats
from datetime import date
baseUrl = "/teams/%s/matches/%s"
acceptable_roles = [Role.admin.value,Role.coach.value]



#/teams/{team_id}/matches/{match_id}/players/submit_lineup
def submit_lineup(event,context):
    lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    team_id = pathParameters["team_id"]
    body =json.loads(event["body"])
    players = body["players"]
    minute = body["minute"]
    new_players = [player_responses.PlayerResponse(**player_dict) for player_dict in players]

    match = retrieve_match_by_id(match_id)
    try:
    
        if(check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):  
             
            if(matches_state_machine.MatchState(match[0].status)==matches_state_machine.MatchState.plan or matches_state_machine.MatchState(match[0].status)==matches_state_machine.MatchState.created):
                matches_data.update_match_status(match_id,matches_state_machine.MatchState.plan.value)
                submit_planned_lineup(match_id=match_id,players=new_players,minute=minute)
            elif(matches_state_machine.MatchState(match[0].status)==matches_state_machine.MatchState.plan_confirmed):
                matches_data.start_match(match_id)
                submit_actual_lineup(match_id=match_id,players=new_players,minute=minute)
            elif(matches_state_machine.MatchState(match[0].status)==matches_state_machine.MatchState.started):
                submit_actual_lineup(match_id=match_id,players=new_players,minute=minute)
            return getMatch(event,context)
        else:
            response = api_helper.make_api_response(403,None,"You do not have permission to edit this match")
            return response
    except exceptions.AuthError as e:
        print(e)
        response = api_helper.make_api_response(401,None,e)
        return response
    except ValidationError as e:
        print(e)
        response = api_helper.make_api_response(400,None,e)
        return response
    except Exception as e:
        print(e)
        response = api_helper.make_api_response(500,None,e)
        return response


def getMatch(event,context):
    lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    team_id = pathParameters["team_id"]

    try:
    
        if(check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)): 
            match = retrieve_match_by_id(match_id)[0]
            print(f"MATCH STATUS {match.status}")
            if(match.status==matches_state_machine.MatchState.created):
                response = getMatchCreated(team_id,match)
            elif(match.status==matches_state_machine.MatchState.plan or (match.status==matches_state_machine.MatchState.plan_confirmed and match.date!=date.today())):
                response = getMatchPlanning(team_id,match)
            elif(match.status==matches_state_machine.MatchState.plan_confirmed and match.date==date.today()):
                response = getMatchConfirmedPlanReadyToStart(team_id,match)
            elif(match.status==matches_state_machine.MatchState.started):
                response = getMatchStarted(team_id,match)
            
            return response
    except exceptions.AuthError as e:
        print(e)
        response = api_helper.make_api_response(401,None,e)
        return response
    except ValidationError as e:
        print(e)
        response = api_helper.make_api_response(400,None,e)
        return response
    except Exception as e:
        print(e)
        response = api_helper.make_api_response(500,None,e)
        return response      

def set_match_stats(event,context):
    lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    team_id = pathParameters["team_id"]
    body =json.loads(event["body"])
    goal_scorer = body["for"]["goal"]
    assister = body["for"]["assist"]

    we_conceded = body["against"]
    oppo_scorer_number = we_conceded["player_number"]

    try:
    
        if(check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)): 
           setStats(match_id,oppo_scorer_number,goal_scorer,assister)
            
        return response
    except exceptions.AuthError as e:
        print(e)
        response = api_helper.make_api_response(401,None,e)
        return response
    except ValidationError as e:
        print(e)
        response = api_helper.make_api_response(400,None,e)
        return response
    except Exception as e:
        print(e)
        response = api_helper.make_api_response(500,None,e)
        return response      




def submit_planned_lineup(match_id,players:List[player_responses.PlayerResponse],minute):
   
    save_planned_lineup(match_id=match_id,minute=minute,players=players)
           
      

def submit_actual_lineup(match_id,players:List[player_responses.PlayerResponse],minute):
 
    save_actual_lineup(match_id=match_id,players=players)
                
      

def update_match_status(event,context):
    lambda_handler(event,context)    
    pathParameters = event["pathParameters"]
    team_id = pathParameters["team_id"]
    status = pathParameters["status"]
    match_id = pathParameters["match_id"]
    try:
        if(check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):  
             if(status=="stats"):
                body =json.loads(event["body"])
                goal_scorer = body["for"]["goal"]
                assister = body["for"]["assist"]

                we_conceded = body["against"]
                oppo_scorer_number = we_conceded["player_number"]
                setStats(match_id,oppo_scorer_number,goal_scorer,assister)
             else:
                matches_data.update_match_status(match_id=match_id,status=matches_state_machine.MatchState(status))
             return getMatch(event,context)    
        else:
            response = api_helper.make_api_response(403,None,"You do not have permission to edit this match")
            return response
    except exceptions.AuthError as e:
        print(e)
        response = api_helper.make_api_response(401,None,e)
        return response
    except ValidationError as e:
        print(e)
        response = api_helper.make_api_response(400,None,e)
        return response
    except Exception as e:
        print(e)
        response = api_helper.make_api_response(500,None,e)
        return response


def list_of_player_ids(players:list):
   return [item["id"] for item in players]
def list_start_line_up_player_ids(players:list):
   return [item["Player_ID"] for item in players]

def list_of_player_ids_from_db(players:list):
   return [item["ID"] for item in players]

# if(sys.argv[1]=="getMatchStarted"):
#     getMatchStarted(sys.argv[2], sys.argv[3])