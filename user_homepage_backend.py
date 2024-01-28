
import asyncio

from team_data import retrieve_teams_by_user_id

from team_backend import retrieveTeamResponse
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
import functools
import time
import asyncio
import hashlib
import json
import team_backend
from cache_trigger import updateTeamCache
import boto3
from secrets_util import getEmailFromToken, lambda_handler
import api_helper
from etag_manager import isEtaggged,setEtag,getLatestObject,deleteEtag
from config import app_config
from cache_paths import Paths
from timeit import timeit
def custom_sort(item):
    return int(item.ageGroup[1:])

@timeit
async def setupHomepage(email):
    
    logger.info("START")
    teams_list = []
    teams = await retrieve_teams_by_user_id(email)
    
    for team in teams:
        team = await team_backend.getTeamFromDB(team.id)
        teams_list.append(team.model_dump())
        await updateTeamCache(team.id)
    
    
    logger.info(teams_list)
    logger.info("END")
    return teams_list


@timeit
async def getUserInfoFromDB(email):

    cached_object = await getLatestObject(email,'users')

    if(cached_object):
       etag = cached_object["etag"]
       teams_list = json.loads(cached_object["object"])
    else:
        teams_list = await setupHomepage(email)
        etag = await setEtag(email,'users',teams_list)
    
    response = api_helper.make_api_response_etag(200,teams_list,etag)
    # get the user
    
    return response

