import json
from pydantic import TypeAdapter, ValidationError
from data_utils import convertMatchDatatoMatchResponse, convertPlayerDataToLineupPlayerResponse
from classes import User,Team,TeamUser
import response_classes
from config import app_config
import exceptions

from player_data import retrieve_players_by_team

from matches_data import retrieve_match_by_id
from match_day_data import save_match_day_player,retrieve_starting_lineup,delete_match_day_player
import matches_apis
from secrets_util import lambda_handler
import api_helper
from matches_apis import update_match_status
from auth import check_permissions
from roles import Role

baseUrl = "/teams/%s/matches/%s"
acceptable_roles = [Role.admin.value,Role.coach.value]

def enter_screen(event, context):
    lambda_handler(event,context)
    query_parameters = event["queryStringParameters"]
    team_id = query_parameters["team_id"]
    match_id = query_parameters["match_id"]
    players = []
    
    try:
        if(check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
               
                playersList = retrieve_players_by_team(team_id)
                
                selected_players = retrieve_starting_lineup(match_id=match_id)
                print(selected_players)
                selected_players_dict = {}
                for selected_player in selected_players:
                    selected_players_dict[selected_player["Player_ID"]]=selected_player
                print(selected_players_dict)
                selected_player_ids = list_start_line_up_player_ids(selected_players)
                
                url = baseUrl%(team_id,match_id)
                selection_id = None
                
                for player in playersList:
                    isSelected = (player["ID"] in selected_player_ids)
                    position = ""
                    if(isSelected): 
                        
                        position = selected_players_dict.get(player["ID"])["Position"]
                        selection_id = selected_players_dict.get(player["ID"])["ID"]
                        
                    players.append(convertPlayerDataToLineupPlayerResponse(player,isSelected,url,position,team_id,match_id,selection_id))
                match = retrieve_match_by_id(match_id)
                new_match = convertMatchDatatoMatchResponse(match)
                
                match_day_response = response_classes.MatchDayResponse(match=new_match,availablePlayers=players).model_dump()
                
                response = api_helper.make_api_response(200,match_day_response)
                
                return response
        else:
            response = api_helper.make_api_response(403,None,"You do not have permission to edit this match")
            return response
    except exceptions.AuthError as e:
        print("Auth Error %s"%e)
        response = api_helper.make_api_response(401,None,e)
        return response
    except ValidationError as e:
        print("Validation Error %s"%e)
        response = api_helper.make_api_response(400,None,e)
        return response
    except Exception as e:
        print("Exception %s"%e)
        response = api_helper.make_api_response(500,None,e)
        return response
def selections(event,context):
    query_parameters = event["queryStringParameters"]
    action = query_parameters["action"]
    if(action=="select_starting"):
        select_remove_from_starting_lineup(event,context)
    elif(action=="remove_starting"):
        select_remove_from_starting_lineup(event,context)

def select_remove_from_starting_lineup(event, context):
    lambda_handler(event,context)
    body =json.loads(event["body"])
    pathParameters = event["pathParameters"]
    team_id = pathParameters["team_id"]
    match_id = pathParameters["match_id"]
    player_id = pathParameters["player_id"]
    position = body.get("position",None)
    selection_id = body.get("selection_id",None)

    
    team_players = retrieve_players_by_team(team_id)
    team_player_ids = list_of_player_ids_from_db(team_players)
    try:
        selected_players = retrieve_starting_lineup(match_id=match_id)
        selected_player_ids = list_start_line_up_player_ids(selected_players)
        
        if(check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
                if(player_id in team_player_ids):

                    if(player_id in selected_player_ids):
                        delete_match_day_player(selection_id) 
                        response = api_helper.make_api_response(200,{"successfully removed from starting lineup"})
                    else:
                        selection_id = save_match_day_player(match_id=match_id,player_id=player_id,subbed_on=0,subbed_off=1,position=position)
                        update_match_status(event,context)
                        response = api_helper.make_api_response(200,{"selectionId":selection_id})
                    # get the user
                    return response
                else:
                    response = api_helper.make_api_response(400,None,"Not all players are part of this team - please check")
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
        response = api_helper.make_api_response(500,None,e.with_traceback(None))
        return response

def submit_starting_lineup(event,match_id,status,team_id):
   
    try:
       
        if(check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
             result = update_match_status(event=event,team_id=team_id,match_id=match_id,status=status)
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





def list_of_player_ids(players:list):
   return [item["id"] for item in players]
def list_start_line_up_player_ids(players:list):
   return [item["Player_ID"] for item in players]

def list_of_player_ids_from_db(players:list):
   return [item["ID"] for item in players]
