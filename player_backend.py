
from pydantic import TypeAdapter
from classes import Player
from config import app_config
import api_helper
from player_data import save_player_season,save_player,retrieve_players_by_team,delete_player,retrieve_player,squad_size_by_team
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
from timeit import timeit
import cache_trigger

@timeit
async def create_players(name, team_id):
    
        request_player = Player(name=name,team_id=team_id)
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


@timeit
async def addGuardian(email,player_id,team_id):
    user_id = await retrieve_user_id_by_email(email)
    print(user_id)
    user = Guardian(email=email,player_id=player_id,team_id=team_id)
    player = await player_data.retrieve_player(player_id)
    if(user_id):
        
        await save_guardian_role(user)
        template_data = {
            "player": player[0]["info"]["name"],
        }
        template_id = 'd-d953ef3608354d49bde38c7d7e3843fa'
        # await send_email_with_template(email,template_id,template_data)
    else:
        user_id = await save_user("",email,"")
        
        await save_guardian_role(user)
        template_data = {
            "player": player[0]["info"]["name"],
        }
        template_id = 'd-9ba5fab4e96a4a56819aeba57916356f'
        # await send_email_with_template(email,template_id,template_data)
        
    
    return user


@timeit
async def getPlayersFromDB(team_id):
    cached_object = await getLatestObject(team_id,'players')
    teams = []
    if(cached_object):
       etag = cached_object["etag"]
       players = json.loads(cached_object["object"])
    else:
        players = await retrieve_players_by_team(team_id)
        etag = await setEtag(team_id,'players',players)
    response = api_helper.make_api_response_etag(200,players,etag)
    return response


