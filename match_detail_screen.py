import json
from pydantic import ValidationError
import classes
import traceback
import exceptions
from typing import List
from player_data import retrieve_players_by_team_with_stats
import sys
from cache_trigger import updateTeamCache,updateMatchCache, updateMatchPlanCache,updateMatchCurrentLineupCache, updateMatchActualCache,updateUserCache
from matches_data import retrieve_match_by_id
import matches_data
from match_day_data import retrieve_periods_by_match,retrieveNextPlanned,retrieveAllPlannedLineups,save_actual_lineup,save_planned_lineup,retrieveCurrentActual, save_assists_for,save_goals_for,save_opposition_goal
from secrets_util import lambda_handler,getEmailFromToken
import api_helper
import match_day_data
from auth import check_permissions
from roles import Role
import matches_state_machine
import player_responses
import response_classes
import match_planning_backend
from match_planning_backend import updateStatus,submit_match_lineup, submit_starting_lineup,submit_planned_lineup,submit_subs,getMatchPlanning,getMatchConfirmedPlanReadyToStart,getMatchStarted,getMatchCreated,setGoalsFor,getMatchGuest,updateMatchPeriod,setGoalsAgainst,addGoalScorers
from datetime import date
import user_homepage_backend

import logging
import time
import asyncio
import datetime
import notifications
import matches_backend
from caching_data import Paths
import team_backend
import enum
from config import app_config
from etag_manager import setEtag,isEtaggged,deleteEtag, updateDocument, whereEqual,getObject,whereEqualwhere
from fcatimer import fcatimer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fcatimer(method):
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
async def start_match(event,context):
    await lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    body =json.loads(event["body"])
    players = body["players"]
    minute = body["minute"]
    new_players = [classes.Player(**player_dict) for player_dict in players]

    match = await retrieve_match_by_id(match_id)
    try:
    
        if(await check_permissions(event=event,team_id=match[0].team_id,acceptable_roles=acceptable_roles)):  
             
            
            if(matches_state_machine.MatchState(match[0].status)==matches_state_machine.MatchState.starting_lineup_confirmed):
                    await match_planning_backend.start_match(match_id=match_id)
                   

            return  api_helper.make_api_response(201,{"link":f"/matches/{match_id}?refresh=time_played"})
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

#/matches/{match_id}/invites
async def update_invites(event,context):
    await lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    body =json.loads(event["body"])
    players = body["players"]
   
   
    match = await retrieve_match_by_id(match_id)
    try:
    
        if(await check_permissions(event=event,team_id=match[0].team.id,acceptable_roles=acceptable_roles)): 
            await matches_backend.updateInvites(match_id,players=players)
            response =  api_helper.make_api_response(201,None,"You do not have permission to edit this match")
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
#/teams/{team_id}/matches/{match_id}/players/submit_lineup
async def submit_lineup(event,context):
    await lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    body =json.loads(event["body"])
    players = body["players"]
    minute = body["minute"]
    new_players = [classes.Player(**player_dict) for player_dict in players]
   
    match = await retrieve_match_by_id(match_id)
    try:
    
        if(await check_permissions(event=event,team_id=match[0].team_id,acceptable_roles=acceptable_roles)):  
             
            if(matches_state_machine.MatchState(match[0].status)==matches_state_machine.MatchState.plan or matches_state_machine.MatchState(match[0].status)==matches_state_machine.MatchState.created):
                await updateStatus(match_id,matches_state_machine.MatchState.plan),
                await submit_planned_lineup(match_id=match_id,players=new_players,minute=minute)     
                
                data = {
                    "link":f"/matches/{match_id}",
                    "match_id":f"{match_id}",
                    "action":"new_plan",
                    "silent": True
                }
                await notifications.sendNotificationUpdatesLink(match_id,"Lineup created","Lineup created",'admins',data)
                return api_helper.make_api_response(201,{"link":f"/matches/{match_id}/planned_lineups"})
            elif(matches_state_machine.MatchState(match[0].status)==matches_state_machine.MatchState.plan_confirmed):
                await submit_starting_lineup(match_id=match_id,players=new_players)
                
                data = {
                    "link":f"/matches/{match_id}",
                    "match_id":f"{match_id}",
                    "action":"actual_lineups",
                    "silent": True
                }
                await notifications.sendNotificationUpdatesLink(match_id,"Lineup created","Lineup created",'match',data)
                return api_helper.make_api_response(201,{"link":f"/matches/{match_id}/actual_lineups"})
            elif(matches_state_machine.MatchState(match[0].status)==matches_state_machine.MatchState.started or (matches_state_machine.MatchState(match[0].status)==matches_state_machine.MatchState.starting_lineup_confirmed)):
                await submit_match_lineup(match_id=match_id,players=new_players,minute=minute) 
                
                data = {
                    "link":f"/matches/{match_id}",
                    "match_id":f"{match_id}",
                    "action":"actual_lineups",
                    "silent": True
                }
                await notifications.sendNotificationUpdatesLink(match_id,"Lineup created","Lineup created",'match',data)
                return api_helper.make_api_response(201,{"link":f"/matches/{match_id}/actual_lineups"})
            
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

