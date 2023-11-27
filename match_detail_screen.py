import json
from pydantic import ValidationError

import exceptions
from typing import List
from player_data import retrieve_players_by_team
import sys
from matches_data import retrieve_match_by_id
import matches_data
from match_day_data import retrieve_periods_by_match,retrieveNextPlanned,retrieveAllPlannedLineups,save_actual_lineup,save_planned_lineup,retrieveCurrentActual, save_assists_for,save_goals_for,save_opposition_goal
from secrets_util import lambda_handler
import api_helper
from auth import check_permissions
from roles import Role
import matches_state_machine
import player_responses
import match_responses
from match_planning_backend import getMatchPlanning,getMatchConfirmedPlanReadyToStart,getMatchStarted,getMatchCreated,setGoalsFor,getMatchGuest,updateMatchPeriod,setGoalsAgainst
from datetime import date
import logging
import time
import asyncio
import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def timeit(method):
    def timed(*args, **kw):
        start_time = time.time()
        result = method(*args, **kw)
        end_time = time.time()

        logging.info(f"{method.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return timed
baseUrl = "/teams/%s/matches/%s"
acceptable_roles = [Role.admin.value,Role.coach.value]



#/teams/{team_id}/matches/{match_id}/players/submit_lineup
async def submit_lineup(event,context):
    lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    team_id = pathParameters["team_id"]
    body =json.loads(event["body"])
    players = body["players"]
    minute = body["minute"]
    new_players = [player_responses.PlayerResponse(**player_dict) for player_dict in players]

    match = await retrieve_match_by_id(match_id)
    try:
    
        if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):  
             
            if(matches_state_machine.MatchState(match[0].status)==matches_state_machine.MatchState.plan or matches_state_machine.MatchState(match[0].status)==matches_state_machine.MatchState.created):
                
                    await matches_data.update_match_status(match_id,matches_state_machine.MatchState.plan.value),
                    await submit_planned_lineup(match_id=match_id,players=new_players,minute=minute)
            elif(matches_state_machine.MatchState(match[0].status)==matches_state_machine.MatchState.plan_confirmed):
                    
                    await submit_actual_lineup(match_id=match_id,players=new_players)
                
            elif(matches_state_machine.MatchState(match[0].status)==matches_state_machine.MatchState.started):
                await submit_actual_lineup(match_id=match_id,players=new_players)
            return await getMatch(event,context)
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

async def submit_substitutions(event,context):
    lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    team_id = pathParameters["team_id"]
    body =json.loads(event["body"])
    players = body["players"]
    minute = body["minute"]
    new_players = [player_responses.PlayerResponse(**player_dict) for player_dict in players]

    match = await retrieve_match_by_id(match_id)
    try:
    
        if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):  
            await submit_subs(match_id=match_id,players=new_players)
            return await getMatch(event,context)
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
    
async def getMatchAsGuest(event,context):
    lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]

    try:
        matchList = await retrieve_match_by_id(match_id)
        if(len(matchList)==0):
            response = api_helper.make_api_response(404,None,e)
        else:
            match = matchList[0]
            response = await getMatchGuest(match)
        print(response)
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


async def getMatch(event,context):
    lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    team_id = pathParameters["team_id"]

    try:
        matchList = await retrieve_match_by_id(match_id)
        match = matchList[0]
        if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)): 
            
            print(f"MATCH STATUS {match.status}")
            if(match.status==matches_state_machine.MatchState.created):
                response = await getMatchCreated(team_id,match)
            elif(match.status==matches_state_machine.MatchState.plan or (match.status==matches_state_machine.MatchState.plan_confirmed and match.date!=date.today())):
                response = await getMatchPlanning(team_id,match)
            elif(match.status==matches_state_machine.MatchState.plan_confirmed and match.date==date.today()):
                response = await getMatchConfirmedPlanReadyToStart(team_id,match)
            elif(match.status==matches_state_machine.MatchState.started or match.status==matches_state_machine.MatchState.ended):
                response =  await getMatchStarted(team_id,match)
            logging.info(response)
            return response
        else:
            response = await getMatchGuest(match)
            print(response)
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

async def set_match_stats(event,context):
    lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    team_id = pathParameters["team_id"]
    body =json.loads(event["body"])
    goal_scorer = body["for"]["goal"]
    assister = body["for"]["assist"]

    we_conceded = body["against"]
    

    try:
    
        if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)): 
           await setGoalsFor(match_id,goal_scorer,assister)
            
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




async def submit_planned_lineup(match_id,players:List[player_responses.PlayerResponse],minute):
   
    await save_planned_lineup(match_id=match_id,minute=minute,players=players)
           
      

async def submit_actual_lineup(match_id,players:List[player_responses.PlayerResponse]):
    await updateMatchPeriod(match_id,matches_state_machine.MatchState.started.value)
    await matches_data.update_match_status(match_id=match_id,status=matches_state_machine.MatchState(matches_state_machine.MatchState.started.value))
    await save_actual_lineup(match_id=match_id,players=players,time_playing=0)

async def submit_subs(match_id,players:List[player_responses.PlayerResponse]):
    periods = await retrieve_periods_by_match(match_id)
    time_playing = 0
    last_period = {}
    started_at = 0
    ended = False
    for period in periods:
        if(period.status=="ended"):
            time_playing = time_playing + (period.time - last_period.time)
            ended = True
        if(period.status == "paused"):
            time_playing = time_playing + (period.time - last_period.time)
            print(f"TIME PLAYING PAUSE {time_playing}")
            last_period = period
        if(period.status=="started" or period.status=="restarted"):
            print(f"TIME PLAYING STARTED {time_playing}")
            if(period.status=="started"):
                started_at = period.time
            last_period = period
    
    time_playing = int((datetime.datetime.utcnow().timestamp()-time_playing-started_at)/60)
    await updateMatchPeriod(match_id,matches_state_machine.MatchState.substitutions.value)
    await save_actual_lineup(match_id=match_id,players=players,time_playing=time_playing)
                
      

async def update_match_status(event,context):
    lambda_handler(event,context)    
    pathParameters = event["pathParameters"]
    team_id = pathParameters["team_id"]
    status = pathParameters["status"]
    match_id = pathParameters["match_id"]
    try:
        if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):  
             if(status=="score_for"):
                body =json.loads(event["body"])
                goal_scorer = body["scorer"]["info"]["id"]
                assister = body["assister"]["info"]["id"]
                await setGoalsFor(match_id,goal_scorer,assister)
             elif(status=="score_against"):
                await setGoalsAgainst(match_id)
             elif(status=="paused" or status=="restarted" or status=="started"):
                 await updateMatchPeriod(match_id,status)
                 await matches_data.update_match_status(match_id=match_id,status=matches_state_machine.MatchState(status))
             else:
                await matches_data.update_match_status(match_id=match_id,status=matches_state_machine.MatchState(status))
             return await getMatch(event,context)    
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