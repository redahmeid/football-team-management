
import asyncio

from team_data import retrieve_teams_by_user_id

from team_backend import retrieveTeamResponse
from player_backend import getGuardianPlayersFromDB
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
import functools
import time
import asyncio
import hashlib
from player_data import retrieve_player
import json
import team_backend
from cache_trigger import updateTeamCache
from roles_data import retrieve_player_roles_by_user_id
from secrets_util import getEmailFromToken, lambda_handler
import api_helper
from etag_manager import isEtaggged,setEtag,getLatestObject,deleteEtag
from config import app_config
from cache_paths import Paths
from fcatimer import fcatimer
def custom_sort(item):
    return int(item.ageGroup[1:])

@fcatimer
async def setupHomepage(email):
    
    logger.info("START")
    teams_list = []
    result = await retrieve_teams_by_user_id(email)
    
    
    
    
    return result['teams']


@fcatimer
async def getUserInfoFromDB(email):

    cached_object = await getLatestObject(email,'users')

    if(cached_object):
       etag = cached_object["etag"]
       teams_list = json.loads(cached_object["object"])
    else:
        teams_list = await setupHomepage(email)
        etag = await setEtag(email,'users',teams_list)
    
    response = api_helper.make_api_response_etag(200,teams_list,etag)
    print("RESPONSE FROM GETUSERINFOFROMDB ")
    print(response)
    # get the user
    
    return response

@fcatimer
async def setupHomepageV2(email):
    
    logger.info("START")
    teams_list = []
    result = await retrieve_teams_by_user_id(email)
    players = await getGuardianPlayersFromDB(email)
    return {"teams":result,"players":players["result"]}


@fcatimer
async def getUserInfoFromDBV2(email):

    cached_object = await getLatestObject(email,'users')

    if(cached_object):
       etag = cached_object["etag"]
       teams_list = json.loads(cached_object["object"])
    else:
        teams_list = await setupHomepageV2(email)
        etag = await setEtag(email,'users',teams_list)
    
    response = api_helper.make_api_response_etag(200,teams_list,etag)
    print("RESPONSE FROM GETUSERINFOFROMDB ")
    print(response)
    # get the user
    
    return response

