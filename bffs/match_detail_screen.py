import json
from pydantic import TypeAdapter, ValidationError
from data_utils import convertMatchDatatoMatchResponse, convertPlayerDataToLineupPlayerResponse
from classes import User,Team,TeamUser
import response_classes
from config import app_config
import exceptions
from typing import List
from player_data import retrieve_players_by_team

from matches_data import retrieve_match_by_id,update_match_status
from match_day_data import save_match_day_player,retieve_lineup_by_minute, retrieve_latest_minute,retrieve_all_lineups
import matches_apis
from secrets_util import lambda_handler
import api_helper
from matches_apis import update_match_status_handler, internal_update_status
from auth import check_permissions
from roles import Role
import matches_state_machine
import player_responses
import match_responses

baseUrl = "/teams/%s/matches/%s"
acceptable_roles = [Role.admin.value,Role.coach.value]

def enter_screen(event, context):
    lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    team_id = pathParameters["team_id"]
    match_id = pathParameters["match_id"]
    players = []
    
    try:
        if(check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
            match = retrieve_match_by_id(match_id)[0]
            print(match)
            print(match.status)
            if(match.status==matches_state_machine.MatchState.lineup_confirmed or match.status==matches_state_machine.MatchState.substitutions):
                print(f"############# enter_lineup_by_minute {match.status}")
                return enter_lineup_by_minute(event,context,match)
            elif(match.status==matches_state_machine.MatchState.plan_confirmed):
                print(f"############# enter_actual_match {match.status}")
                return enter_actual_match(event,context,match)
            else:
                playersList = retrieve_players_by_team(team_id)

                
                
                self_url = match_responses.getMatchUrl(team_id,match.id)
                self = match_responses.Link(link=self_url,method="get")
                submit_starting_lineup_url = match_responses.getMatchUrl(team_id,match.id)
                submit_starting_lineup_url = "%s/lineup_confirmed"%submit_starting_lineup_url
                submit_starting_lineup =match_responses.Link(link=submit_starting_lineup_url,method="post")
                links = {"self":self,"submit_lineup":submit_starting_lineup}
                match_day_response = match_responses.MatchResponse(match=match,players=playersList,links=links).model_dump()
                match_day_responses = [match_day_response]
                
               
                
                response = api_helper.make_api_response(200,match_day_responses)
                print("match_detail_screnn.py.enter_screen %s"%response)
                
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
        print("################## Exception ###############")
        print(e)
        response = api_helper.make_api_response(500,None,e)
        return response
    


def enter_lineup_by_minute(event,context,match):
    lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    team_id = pathParameters["team_id"]
    match_id = pathParameters["match_id"]
    query_parameters = event.get("queryStringParameters", {})

    if query_parameters is not None and 'minute' in query_parameters:
        minute = query_parameters['minute']
    else:
        minute = retrieve_latest_minute(match_id)
    
    print(f"############# MATCH ID {match_id}")
    print(f"############# MATCH {match}")
    print(f"############# MINUTE {minute}")
    print(f"############# TEAM_ID {team_id}")
    try:
        if(check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
                

                selected_players = retrieve_all_lineups(match_id=match_id)
                
                url = match_responses.getMatchUrl(team_id,match_id)
                
                
                submit_first_subs = match_responses.Link(link=f'{url}/{matches_state_machine.MatchState.substitutions.value}',method="post")
                confirm_plan = match_responses.Link(link=f'{url}/{matches_state_machine.MatchState.plan_confirmed.name}',method="post")
                links = {"submit_lineup":submit_first_subs,"confirm_plan":confirm_plan }
                match_day_response = match_responses.MatchResponse(match=match,players=selected_players,links=links).model_dump()
                match_day_responses = []
                match_day_responses.append(match_day_response)

                response = api_helper.make_api_response(200,match_day_responses)
                print("match_detail_screnn.py.enter_screen_lineup_confirmed %s"%response)
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
        print("################## Exception ###############")
        print(e)
        response = api_helper.make_api_response(500,None,e)
        return response


def enter_actual_match(event,context,match):
    lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    team_id = pathParameters["team_id"]
    match_id = pathParameters["match_id"]
    query_parameters = event.get("queryStringParameters", {})

    if query_parameters is not None and 'minute' in query_parameters:
        minute = query_parameters['minute']
    else:
        minute = retrieve_latest_minute(match_id)
    
    print(f"############# MATCH ID {match_id}")
    print(f"############# MATCH {match}")
    print(f"############# MINUTE {minute}")
    print(f"############# TEAM_ID {team_id}")
    try:
        if(check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
                

                selected_players = retrieve_all_lineups(match_id=match_id)
                
                url = match_responses.getMatchUrl(team_id,match_id)
                
                
                submit_first_subs = match_responses.Link(link=f'{url}/{matches_state_machine.MatchState.actual_substitutions.value}',method="post")
                end_match = match_responses.Link(link=f'{url}/{matches_state_machine.MatchState.actual_match_ended.name}',method="post")
                start_match = match_responses.Link(link=f'{url}/{matches_state_machine.MatchState.actual_match_started.name}',method="post")
                links = {"submit_subs":submit_first_subs,"end_match":end_match,"start_match":start_match}
                match_day_response = match_responses.MatchResponse(match=match,players=selected_players,links=links).model_dump()
                match_day_responses = []
                match_day_responses.append(match_day_response)

                response = api_helper.make_api_response(200,match_day_responses)
                print("match_detail_screnn.py.enter_actual_match %s"%response)
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
        print("################## Exception ###############")
        print(e)
        response = api_helper.make_api_response(500,None,e)
        return response




def submit_lineup_by_minute(event,context):
    lambda_handler(event,context)
    queryParameters = event["queryStringParameters"]
    pathParameters = event["pathParameters"]
    team_id = pathParameters["team_id"]
    status = pathParameters["status"]
    if(status==matches_state_machine.MatchState.plan_confirmed.value):
        return confirm_plan(event,context)
    else:
        match_id = pathParameters["match_id"]
        minute = (queryParameters['minute']) if queryParameters['minute'] else retrieve_latest_minute(match_id)
        body =json.loads(event["body"])
        players = body["players"]
        try:
        
            if(check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
                for player in players:
                    print(player)
                    new_player = player_responses.PlayerResponse(**player)
                    selection_id = save_match_day_player(match_id=match_id,player_id=new_player.info.id,minute=minute,position=new_player.selectionInfo.position,status=status)
                    print(selection_id)
                internal_update_status(match_id=match_id,status=matches_state_machine.MatchState(status),minute=minute)
                return enter_screen(event,context)
                
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

def confirm_plan(event,context):
    lambda_handler(event,context)
    
    pathParameters = event["pathParameters"]
    team_id = pathParameters["team_id"]
    status = pathParameters["status"]
    match_id = pathParameters["match_id"]

    try:
       
        if(check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
             
             update_match_status(match_id=match_id,status=matches_state_machine.MatchState(status))
             return enter_screen(event,context)
             
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
