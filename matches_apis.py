import json
from pydantic import TypeAdapter, ValidationError, BaseModel

from classes import Team, Match,PlayerMatch
from config import app_config
import api_helper
import response_errors
from matches_data import retrieve_match_by_id,save_team_fixture,retrieve_matches_by_team,retrieve_next_match_by_team,update_match_status
import response_classes
from data_utils import convertMatchDatatoMatchResponse,convertPlayerDataToLineupPlayerResponse
from roles import Role
from auth import check_permissions
import match_detail_screen
import match_responses
import asyncio
import matches_state_machine
import exceptions
from secrets_util import lambda_handler

async def create_fixtures(event, context):
    body =json.loads(event["body"])
    print(body)
    team_id = event["pathParameters"]["team_id"]
    
    matches = body["matches"]
    created_matches = []
    for match in matches:
        type = match.get("type",None)
        if(type):
            type = match_responses.MatchType(type)

        matchInfo = match_responses.MatchInfo(id="",opposition=match["opposition"],homeOrAway=match["homeOrAway"],date=match["date"],length=match["length"],status=matches_state_machine.MatchState.created.value,type=type)
        

        try:
            result = await retrieve_match_by_id(await save_team_fixture(matchInfo,team_id))
            self_url = match_responses.getMatchUrl(team_id,result[0].id)
            self = match_responses.Link(link=self_url,method="get")
            links = {"self":self}
            match_response = match_responses.MatchResponse(match=result[0],links=links).model_dump()
            created_matches.append(match_response)
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


async def list_matches_by_team_backend(team_id):
    matches = []
    for match in await retrieve_matches_by_team(team_id):
        try:
            self_url = match_responses.getMatchUrl(team_id,match.id)
            self = match_responses.Link(link=self_url,method="get")
            links = {"self":self}
            match_response = match_responses.MatchResponse(match=match,links=links).model_dump()
            
            matches.append(match_response)
        except ValidationError as e:
            print(e)
            errors = response_errors.validationErrorsList(e)
            print(errors)
            response = api_helper.make_api_response(400,None,errors)
            return response
        except ValueError as e:
            print(e)
            response = api_helper.make_api_response(400,None)
            return response
   
    return matches
async def next_match_by_team(event, context):
    team_id = event["pathParameters"]["team_id"]
    
    matches = []
    
    try:
        for match in await retrieve_next_match_by_team(team_id):
            self_url = match_responses.getMatchUrl(team_id,match.id)
            self = match_responses.Link(link=self_url,method="get")
            links = {"self":self}
            match_response = match_responses.MatchResponse(match=match,links=links).model_dump()
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

async def update_match_status_handler(event,context):
    lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    queryParameters = event["queryParameters"]
    match_id = pathParameters["match_id"]
    status = pathParameters["status"]
    team_id = pathParameters["team_id"]
    minute = queryParameters["minute"]
    acceptable_roles = [Role.admin.value,Role.coach.value]
    print(status)
    try:
       
        if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
             result =  await internal_update_status(match_id=match_id,status=matches_state_machine.MatchState(status))
             return await match_detail_screen.getMatch(event,context)
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

async def internal_update_status(match_id,status:matches_state_machine.MatchState,minute):
    
    return await update_match_status(match_id=match_id,status=status)

