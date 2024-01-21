
from pydantic import TypeAdapter
from classes import Player
from config import app_config
import api_helper
import team_backend
from player_data import save_player_season,save_player,retrieve_players_by_team,delete_player,retrieve_player,squad_size_by_team
from etag_manager import isEtaggged,deleteEtag,setEtag,getLatestObject
import functools
import time
from cache_paths import Paths
import boto3
import asyncio
import hashlib
import json
import firebase_admin
from firebase_admin import credentials, firestore
from timeit import timeit

@timeit
async def create_players(name, team_id):
    
        request_player = Player(name=name,team_id=team_id)
        PlayerValidator = TypeAdapter(Player)

        try:
            new_player = PlayerValidator.validate_python(request_player)
            id = await save_player(new_player)
            player_season_id = await save_player_season(id,team_id)
            await team_backend.updateTeamCache(team_id)
            await updatePlayerCache(team_id)
            result = await retrieve_player(player_season_id)
            return result[0]

        except Exception as e:
            raise

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

@timeit
async def updatePlayerCache(team_id):
    print("TRIGGERING PLAYERS CACHE")
    await deleteEtag(team_id,'players')
    event = {
        "id":team_id,
        "path":Paths.cachePlayers.value
    }
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
    FunctionName=app_config.cache_handler,  # Name of the target Lambda
    InvocationType='Event',
    Payload=json.dumps(event)  # Asynchronous invocation
    ) 
    print("FINISHED TRIGGERING PLAYERS CACHE")

