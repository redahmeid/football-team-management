import json
from pydantic import TypeAdapter, ValidationError
from data_utils import convertMatchDatatoMatchResponse, convertPlayerDataToPlayerResponse, convertTeamDataToTeamResponse,convertPlayerDataToLineupPlayerResponse
from classes import User,Team,TeamUser
import response_classes
from config import app_config
import exceptions
from users_data import retrieve_user_id_by_email
from player_data import retrieve_players_by_team
from team_data import save_team,retrieve_team_by_id
from matches_data import retrieve_match_by_id
from match_day_data import save_match_day_player,retrieve_starting_lineup,delete_match_day_player
from secrets_util import getEmailFromToken, lambda_handler
import api_helper
from roles_data import save_role,retrieve_role_by_user_id_and_team_id
import roles

baseUrl = "/bff/match_details"

def enter_screen(event, context):
    lambda_handler(event,context)
    query_parameters = event["queryStringParameters"]
    team_id = query_parameters["team_id"]
    match_id = query_parameters["match_id"]
    players = []
    acceptable_roles = ["admin"]
    try:
        user_id = retrieve_user_id_by_email(getEmailFromToken(event,context))
        if(check_permissions(user_id=user_id,team_id=team_id,acceptable_roles=acceptable_roles)):
                print("CHECK PERMISSIONS")
                playersList = retrieve_players_by_team(team_id)
                print("PLAYERS LIST %s"%playersList)
                selected_players = retrieve_starting_lineup(match_id=match_id)
                print(selected_players)
                selected_players_dict = {}
                for selected_player in selected_players:
                    selected_players_dict[selected_player["Player_ID"]]=selected_player
                print(selected_players_dict)
                selected_player_ids = list_start_line_up_player_ids(selected_players)
                print("SELECTED PLAYERS LIST %s"%selected_player_ids)
                url = baseUrl
                selection_id = None
                print("BASEURL %s"%url)
                for player in playersList:
                    isSelected = (player["ID"] in selected_player_ids)
                    position = ""
                    if(isSelected): 
                        print("ISSELECTED %s"%isSelected)
                        print(selected_players_dict.get(player["ID"]))
                        position = selected_players_dict.get(player["ID"])["Position"]
                        selection_id = selected_players_dict.get(player["ID"])["ID"]
                        
                    players.append(convertPlayerDataToLineupPlayerResponse(player,isSelected,url,position,team_id,match_id,selection_id))
                
                match = retrieve_match_by_id(match_id)
                new_match = convertMatchDatatoMatchResponse(match)
                print("IS HERE 1")
                match_day_response = response_classes.MatchDayResponse(match=new_match,availablePlayers=players).model_dump()
                print("IS HERE 2")
                response = api_helper.make_api_response(200,match_day_response)
                print("IS HERE 1 %s"%response)
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

def select_remove_from_starting_lineup(event, context):
    lambda_handler(event,context)
    query_parameters = event["queryStringParameters"]
    team_id = query_parameters["team_id"]
    match_id = query_parameters["match_id"]
    player_id = query_parameters["player_id"]
    position = query_parameters.get("position",None)
    selection_id = query_parameters.get("selectionId",None)
    players = []
    acceptable_roles = ["admin","coach"]
    team_players = retrieve_players_by_team(team_id)
    team_player_ids = list_of_player_ids_from_db(team_players)
    try:
        selected_players = retrieve_starting_lineup(match_id=match_id)
        selected_player_ids = list_start_line_up_player_ids(selected_players)
        user_id = retrieve_user_id_by_email(getEmailFromToken(event,context))
        if(check_permissions(user_id=user_id,team_id=team_id,acceptable_roles=acceptable_roles)):
                if(player_id in team_player_ids):

                    if(player_id in selected_player_ids):
                        delete_match_day_player(selection_id) 
                        response = api_helper.make_api_response(200,{"successfully removed from starting lineup"})
                    else:
                        selection_id = save_match_day_player(match_id=match_id,player_id=player_id,subbed_on=0,subbed_off=1,position=position)
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
        response = api_helper.make_api_response(500,None,e)
        return response

def check_permissions(user_id,team_id,acceptable_roles):
    roles = retrieve_role_by_user_id_and_team_id(user_id=user_id,team_id=team_id)
    for role in roles:
        if(role["Role"] in acceptable_roles):
            return True
    return False

def list_of_player_ids(players:list):
   return [item["id"] for item in players]
def list_start_line_up_player_ids(players:list):
   return [item["Player_ID"] for item in players]

def list_of_player_ids_from_db(players:list):
   return [item["ID"] for item in players]
