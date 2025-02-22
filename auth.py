import json

from team_data import retrieve_teams_by_user_id,does_userid_match_team
from roles_data import retrieve_role_by_user_id_and_team_id,retrieve_player_roles_by_user_id,retrieve_team_roles_by_user_id
from secrets_util import  lambda_handler,validate_firebase_id_token
import api_helper
import sys
import asyncio
import json
import boto3    
from etag_manager import getObject,updateDocument
import firebase_admin
import etag_manager
from firebase_admin import credentials
from firebase_admin import auth
from exceptions import AuthError
from notifications import save_token,save_token_by_match,turn_off_notifications
from fcatimer import fcatimer
import traceback
import logging
logger = logging.getLogger(__name__)
import functools

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the AWS Secrets Manager client
secretsmanager = boto3.client('secretsmanager')

@fcatimer
async def set_custom_claims(event, context):
    print("###################IN SET CLAIMS################")
    await lambda_handler(event,context)
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


@fcatimer
async def set_claims(email,uid):
    teamsClaims = {}
    additionalClaims = {}
    playerClaims = {}
    user = await getObject(email,'users_store')
    if(not user):
        user = await getObject(str(str(email).lower.__hash__),'users_store')
    if(user):
        user_dict = user.get().to_dict()
        admins = user_dict.get('admin',[])
        for admin in admins:
            team_id = admin
            roles = []
            if team_id in teamsClaims:
                teamsClaims[team_id].append('admin')
            else:
                teamsClaims[team_id] = ['admin']
        guardians = user_dict.get('guardians',[])
        for guardian in guardians:
            team_id = guardian
            roles = []
            if team_id in teamsClaims:
                teamsClaims[team_id].append('parent')
            else:
                teamsClaims[team_id] = ['parent']
        players = user_dict.get('players',[])
        for player in players:
            player_id = player
            roles = []
            if player_id in playerClaims:
                playerClaims[player_id].append('parent')
            else:
                playerClaims[player_id] = ['parent']
    
    additionalClaims['teams'] =  teamsClaims
    
   
    additionalClaims["players"]= playerClaims
    
    auth.set_custom_user_claims(uid=uid,custom_claims=additionalClaims)
    await etag_manager.setEtag(email,'claims',additionalClaims)

@fcatimer
async def saveDeviceToken(event,context)  :
    await lambda_handler(event,context)
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
        device_token = headers.get('x-device-token',None)
        device_id = headers.get('x-device-id',None)
        version = headers.get('x-football-app',None)
        print(f"DEVICE TOKEN {device_token}")
        try:
            email = getToken(event)["email"]
        except AuthError as e:
            email =""
        await save_token(email=email,token=device_token,device=device_id,version=version)
        print("Token saved")
    except Exception as e:
        traceback.print_exception(*sys.exc_info()) 
        logger.error("e")

async def turnOffNotifications(event,context)  :
    await lambda_handler(event,context)
    try:
        headers = event["headers"]
        
        print(headers)
        device_token = event["headers"]['x-device-id']
        print(f"DEVICE TOKEN {device_token}")
       
        await turn_off_notifications(device=device_token)
        print("Token saved")
    except Exception as e:
        traceback.print_exception(*sys.exc_info()) 
        logger.error("e")

async def saveDeviceTokenByMatch(event,context)  :
    await lambda_handler(event,context)
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

@fcatimer 
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
    

