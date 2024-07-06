
from pydantic import TypeAdapter
from classes import Player
import id_generator
from config import app_config
from team_data import retrieve_team_by_id
import api_helper
from player_data import save_player_season,save_player,retrieve_players_by_team_with_stats,delete_player,retrieve_player,squad_size_by_team
from etag_manager import isEtaggged,deleteEtag,setEtag,getLatestObject,getObject,updateDocument,whereContains,whereEqual
from roles import Role
from users_data import retrieve_user_id_by_email,save_user
from roles_data import save_role, save_guardian_role
import classes
import response_classes
import player_data
import time
from cache_paths import Paths
import boto3
import asyncio
import hashlib
import json
import firebase_admin
import classes
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
    
        id = id_generator.generate_random_number(7)
        request_player = classes.Player(info=classes.PlayerInfo(id=str(id),forename=forename,name=forename,surname=surname,team_id=team_id),guardians=[email])
        

        try:

            await updateDocument('players_store',str(id),request_player)

            fs_team = await getObject(team_id,'teams_store')
            if(fs_team):
                fs_team_dict = fs_team.get().to_dict()
                team = classes.Team(**fs_team_dict)
                
                team.squad.append(str(id))
                fs_team.update(team.model_dump())
            
            fs_user = await getObject(email,'users_store')
            if(fs_user):
                fs_user_dict = fs_user.get().to_dict()
                user = classes.User(**fs_user_dict)
                user.players.append(id)
                user.guardians.append(team_id)
                user.teams.append(team_id)
                fs_user.update(user.model_dump())
            else:
                 await updateDocument('users_store',email,classes.User(email=email,players=[id],guardians=[team_id],teams=[team_id]))

            return request_player.model_dump()

        except Exception as e:
            raise


@fcatimer
async def getPlayersByTeam(team_id):
    fs_players = await whereEqual('players_store','team_id',team_id)
    players = []
    for fs_player in fs_players:
        fs_player_dict = fs_player.to_dict()
        player = classes.Player(**fs_player_dict)
        players.append(player)
    response = api_helper.make_api_response(200,players)
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


