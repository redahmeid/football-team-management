
from cache_paths import Paths

from etag_manager import isEtaggged,deleteEtag,setEtag,getLatestObject
import boto3
from config import app_config
import json
from fcatimer import fcatimer

@fcatimer
async def updateTeamCache(team_id):
    
    await deleteEtag(team_id,'teams')
    event = {
        "id":team_id,
        "path":Paths.cacheTeam.value
    }
    await invokeCacheHander(event)

@fcatimer
async def updateMatchCache(match_id):
    await deleteEtag(match_id,'matches')
    event = {
        "id":match_id,
        "path":Paths.cacheMatch.value
    }
    await invokeCacheHander(event)

@fcatimer
async def updateMatchPlanCache(match_id):
    await deleteEtag(match_id,'planned_lineups')
    event = {
        "id":match_id,
        "path":Paths.cachePlans.value
    }
    await invokeCacheHander(event) # Opt

@fcatimer
async def updateMatchActualCache(match_id):
    await deleteEtag(match_id,'actual_lineups')
    event = {
        "id":match_id,
        "path":Paths.cacheActual.value
    }
    await invokeCacheHander(event) # Opt

@fcatimer
async def updateMatchCurrentLineupCache(match_id):
    await deleteEtag(match_id,'current_lineup')
    event = {
        "id":match_id,
        "path":Paths.cacheCurrentLineup.value
    }
    await invokeCacheHander(event) #

@fcatimer
async def updateUserCache(email):
    await deleteEtag(email,'users')
    event = {
        "id":email,
        "path":Paths.cacheUser.value
    }
    await invokeCacheHander(event)

@fcatimer
async def updatePlayerCache(team_id):
    
    await deleteEtag(team_id,'players')
    event = {
        "id":team_id,
        "path":Paths.cachePlayers.value
    }
    await invokeCacheHander(event)

@fcatimer
async def saveDeviceToken(email,device_token,device_id,app_version):
    
    
    event = {
        "email":email,
        "device_token":device_token,
        "device_id":device_id,
        "app_version":app_version,
        "path":Paths.saveDeviceToken.value
    }
    await invokeCacheHander(event)


@fcatimer
async def updateGuardiansPlayerCache(team_id):
    
    await deleteEtag(team_id,'guardian_players')
    event = {
        "id":team_id,
        "path":Paths.cacheGuardiansPlayers.value
    }
    await invokeCacheHander(event)



@fcatimer
async def  invokeCacheHander(event):
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
    FunctionName=app_config.cache_handler,  # Name of the target Lambda
    InvocationType='Event',
    Payload=json.dumps(event)  # Asynchronous invocation
    ) 