async def set_captain(event,context):
    await lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    body =json.loads(event["body"])
    player_id = body["player_id"]
    path = event.get('rawPath') or event.get('path')

   


    match = await retrieve_match_by_id(match_id)
    try:
    
        if(await check_permissions(event=event,team_id=match[0].team.id,acceptable_roles=acceptable_roles)):  
            if "captain" in path:
                await matches_data.set_captain(match[0],player_id)
            elif "potm" in path:
                await matches_data.set_potm(match[0],player_id)
            else:
                response = api_helper.make_api_response(400,"Enter captain or potm")
                return response
            return api_helper.make_api_response(201,{"link":f"/matches/{match_id}?refresh=time_played"})
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
    await lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    body =json.loads(event["body"])
    players = body["players"]
    minute = body["minute"]
    new_players = [classes.Player(**player_dict) for player_dict in players]

    match = await retrieve_match_by_id(match_id)
    try:
    
        if(await check_permissions(event=event,team_id=match[0].team.id,acceptable_roles=acceptable_roles)):  
            
            await submit_subs(match=match[0],players=new_players)
            match_response = await match_planning_backend.getMatchStarted(match[0].team.id,match[0])
            return api_helper.make_api_response(201,{"link":f"/matches/{match_id}?refresh=time_played"})
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

async def retrieveScore(event,context):
    await lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    

    object = await matches_backend.getMatchFromDB(match_id)
    match = object["result"]
    try:
    
        
        response = {"goals_for":match.match.goals,"goals_against":match.match.conceded}
        return api_helper.make_api_response(200,response)
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
    await lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    matches = []
    try:
        matchList = await retrieve_match_by_id(match_id)
        if(len(matchList)==0):
            response = api_helper.make_api_response(404,None,e)
        else:
            match = matchList[0]
            response = await match_planning_backend.getMatch(match.team.id, match)
        print(response)
        matches.append(response)
        return api_helper.make_api_response(200,matches,None)
    except exceptions.AuthError as e:
        traceback.print_exception(*sys.exc_info()) 
        response = api_helper.make_api_response(401,None,e)
        return response
    except ValidationError as e:
        traceback.print_exception(*sys.exc_info()) 
        response = api_helper.make_api_response(400,None,e)
        return response
    except Exception as e:
        traceback.print_exception(*sys.exc_info()) 
        response = api_helper.make_api_response(500,None,e)
        return response      


async def getMatch(event,context):
    await lambda_handler(event,context)
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
            elif(match.status==matches_state_machine.MatchState.started or match.status==matches_state_machine.MatchState.ended or match.status==matches_state_machine.MatchState.paused or match.status==matches_state_machine.MatchState.restarted):
                response =  await getMatchStarted(team_id,match)
            else:
                response =  await getMatchStarted(team_id,match)
            return response
        else:
            response = await match_planning_backend.getMatch(match.team.id, match)
            matches = []
            matches.append(response)
            print(response)
            return api_helper.make_api_response(200,matches,None)
    except exceptions.AuthError as e:
        traceback.print_exception(*sys.exc_info()) 
        response = api_helper.make_api_response(401,None,e)
        return response
    except ValidationError as e:
        traceback.print_exception(*sys.exc_info()) 
        response = api_helper.make_api_response(400,None,e)
        return response
    except Exception as e:
        traceback.print_exception(*sys.exc_info()) 
        response = api_helper.make_api_response(500,None,e)
        return response      

async def set_match_stats(event,context):
    await lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    team_id = pathParameters["team_id"]
    body =json.loads(event["body"])
    goal_scorer = body["for"]["goal"]
    assister = body.get('for').get('assist')
    type = body.get('for').get('type')

    we_conceded = body["against"]
    

    try:
    
        if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)): 
           await match_planning_backend.sendGoalScoredNotification(team_id,match_id,goal_scorer,assister,type)
            
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





async def subs_due(event,context):
    match_planning_backend.subs_due(event)
      

