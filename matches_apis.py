import json
from pydantic import TypeAdapter, ValidationError, BaseModel
from typing import List
from config import app_config
import api_helper
import response_errors
import team_backend
from matches_data import retrieve_match_by_id,save_team_fixture,retrieve_not_played_by_team,retrieve_next_match_by_team,update_match_status
import notifications
from roles import Role
from auth import check_permissions
import match_detail_screen
import response_classes
import matches_data
import match_planning_backend
import match_day_data
import matches_backend
import user_homepage_backend
import matches_state_machine
import exceptions
from secrets_util import lambda_handler, getEmailFromToken
from match_planning_backend import list_matches_by_team_backend
from matches_backend import create_match_backend
from etag_manager import deleteEtag,whereEqual,getObject,updateDocument
import functools
import time
import sys
import traceback
import json

import firebase_admin
from firebase_admin import credentials, firestore
from fcatimer import fcatimer
from cache_trigger import updateTeamCache,updateMatchCache, updateUserCache,updatePlayerCache


async def create_fixtures(event, context):
    await lambda_handler(event,context)
    http_method = event['httpMethod']

    
    body =json.loads(event["body"])
    print(body)
    pathParameters = event["pathParameters"]
    team_id = pathParameters["team_id"]
    
    
    matches = body["matches"]
    created_matches = []
    for match in matches:
    
        try:
            result = await create_match_backend(match,team_id)
            
            created_matches.append(result.model_dump())
        except ValidationError as e:
            print(f"CREATE MATCH VALIDATION ERROR {e}")
            errors = response_errors.validationErrorsList(e)
            response = api_helper.make_api_response(400,None,errors)
        except ValueError as e:
            print(f"CREATE MATCH VALUE ERROR {e}")
            response = api_helper.make_api_response(400,None)

    
    response = api_helper.make_api_response(200,created_matches)
    print(f"CREATE MATCH API RESPONSE {response}")
    return response
    
async def list_matches_by_team(event, context):
    try:
        team_id = event["pathParameters"]["team_id"]
        
        response =  await list_matches_by_team_backend(team_id)
        return api_helper.make_api_response(200,response)
    except Exception as e:
        traceback.print_exception(*sys.exc_info()) 

@fcatimer
async def time_played(event,context):
    await lambda_handler(event,context)
    
    match_id = event["pathParameters"]["match_id"]
    response = await match_planning_backend.how_long_played(match_id)
    return api_helper.make_api_response(200,{"player":response})

# @fcatimer
# async def updateFromCache(event,context):
#     await lambda_handler(event,context)
#     await matches_backend.updateDBFromCache()
@fcatimer
async def edit_match(event,context):
    await lambda_handler(event,context)
    body =json.loads(event["body"])
    match_id = event["pathParameters"]["match_id"]
    
    goals_for = body.get("goals_for","")
    goals_against = body.get("goals_against","")
    players = body.get("players","")
    if(goals_for!="" and goals_against!=""):
        await matches_backend.updateScore(match_id,goals_for,goals_against)
    if(len(players)>0):
        await matches_backend.addPlayerRatings(match_id,players)
        await match_planning_backend.updateStatus(match_id,matches_state_machine.MatchState.rated)
    await updateMatchCache(match_id)
    
    result = await matches_backend.getMatchFromDB(match_id)
    await updateTeamCache(result["result"]["match"]["team"]["id"])
    await updatePlayerCache(result["result"]["match"]["team"]["id"])
    response =  api_helper.make_api_response_etag(200,[result["result"]],result["etag"])
    print(f"EDIT RESPONSE {response}")
    return response


@fcatimer
async def addGoalScorer(event,context):
    await lambda_handler(event,context)

    
    body =json.loads(event["body"])
    goal_scorer = body["scorer"]
    assister = body.get('assister')
    assist_type = body.get('assist_type',"")
    
    type = body.get('type','')
    minutes = body.get('minutes','')

@fcatimer
async def retrieve_match_by_id(event,context):
    await lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    queryParameters = event.get("queryStringParameters",{})
    match_id = pathParameters["match_id"]
    headers = event['headers']
    etag = headers.get('etag',None)
    print(f"USER HEADERS {headers}")
    refresh= None
    if(queryParameters):
        refresh = queryParameters.get("refresh",None)
    print(f"QUERY PARAMETERS: {queryParameters}")
    matches = []

    try:
        response = await matches_backend.getMatchFromDB(match_id)
        api_helper.make_api_response(200,response)
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        print(errors)
        response = api_helper.make_api_response(400,None,errors)
        return response
    except ValueError as e:
        print(e)
        response = api_helper.make_api_response(400,None)
        return response





@fcatimer
async def updateStatus(event,context):
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    status = pathParameters["status"]
    matches_backend.updateStatus(match_id,status)

    await deleteEtag(match_id,'matches')
    response = api_helper.make_api_response(200,{})






