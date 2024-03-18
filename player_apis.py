import json
from pydantic import TypeAdapter, ValidationError
from secrets_util import lambda_handler, getEmailFromToken
from classes import Player
from exceptions import AuthError
from config import app_config
import api_helper
import response_errors
import response_classes
import team_backend
from player_data import save_player,retrieve_players_by_team,delete_player,retrieve_player,squad_size_by_team
from roles_data import retrieve_role_by_user_id_and_team_id
from users_data import retrieve_user_id_by_email
from etag_manager import deleteEtag
from roles import Role
from auth import check_permissions
from firebase_admin import credentials
from firebase_admin import messaging
import notifications
import player_backend
from etag_manager import isEtaggged,deleteEtag,setEtag
import functools
import time
import asyncio
import hashlib
import json
import firebase_admin
from firebase_admin import credentials, firestore
from timeit import timeit
import cache_trigger

@timeit    
async def create_players(event, context):
    await lambda_handler(event,context)
    body =json.loads(event["body"])
    
    team_id = event["pathParameters"]["team_id"]
    
    players = body["players"]
    created_players = []
    i = 0
    for player in players:
        result = await player_backend.create_players(player,team_id)
        created_players.append(result)
    await cache_trigger.updatePlayerCache(team_id)
    data = {
        "link":f"/teams/{team_id}",
        "team_id":team_id,
        "action":"new_players",
        "silent":"True"
    }
    await notifications.sendNotificationUpdatesLink(getEmailFromToken(event,context),"New players","New players",'team',data)
    response = api_helper.make_api_response(200,created_players)
    return response

@timeit
async def addGuardiansToPlayer(event,context):
    await lambda_handler(event,context)
    acceptable_roles = [Role.admin.value,Role.coach.value]
    team_id = event["pathParameters"]["team_id"]
    player_id = event["pathParameters"]["player_id"]
    body =json.loads(event["body"])
    
    emails = body["emails"]

    if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
        results = []
        for email in emails:
           
            result = await player_backend.addGuardian(email,player_id,team_id)
            await cache_trigger.updateGuardiansPlayerCache(email)
            await cache_trigger.updateUserCache(email)
            results.append(result.model_dump())
        await cache_trigger.updateTeamCache(team_id)
        await cache_trigger.updatePlayerCache(team_id)
        
        data = {
            "link":f"/players/{player_id}",
            "team_id":f"{team_id}",
            "action":"new_guardian",
            "silent":"False"
        }
        await notifications.sendNotificationUpdatesLink(getEmailFromToken(event,context),f"Guardian has been added to ",f"New coach added to {team.name}",'team',data)
        response = api_helper.make_api_response(200,results)
    else:
            response = api_helper.make_api_response(403,None,"You do not have permission to edit this match")
    return response

@timeit
async def list_players_by_team(event, context):
    await lambda_handler(event,context)
    acceptable_roles = [Role.admin.value,Role.coach.value,Role.parent.value]
    team_id = event["pathParameters"]["team_id"]
    if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
        players = []
        try:
            headers = event['headers']
            etag = headers.get('etag',None)
            if(etag):
                print("ETAG EXISTS")
                isEtag = await isEtaggged(team_id,'players',etag)
                if(isEtag):
                    response = api_helper.make_api_response_etag(304,result={},etag=etag)
                    return response 
                else:
                    return await player_backend.getPlayersFromDB(team_id)
            else:
                return await player_backend.getPlayersFromDB(team_id)
        except ValidationError as e:
            errors = response_errors.validationErrorsList(e)
            response = api_helper.make_api_response(400,None,errors)
        except ValueError as e:
            response = api_helper.make_api_response(400,None,None)
    else:
        response = api_helper.make_api_response(403,None,"You do not have permission to view the players")
        return response


@timeit
async def list_players_by_guardian(event, context):
    await lambda_handler(event,context)
    acceptable_roles = [Role.admin.value,Role.coach.value,Role.parent.value]
    
    
    players = []
    
    try:
        email = getEmailFromToken(event,context)
        headers = event['headers']
        etag = headers.get('etag',None)
        if(etag):
            print("ETAG EXISTS")
            isEtag = await isEtaggged(email,'guardian_players',etag)
            if(isEtag):
                response = api_helper.make_api_response_etag(304,result={},etag=etag)
                return response 
            else:
                players = await player_backend.getGuardianPlayersFromDB(email)
                response = api_helper.make_api_response_etag(200,players["result"],players["etag"])
                return response
        else:
            players = await player_backend.getGuardianPlayersFromDB(email)
            response = api_helper.make_api_response_etag(200,players["result"],players["etag"])
            return response
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        response = api_helper.make_api_response(400,None,errors)
    except ValueError as e:
        response = api_helper.make_api_response(400,None,None)
    except AuthError as e:
        response = api_helper.make_api_response(403,None,None)
   
    

def delete_player_from_team(event, context):
   
    
    player_id = event["pathParameters"]["player_id"]
    
    players = []
    

    try:
        delete_player(player_id)
        save_response = {"message":"Player %s has been deleted"%(player_id)}
        save_response["link"] = "/players/%s"%(player_id)
        players.append(save_response)
        actions = list()
            
        
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        response = api_helper.make_api_response(400,None,None,errors)
    except ValueError as e:
        response = api_helper.make_api_response(400,None,None,None)

    
    response = api_helper.make_api_response(200,players,actions)
    return response

# ID varchar(255),"\
        # "Name varchar(255) NOT NULL,"\
        # "Team_ID varchar(255) NOT NULL,"\
        # "Email varchar(255),"\
        # "live varchar(255),"\
def convertPlayerDataToPlayerResponse(player) -> response_classes.PlayerResponse:
    
    id = player["ID"]
    baseTeamUrl = "/players/%s"%(id)
    name = player["Name"]
    live = player["live"]
    if(live == None):
        live = True
    self = response_classes.Link(link=baseTeamUrl,method="get")
    deletePlayer = response_classes.Link(link=baseTeamUrl,method="delete")
    response =  response_classes.PlayerResponse(id=id,name=name,live=live,self=self,deletePlayer=deletePlayer)
    print("Convert player %s"%(response))
    return response.model_dump()

