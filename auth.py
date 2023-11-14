import json

from team_data import retrieve_teams_by_user_id,does_userid_match_team
from roles_data import retrieve_role_by_user_id_and_team_id
from secrets_util import  lambda_handler,validate_firebase_id_token
import api_helper

import json
import boto3
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from exceptions import AuthError


# Initialize the AWS Secrets Manager client
secretsmanager = boto3.client('secretsmanager')

def set_custom_claims(event, context):
    print("###################IN SET CLAIMS################")
    lambda_handler(event,context)
    id_token = getToken(event=event)
    
    email = id_token["email"]
    print("###################EMAIL %s################"%email)
    teams = retrieve_teams_by_user_id(email)
    print(teams)
    teamsClaims = {}
    for team in teams:
        team_id = team["Team_ID"]
        roles = retrieve_role_by_user_id_and_team_id(id_token["email"],team_id)
        roleClaims = []
        for role in roles:
            
            roleClaims.append(role["Role"])
        teamsClaims[team_id] = roleClaims
    additionalClaims = {
        "teams": teamsClaims
    }
    
    
    auth.set_custom_user_claims(uid=id_token["uid"],custom_claims=additionalClaims)
    
    response = api_helper.make_api_response(200,{"claims":"set"})
                
    return response

def getToken(event):
    id_token = event["headers"]['Authorization'].split('Bearer ')[1]
    if(validate_firebase_id_token(id_token)):
        
        return auth.verify_id_token(id_token)
    else:
        raise AuthError
    
def check_permissions(event,team_id,acceptable_roles):
    id_token = getToken(event)
    print("###########DISCOVERED TOKN %s"%id_token)
    roles = id_token["teams"][team_id]
    print("###########DISCOVERED ROLES %s"%roles)
    intersection = set(roles).intersection(acceptable_roles)
    if intersection:
         return True
    else: 
        return does_userid_match_team(user_id=id_token["email"],team_id=team_id)
        
    

