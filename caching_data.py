

from etag_manager import isEtaggged,deleteEtag,setEtag,getLatestObject
import functools
import time
import asyncio
import hashlib
import json
import firebase_admin
from firebase_admin import credentials, firestore
import player_data
import matches_backend
import team_backend
import team_data
import json
import boto3
import firebase_admin
import matches_backend
import player_backend
import user_homepage_backend
from firebase_admin import credentials
from firebase_admin import auth, messaging
from exceptions import AuthError

# Initialize the AWS Secrets Manager client
secretsmanager = boto3.client('secretsmanager')
from cache_paths import Paths
from timeit import timeit




@timeit
async def handler(event,context):
    try:
        # Retrieve the serviceAccountKey.json from Secrets Manager
        secret_name = "dev/firebase"  # Replace with your secret name
        secret = secretsmanager.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(secret['SecretString'])
        
        # Initialize Firebase Admin SDK with the retrieved credentials
        firebase_cred = credentials.Certificate(secret_dict)
        
        app = firebase_admin.initialize_app(credential=firebase_cred)
        print("FIREBASE APP initialized: %s"%app)
    except Exception as e:
        print(e)
    path = event["path"]

    if(path==Paths.cacheMatch.value):
        match_id = event["id"]
        await cacheMatch(match_id)
    elif(path==Paths.cacheTeam.value):
        team_id = event["id"]
        await cacheTeam(team_id)
    elif(path==Paths.cachePlans.value):
        match_id = event["id"]
        await cachePlans(match_id)
    elif(path==Paths.cacheUser.value):
        email = event["id"]
        await cacheUser(email)
    elif(path==Paths.cachePlayers.value):
        team_id = event["id"]
        await cachePlayers(team_id)
    elif(path==Paths.cacheCurrentLineup.value):
        match_id = event["id"]
        await cacheCurrentLineup(match_id)
    elif(path==Paths.cacheActual.value):
        match_id = event["id"]
        await cacheActualLineup(match_id)
@timeit
async def cacheMatch(match_id):
    
    await matches_backend.getMatchFromDB(match_id)

@timeit
async def cacheTeam(team_id):
    await team_backend.getTeamFromDB(team_id)

@timeit
async def cachePlans(match_id):
    await matches_backend.getPlannedLineupsFromDB(match_id)

@timeit
async def cacheUser(email):
    
    await user_homepage_backend.getUserInfoFromDB(email)

@timeit
async def cachePlayers(team_id):
    
    await player_backend.getPlayersFromDB(team_id)

@timeit
async def cacheCurrentLineup(match_id):
    
    await matches_backend.getMatchCurrentLineups(match_id)

@timeit
async def cacheActualLineup(match_id):
    
    await matches_backend.getMatchCurrentLineups(match_id)