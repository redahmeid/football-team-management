import json
from pydantic import TypeAdapter, ValidationError, BaseModel

from classes import Team, Match,PlayerMatch
from config import app_config
import api_helper
import response_errors
from matches_data import retrieve_match_by_id,save_team_fixture,save_planned_match_squad,retrieve_planned_match_squad, retrieve_fixture_team_size, retrieve_matches_by_team,retrieve_next_match_by_team
import response_classes
from data_utils import convertMatchDatatoMatchResponse
from roles import Role
from auth import check_permissions
import match_day_data
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
            result = convertMatchDatatoMatchResponse(retrieve_match_by_id(save_team_fixture(new_match)))
            
            created_matches.append(result)
            
                
            
        except ValidationError as e:
            errors = response_errors.validationErrorsList(e)
            response = api_helper.make_api_response(400,None)
        except ValueError as e:
            response = api_helper.make_api_response(400,None)

    
    response = api_helper.make_api_response(200,created_matches)
    return response

# {
    # player_id:""
    # start_time_minutes:0
    # end_time_minutes:10
    # position:"CM"
# }
def plan_match_squad(event,context):
    class PlayerMatch:
        def __init__(self, match_id, player_id,start_time_minutes,end_time_minutes,position):
            self.player_id = player_id
            self.start_time_minutes = start_time_minutes
            self.end_time_minutes = end_time_minutes
            self.match_id=match_id
            self.position = position
    


    body =json.loads(event["body"])
    
    match_id = event["pathParameters"]["match_id"]
    
    team_size = retrieve_fixture_team_size(match_id)

    players = body["players"]
    start_times = []
    for player in players:
        player_id = player["player_id"]
        start_time_minutes = player["start_time_minutes"]
        start_times.append(start_time_minutes)
        end_time_minutes = player["end_time_minutes"]
        position = player["position"]
    
    unique_start_times = list(set(start_times))
    on_pitch = list()
    for start_time in unique_start_times:
        def on_pitch_check(playerMatch):
            return playerMatch["start_time_minutes"] <= start_time and playerMatch["end_time_minutes"] > start_time
        on_pitch_filtered = list(filter(on_pitch_check,players))
        print("TEAM SIZE "+str(len(on_pitch_filtered)))
        print("TEAM SIZE "+str(team_size))
        if(len(on_pitch_filtered)!=team_size):
            return api_helper.make_api_response(400,None,None,[{"messages":"Team size is too small"}])
    
    for player in players:
        player_id = player["player_id"]
        start_time_minutes = player["start_time_minutes"]
        end_time_minutes = player["end_time_minutes"]
        position = player["position"]
        new_player = PlayerMatch(player_id=player_id,match_id=match_id,start_time_minutes=start_time_minutes,end_time_minutes=end_time_minutes,position=position)
        id = save_planned_match_squad(new_player)

    response = api_helper.make_api_response(200,match_id,None)

    return response
    
def list_matches_by_team(event, context):
    team_id = event["pathParameters"]["team_id"]
    
    matches = []
    for match in retrieve_matches_by_team(team_id):
        try:
            
            save_response =convertMatchDatatoMatchResponse(match)
            
            matches.append(save_response)
            
                
            
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

def next_match_by_team(event, context):
    team_id = event["pathParameters"]["team_id"]
    
    matches = []
    
    try:
        match = retrieve_next_match_by_team(team_id)
        save_response =convertMatchDatatoMatchResponse(match)
        matches.append(save_response)
        
            
        
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

def update_match_status(event,context):
    lambda_handler(event,context)
    body =json.loads(event["body"])
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    status = body["status"]
    team_id = body["team_id"]
    acceptable_roles = [Role.admin.value,Role.coach.value]
    try:
       
        if(check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
             result = match_day_data.update_match_status(match_id=match_id,status=status)
             response = api_helper.make_api_response(200,{"rows_updated":result})
             return response
        else:
            response = api_helper.make_api_response(403,None,"You do not have permission to edit this match")
            return response
    except exceptions.AuthError as e:
        response = api_helper.make_api_response(401,None,e)
        return response
    except ValidationError as e:
        response = api_helper.make_api_response(400,None,e)
        return response
    except Exception as e:
        response = api_helper.make_api_response(500,None,e)
        return response