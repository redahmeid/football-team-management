import json
from pydantic import TypeAdapter, ValidationError, BaseModel
from typing import List
from config import app_config
import api_helper
import response_errors
import team_backend
from matches_data import retrieve_match_by_id,save_team_fixture,retrieve_matches_by_team,retrieve_next_match_by_team,update_match_status
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
from match_planning_backend import list_matches_by_team_backend,create_match_backend
from etag_manager import isEtaggged,deleteEtag,setEtag,getLatestObject
import functools
import time
import asyncio
import hashlib
import json

import firebase_admin
from firebase_admin import credentials, firestore
from timeit import timeit
from cache_trigger import updateTeamCache,updateMatchCache, updateUserCache


async def create_fixtures(event, context):
    lambda_handler(event,context)
    body =json.loads(event["body"])
    print(body)
    pathParameters = event["pathParameters"]
    team_id = pathParameters["team_id"]
    
    
    matches = body["matches"]
    created_matches = []
    for match in matches:
       
        try:
            result = await create_match_backend(match,team_id)
            await updateTeamCache(team_id)
            await updateMatchCache(result.match.id)
            await updateUserCache(getEmailFromToken(event,context))
            created_matches.append(result.model_dump())
        except ValidationError as e:
            errors = response_errors.validationErrorsList(e)
            response = api_helper.make_api_response(400,None,errors)
        except ValueError as e:
            response = api_helper.make_api_response(400,None)

    
    response = api_helper.make_api_response(200,created_matches)
    return response
    
async def list_matches_by_team(event, context):
    team_id = event["pathParameters"]["team_id"]
    
    response =  await list_matches_by_team_backend(team_id)
    return api_helper.make_api_response(200,response)

@timeit
async def time_played(event,context):
    lambda_handler(event,context)
    
    match_id = event["pathParameters"]["match_id"]
    response = await match_planning_backend.how_long_played(match_id)
    return api_helper.make_api_response(200,{"player":response})


@timeit
async def retrieve_match_by_id(event,context):
    lambda_handler(event,context)
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
        if(refresh):
            etag=None
        if(etag):
            isEtag = await isEtaggged(match_id,'matches',etag)
            if(isEtag):
                response = api_helper.make_api_response_etag(304,result={},etag=etag)
                return response 
                
            else:
                return await getMatchFromDBAPIResponse(match_id,refresh)
        else:
               return await getMatchFromDBAPIResponse(match_id,refresh)

    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        print(errors)
        response = api_helper.make_api_response(400,None,errors)
        return response
    except ValueError as e:
        print(e)
        response = api_helper.make_api_response(400,None)
        return response
@timeit
async def getMatchFromDBAPIResponse(match_id,refresh:str):
    matches = []
    
    if(refresh is not None):
        match = await matches_backend.getMatchFromDBRefresh(match_id,refresh)
    else:
        match = await matches_backend.getMatchFromDB(match_id)
    
    
    matches.append(match["result"])
    etag = match["etag"]
    return api_helper.make_api_response_etag(200,matches,etag)    




@timeit
async def retrieve_match_planned_lineups(event,context):
    lambda_handler(event,context)
    
    match_id = event["pathParameters"]["match_id"]
    headers = event['headers']
    etag = headers.get('etag',None)
    print(f"USER HEADERS {headers}")
    
    matches = []

    try:
        if(etag):
            isEtag = await isEtaggged(match_id,'planned_lineups',etag)
            if(isEtag):
                response = api_helper.make_api_response_etag(304,result={},etag=etag)
                return response 
                
            else:
                return await getMatchPlannedLineupsFromDB(match_id)
        else:
                return await getMatchPlannedLineupsFromDB(match_id)

    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        print(errors)
        response = api_helper.make_api_response(400,None,errors)
        return response
    except ValueError as e:
        print(e)
        response = api_helper.make_api_response(400,None)
        return response
@timeit
async def getMatchPlannedLineupsFromDB(match_id):

    latest_planned_lineups = await getLatestObject(match_id,'planned_lineups')
    if(latest_planned_lineups):
        object = json.loads(latest_planned_lineups["object"])
    else:
        latest_planned_lineups = await matches_backend.getPlannedLineupsFromDB(match_id)
        object = latest_planned_lineups["result"]
    
    
    etag = latest_planned_lineups["etag"]
    
    
    
    response = api_helper.make_api_response_etag(200,object,etag)
    # get the user

    return response

@timeit
async def retrieve_match_actual_lineups(event,context):
    lambda_handler(event,context)
    
    match_id = event["pathParameters"]["match_id"]
    headers = event['headers']
    etag = headers.get('etag',None)
    print(f"USER HEADERS {headers}")
    
    matches = []

    try:
        if(etag):
            isEtag = await isEtaggged(match_id,'actual_lineups',etag)
            if(isEtag):
                response = api_helper.make_api_response_etag(304,result={},etag=etag)
                return response 
                
            else:
                return await getMatchActualLineupsFromDB(match_id)
        else:
                return await getMatchActualLineupsFromDB(match_id)

    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        print(errors)
        response = api_helper.make_api_response(400,None,errors)
        return response
    except ValueError as e:
        print(e)
        response = api_helper.make_api_response(400,None)
        return response
@timeit
async def getMatchActualLineupsFromDB(match_id):
    
    matches = await match_day_data.retrieveAllActualLineups(match_id)
    
    etag = await setEtag(match_id,'actual_lineups',matches)
    
    response = api_helper.make_api_response_etag(200,matches,etag)
    # get the user
    
    return response

@timeit
async def retrieve_match_current_lineup(event,context):
    lambda_handler(event,context)
    
    match_id = event["pathParameters"]["match_id"]
    headers = event['headers']
    etag = headers.get('etag',None)
    print(f"USER HEADERS {headers}")
    
    matches = []

    try:
        if(etag):
            isEtag = await isEtaggged(match_id,'current_lineup',etag)
            if(isEtag):
                response = api_helper.make_api_response_etag(304,result={},etag=etag)
                return response 
                
            else:
                response =  await matches_backend.getMatchCurrentLineups(match_id)
        else:
                response =  await matches_backend.getMatchCurrentLineups(match_id)
        
        return api_helper.make_api_response_etag(200,response["object"],response["etag"])

    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        print(errors)
        response = api_helper.make_api_response(400,None,errors)
        return response
    except ValueError as e:
        print(e)
        response = api_helper.make_api_response(400,None)
        return response




@timeit
async def updateStatus(event,context):
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    status = pathParameters["status"]
    matches_backend.updateStatus(match_id,status)

    await deleteEtag(match_id,'matches')
    response = api_helper.make_api_response(200,{})


async def next_match_by_team(event, context):
    team_id = event["pathParameters"]["team_id"]
    
    matches = []
    
    try:
        for match in await retrieve_next_match_by_team(team_id):
            self_url = response_classes.getMatchUrl(team_id,match.id)
            self = response_classes.Link(link=self_url,method="get")
            links = {"self":self}
            match_response = response_classes.MatchResponse(match=match,links=links).model_dump()
            matches.append(match_response)
        if(len(matches)==0):
            response = api_helper.make_api_response(404,None)
        else:
            response = api_helper.make_api_response(200,matches)
        
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        print(errors)
        response = api_helper.make_api_response(400,None,errors)
        return response
    except ValueError as e:
        print(e)
        response = api_helper.make_api_response(400,None)
        return response
            
    
    
    return response



