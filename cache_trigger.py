
from cache_paths import Paths

from etag_manager import isEtaggged,deleteEtag,setEtag,getLatestObject
import boto3
from config import app_config
import json
from timeit import timeit

@timeit
async def updateTeamCache(team_id):
    
    await deleteEtag(team_id,'teams')
    event = {
        "id":team_id,
        "path":Paths.cacheTeam.value
    }
    await invokeCacheHander(event)

@timeit
async def updateMatchCache(match_id):
    await deleteEtag(match_id,'matches')
    event = {
        "id":match_id,
        "path":Paths.cacheMatch.value
    }
    await invokeCacheHander(event)

@timeit
async def updateMatchPlanCache(match_id):
    await deleteEtag(match_id,'planned_lineups')
    event = {
        "id":match_id,
        "path":Paths.cachePlans.value
    }
    await invokeCacheHander(event) # Opt

@timeit
async def updateMatchActualCache(match_id):
    await deleteEtag(match_id,'actual_lineups')
    event = {
        "id":match_id,
        "path":Paths.cacheActual.value
    }
    await invokeCacheHander(event) # Opt

@timeit
async def updateMatchCurrentLineupCache(match_id):
    await deleteEtag(match_id,'current_lineup')
    event = {
        "id":match_id,
        "path":Paths.cacheCurrentLineup.value
    }
    await invokeCacheHander(event) #

@timeit
async def updateUserCache(email):
    await deleteEtag(email,'users')
    event = {
        "id":email,
        "path":Paths.cacheUser.value
    }
    await invokeCacheHander(event)

@timeit
async def updatePlayerCache(team_id):
    
    await deleteEtag(team_id,'players')
    event = {
        "id":team_id,
        "path":Paths.cachePlayers.value
    }
    await invokeCacheHander(event)



@timeit
async def  invokeCacheHander(event):
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
    FunctionName=app_config.cache_handler,  # Name of the target Lambda
    InvocationType='Event',
    Payload=json.dumps(event)  # Asynchronous invocation
    ) 