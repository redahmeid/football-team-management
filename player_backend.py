
from pydantic import TypeAdapter
from classes import Player
from config import app_config
from team_data import retrieve_team_by_id
import api_helper
from player_data import save_player_season,save_player,retrieve_players_by_team_with_stats,delete_player,retrieve_player,squad_size_by_team
from etag_manager import isEtaggged,deleteEtag,setEtag,getLatestObject
from roles import Role
from users_data import retrieve_user_id_by_email,save_user
from roles_data import save_role, save_guardian_role
from player_responses import PlayerResponse,Guardian
import player_data
import time
from cache_paths import Paths
import boto3
import asyncio
import hashlib
import json
import firebase_admin
from firebase_admin import credentials, firestore
from fcatimer import fcatimer
import cache_trigger
from email_sender import send_email_with_template

@fcatimer
async def create_players(name, team_id):
    
        request_player = Player(forename=name,team_id=team_id)
        PlayerValidator = TypeAdapter(Player)

        try:
            new_player = PlayerValidator.validate_python(request_player)
            id = await save_player(new_player)
            player_season_id = await save_player_season(id,team_id)
            
            await cache_trigger.updateTeamCache(team_id)
            await cache_trigger.updatePlayerCache(team_id)
            result = await retrieve_player(player_season_id)
            return result[0]

        except Exception as e:
            raise

@fcatimer
async def create_players_and_guardians(forename, surname, team_id,email):
    
        request_player = Player(forename=forename,name=forename,surname=surname,team_id=team_id)
        PlayerValidator = TypeAdapter(Player)

        try:
            new_player = PlayerValidator.validate_python(request_player)
            id = await save_player(new_player)
            player_season_id = await save_player_season(id,team_id)
            
            await cache_trigger.updateTeamCache(team_id)
            await cache_trigger.updatePlayerCache(team_id)
            result = await retrieve_player(player_season_id)
            await addGuardian(email,player_season_id,team_id)
            return result[0]

        except Exception as e:
            raise


@fcatimer
async def addGuardian(email,player_id,team_id):
    user_id = await retrieve_user_id_by_email(email)
    team = await retrieve_team_by_id(team_id)
    print(user_id)
    user = Guardian(email=email,player_id=str(player_id),team_id=team_id)
    player = await player_data.retrieve_player(player_id)
    if(user_id):
        
        await save_guardian_role(user)
        template_data = {
            "player": player[0]['info']['name'],
            "team": team.name
        }
        template_id = 'd-d84865ab98a44c9aa6770e86364df6e5'
        await send_email_with_template(email,template_id,template_data)
    else:
        user_id = await save_user("",email,"")
        
        await save_guardian_role(user)
        template_data = {
            "player": player[0]['info']['name'],
            "team": team.name
        }
        template_id = 'd-0904ad249669492fb6999ff0102742f1'
        await send_email_with_template(email,template_id,template_data)
        
    
    return user


@fcatimer
async def getPlayersFromDB(team_id):
    cached_object = await getLatestObject(team_id,'players')
    teams = []
    if(cached_object):
       etag = cached_object["etag"]
       players = json.loads(cached_object["object"])
    else:
        players = await retrieve_players_by_team_with_stats(team_id)
        etag = await setEtag(team_id,'players',players)
    response = api_helper.make_api_response_etag(200,players,etag)
    return response

@fcatimer
async def getGuardianPlayersFromDB(email):
    cached_object = await getLatestObject(email,'guardian_players')
    teams = []
    if(cached_object):
       etag = cached_object["etag"]
       players = json.loads(cached_object["object"])
    else:
        players = await player_data.retrieve_players_by_user(email)
        etag = await setEtag(email,'guardian_players',players)
    
    return {"result":players,"etag":etag}


