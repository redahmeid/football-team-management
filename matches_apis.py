import json
from pydantic import TypeAdapter, ValidationError, BaseModel

from classes import Team, Match,PlayerMatch
from config import app_config
import api_helper
import response_errors
from matches_data import retrieve_match_by_id,save_team_fixture,retrieve_matches_by_team,retrieve_next_match_by_team
import response_classes
from data_utils import convertMatchDatatoMatchResponse,convertPlayerDataToLineupPlayerResponse
from roles import Role
from auth import check_permissions
import match_day_data
import match_responses
import matches_state_machine
import exceptions
from secrets_util import lambda_handler

def create_fixtures(event, context):
    body =json.loads(event["body"])
    print(body)
    team_id = event["pathParameters"]["team_id"]
    
    matches = body["matches"]
    created_matches = []
    for match in matches:
        request_player = Match(opposition=match["opposition"],homeOrAway=match["homeOrAway"],date=match["date"],length=match["length"],status="draft",team_id=team_id)
        MatchValidator = TypeAdapter(Match)

        try:
            new_match = MatchValidator.validate_python(request_player)
            result = retrieve_match_by_id(save_team_fixture(new_match))
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
    
def list_matches_by_team(event, context):
    team_id = event["pathParameters"]["team_id"]
    
    matches = []
    for match in retrieve_matches_by_team(team_id):
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

    response = api_helper.make_api_response(200,matches)
    return response

def next_match_by_team(event, context):
    team_id = event["pathParameters"]["team_id"]
    
    matches = []
    
    try:
        for match in retrieve_next_match_by_team(team_id):
            self_url = match_responses.getMatchUrl(team_id,match.id)
            self = match_responses.Link(link=self_url,method="get")
            links = {"self":self}
            match_response = match_responses.MatchResponse(match=match,links=links).model_dump()
            matches.append(match_response)
        
            
        
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        print(errors)
        response = api_helper.make_api_response(400,None,errors)
        return response
    except ValueError as e:
        print(e)
        response = api_helper.make_api_response(400,None)
        return response
            
    
    response = api_helper.make_api_response(200,matches)
    return response

def update_match_status_handler(event,context):
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
       
        if(check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
             result =  internal_update_status(match_id=match_id,status=matches_state_machine.MatchState(status))
             response = api_helper.make_api_response(200,{"rows_updated":result})
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

def internal_update_status(match_id,status:matches_state_machine.MatchState,minute):
    result = match_day_data.update_match_status(match_id=match_id,status=status.value,minute=minute)
    
    return result
       
    
# def retrieve_starting_lineup(event,context):
#     lambda_handler(event,context)
#     pathParameters = event["pathParameters"]
#     match_id = pathParameters["match_id"]

#     team_id = pathParameters["team_id"]
#     acceptable_roles = [Role.admin.value,Role.coach.value,Role.parent.value]
#     try:
       
#         if(check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
#              result = match_day_data.retrieve_starting_lineup(match_id=match_id)
#              convertPlayerDataToLineupPlayerResponse(response)
#              response = api_helper.make_api_response(200,{"rows_updated":result})
#              return response
#         else:
#             response = api_helper.make_api_response(403,None,"You do not have permission to edit this match")
#             return response
#     except exceptions.AuthError as e:
#         response = api_helper.make_api_response(401,None,e)
#         return response
#     except ValidationError as e:
#         response = api_helper.make_api_response(400,None,e)
#         return response
#     except Exception as e:
#         response = api_helper.make_api_response(500,None,e)
#         return response

# def convertMatchDayDataToLineupPlayerResponse(player,baseUrl) -> response_classes.SelectedPlayerResponse:
    
#     id = player["ID"]
#     selection_id = player["ID"]
#     name = player["Name"]
#     position=position
#     live = player["live"]
#     url = "%s/players/%s"%(baseUrl,id)
#     if(live == None):
#         live = True
#     self = response_classes.Link(link=url,method="get")
    
    
    # subOnOff = response_classes.Link(link=url,method="patch")
    # response =  response_classes.SelectedPlayerResponse(id=id,selectionId=selection_id,name=name,live=live,self=self,position=position,toggleStarting=subOnOff,isSelected=isSelected)
    # print("Convert player %s"%(response))
    # return response.model_dump()