async def add_goal_scorers(event,context):
    await lambda_handler(event,context)    
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    
    try:
        match = await retrieve_match_by_id(match_id)
        team_id = match[0].team.id
        if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):  
             
            body =json.loads(event["body"])
            await match_day_data.delete_goal_scorers(match_id)
            scorers = body.get('scorers')
            print(f"SCORERS {scorers}")
            for scorer in scorers:
                goal_scorer = scorer['player']
                assister = scorer['secondary_player']
                assist_type = scorer['assist_type']
                time_playing = scorer['minute']
                
                type = scorer['type']
                await addGoalScorers(team_id,match_id,goal_scorer,assister,type,assist_type,time_playing)
                
             
            await updateTeamCache(team_id)
            await updateUserCache(getEmailFromToken(event,context))
             
              # asyncio.create_task(matches_backend.getMatchFromDB(match_id))
            print(f"UPDATE STATUS TASK CREATION END {match_id}")
            match = await matches_backend.getMatchFromDB(match_id)
            return api_helper.make_api_response_etag(200,match["result"],match["etag"])   
        else:
            response = api_helper.make_api_response(403,None,"You do not have permission to edit this match")
            return response
    except exceptions.AuthError as e:
        print(e)
        traceback.print_exception(*sys.exc_info()) 
        response = api_helper.make_api_response(401,None,e)
        return response
    except ValidationError as e:
        print(e)
        traceback.print_exception(*sys.exc_info()) 
        response = api_helper.make_api_response(400,None,e)
        return response
    except Exception as e:
        print(e)
        traceback.print_exception(*sys.exc_info()) 
        response = api_helper.make_api_response(500,None,e)
        return response
@fcatimer
async def update_match_status(event,context):
    await lambda_handler(event,context)    
    pathParameters = event["pathParameters"]
    status = pathParameters["status"]
    match_id = pathParameters["match_id"]
    print(f"STATUS FROM REQUEST {status}")
    try:
        match = await retrieve_match_by_id(match_id)
        team_id = match[0].team_id
        if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):  
             if(status=="score_for"):
                body =json.loads(event["body"])
                goal_scorer = body["scorer"]
                assister = body.get('assister')
                assist_type = body.get('assist_type',"")
                
                type = body.get('type')
                await match_planning_backend.sendGoalScoredNotification(team_id,match_id,goal_scorer,assister,type,assist_type)
                
             elif(status=="score_against"):
                await match_planning_backend.sendGoalConcededNotification(team_id,match_id)
             elif(status=="paused" or status=="restarted" or status=="started"):
                 
                 await match_planning_backend.updateStatus(match_id=match_id,status=matches_state_machine.MatchState(status))
             else:
                await match_planning_backend.updateStatus(match_id=match_id,status=matches_state_machine.MatchState(status))
                print(f"UPDATE STATUS TASK CREATION START {match_id}")
            
            
             return api_helper.make_api_response(200,{})   
        else:
            response = api_helper.make_api_response(403,None,"You do not have permission to edit this match")
            return response
    except exceptions.AuthError as e:
        print(e)
        traceback.print_exception(*sys.exc_info()) 
        response = api_helper.make_api_response(401,None,e)
        return response
    except ValidationError as e:
        print(e)
        traceback.print_exception(*sys.exc_info()) 
        response = api_helper.make_api_response(400,None,e)
        return response
    except Exception as e:
        print(e)
        traceback.print_exception(*sys.exc_info()) 
        response = api_helper.make_api_response(500,None,e)
        return response

from secrets_util import initialise_firebase
from firebase_admin import credentials, firestore
@fcatimer
async def calculate_match_stats(event,context):
    await initialise_firebase()
    # id = event['id']
    # where_team = {
    #     'compare':'team_id',
    #     'fieldValue':id
    # }
    # where_team,
    where_stats = firestore.FieldPath.exists("stats_calculated")
    where_status = firestore.FieldFilter('status', '==', 'ended')

    fs_matches = await whereEqualwhere('matches_store',wheres=[where_status,where_stats])
    if(fs_matches):
        print(fs_matches)
        i = 0
        for  fs_match in fs_matches:
            fs_match_dict = fs_match.to_dict()
            print(f'Match number {i}')
            i = i+1




def list_of_player_ids(players:list):
   return [item["id"] for item in players]
def list_start_line_up_player_ids(players:list):
   return [item["Player_ID"] for item in players]

def list_of_player_ids_from_db(players:list):
   return [item["ID"] for item in players]

# if(sys.argv[1]=="getMatchStarted"):
#     getMatchStarted(sys.argv[2], sys.argv[3])