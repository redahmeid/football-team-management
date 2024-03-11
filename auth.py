import json

from team_data import retrieve_teams_by_user_id,does_userid_match_team
from roles_data import retrieve_role_by_user_id_and_team_id,retrieve_player_roles_by_user_id,retrieve_team_roles_by_user_id
from secrets_util import  lambda_handler,validate_firebase_id_token
import api_helper
import sys
import asyncio
import json
import boto3    
import firebase_admin
import etag_manager
from firebase_admin import credentials
from firebase_admin import auth
from exceptions import AuthError
from notifications import save_token,save_token_by_match,turn_off_notifications
from timeit import timeit
import traceback
import logging
logger = logging.getLogger(__name__)
import functools

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the AWS Secrets Manager client
secretsmanager = boto3.client('secretsmanager')

@timeit
async def set_custom_claims(event, context):
    print("###################IN SET CLAIMS################")
    lambda_handler(event,context)
    id_token = getToken(event=event)
    
    # body =json.loads(event["body"])
    email = id_token["email"]
    # if(body["registration_token"] is not None):
    #     registration_token = body["registration_token"]
    #     asyncio.run(save_token(email,None,None,None,registration_token))
    
    print("###################EMAIL %s################"%email)
    await set_claims(email,id_token["uid"])
    
    response = api_helper.make_api_response(200,{"claims":"set"})
                
    return response


@timeit
async def set_claims(email,uid):
    teams = await retrieve_team_roles_by_user_id(email)
    players = await retrieve_player_roles_by_user_id(email)
    print(teams)
    teamsClaims = {}
    additionalClaims = {}
    for team in teams:
        
        team_id = team['Team_ID']
        roles = []
        if(team['user_roles']):
            roles = team['user_roles'].split(',')
        
        teamsClaims[team_id] = roles
    additionalClaims['teams'] =  teamsClaims
    playerClaims = {}
    for player in players:
        
        team_id = player['Player_ID']
        roles = []
        if(player['user_roles']):
            roles = player['user_roles'].split(',')
        
        playerClaims[team_id] = roles
    additionalClaims["players"]= playerClaims
    
    auth.set_custom_user_claims(uid=uid,custom_claims=additionalClaims)
    await etag_manager.setEtag(email,'claims',additionalClaims)

@timeit
async def saveDeviceToken(event,context)  :
    lambda_handler(event,context)
    try:
        headers = event["headers"]
        pathParameters = event.get("pathParameters")

        # Check if pathParameters is not None and 'match_id' exists as a key
        if pathParameters and "match_id" in pathParameters:
            match_id = pathParameters["match_id"]
            # Proceed with your logic using match_id
        else:
            match_id=""

        print(headers)
        device_token = event["headers"]['x-device-id']
        print(f"DEVICE TOKEN {device_token}")
        try:
            email = getToken(event)["email"]
        except AuthError as e:
            email =""
        await save_token(email=email,token=device_token)
        print("Token saved")
    except Exception as e:
        traceback.print_exception(*sys.exc_info()) 
        logger.error("e")

async def turnOffNotifications(event,context)  :
    lambda_handler(event,context)
    try:
        headers = event["headers"]
        
        print(headers)
        device_token = event["headers"]['x-device-id']
        print(f"DEVICE TOKEN {device_token}")
       
        await turn_off_notifications(token=device_token)
        print("Token saved")
    except Exception as e:
        traceback.print_exception(*sys.exc_info()) 
        logger.error("e")

async def saveDeviceTokenByMatch(event,context)  :
    lambda_handler(event,context)
    try:
        headers = event["headers"]
        pathParameters = event.get("pathParameters")

        # Check if pathParameters is not None and 'match_id' exists as a key
        if pathParameters and "match_id" in pathParameters:
            match_id = pathParameters["match_id"]
            # Proceed with your logic using match_id
        else:
            match_id=""

        print(headers)
        device_token = event["headers"]['x-device-id']
        print(f"DEVICE TOKEN {device_token}")
        
        await save_token_by_match(match_id=match_id,token=device_token)
        print("Token saved")
    except Exception as e:
        traceback.print_exception(*sys.exc_info()) 
        logger.error("e")

def getDeviceToken(event):
    id_token = event["headers"]['x-device-id']
    return id_token

def getToken(event):
    id_token = event["headers"]['Authorization'].split('Bearer ')[1]
    if(validate_firebase_id_token(id_token)):
        
        return auth.verify_id_token(id_token)
    else:
        raise AuthError

@timeit 
async def check_permissions(event,team_id,acceptable_roles):
    try:
        id_token = getToken(event)
        print("###########DISCOVERED TOKN %s"%id_token)
        if "teams" in id_token and id_token["teams"] is not None:
            if( team_id in id_token["teams"]):
                roles = id_token["teams"][team_id]
                print("###########DISCOVERED ROLES %s"%roles)
                intersection = set(roles).intersection(acceptable_roles)
                if intersection:
                    return True
                else: 
                    return False
            else:
                valid =  await does_userid_match_team(user_id=id_token["email"],team_id=team_id)
                
                await set_claims(id_token["email"],id_token["uid"])
                return valid
        else:
             valid =  await does_userid_match_team(user_id=id_token["email"],team_id=team_id)
             await set_claims(id_token["email"],id_token["uid"])
             return valid
    except Exception as e:
        traceback.print_exception(*sys.exc_info()) 
        return False

def getEmailFromToken(event,context):
    print("GET EMAIL FROM TOKEN")
    id_token = event["headers"]['Authorization'].split('Bearer ')[1]
    if(validate_firebase_id_token(id_token)):
        print("GET EMAIL FROM TOKEN SUCESS")
        return auth.verify_id_token(id_token)["email"]
    else:
        print("GET EMAIL FROM TOKEN ERROR")
        raise AuthError
    

