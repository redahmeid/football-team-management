import json
from pydantic import TypeAdapter, ValidationError

from classes import User
import response_classes
from config import app_config
import api_helper
import response_errors
from users_data import save_user,retrieve_user_id_by_email,update_user
from matches_data import retrieve_next_match_by_team
from auth import getToken
from secrets_util import lambda_handler
from notifications import save_token
import asyncio
from email_sender import send_email,send_email_with_template

async def new_user(event, context):
    await lambda_handler(event,context)
    try:
        body =json.loads(event["body"])
        print(body)
        email = getToken(event)["email"]
        await saveDeviceToken(event)
        user = await retrieve_user_id_by_email(email)
        
        if(not user):
            await save_user(id,email,body["name"])
            template_id="d-f25c6f27e6d14af58f8a3457ecfebee2"
            await send_email_with_template(email,template_id,{})
        else:
            await update_user(user,body["name"])
        
        response = api_helper.make_api_response(200,{"id":id})
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        response = api_helper.make_api_response(400,None,errors)
    except ValueError as e:
        response = api_helper.make_api_response(400,None,e)

    print(response)
    return response

async def saveDeviceToken(event):
    headers = event["headers"]
    device_token = event["headers"]['x-device-token']
    device_id = event["headers"]['x-device-id']
    email = getToken(event)["email"]
    version = headers.get('x-football-app',None)
    await save_token(email=email,token=device_token,device=device_id,version=version)


# "(ID varchar(255),"\
#         "Name varchar(255) NOT NULL,"\
#         "AgeGroup varchar(255) NOT NULL,"\
#         "Email varchar(255) NOT NULL,"\
#         "Club_ID varchar(255) NOT NULL,"\
#         "live VARCHAR(255),"\
def convertTeamDataToTeamResponse(team) -> response_classes.TeamResponse:
    print("convertTeamDataToTeamResponse: %s"%(team))
    id = team["ID"]
    baseTeamUrl = "/teams/%s"%(id)
    name = team["Name"]
    ageGroup = team["AgeGroup"]
    email = team["Email"]
    clubId = team["Club_ID"]
    live = team["live"]
    print("Convert team live %s"%(live))
    if(live == None):
        live = True
    self = response_classes.Link(link=baseTeamUrl,method="get")
    players = response_classes.Link(link="%s/players"%(baseTeamUrl),method="get")
    fixtures= response_classes.Link(link="%s/matches"%(baseTeamUrl),method="get")
    addPlayers = response_classes.Link(link="%s/players"%(baseTeamUrl),method="post")
    addFixtures = response_classes.Link(link="%s/matches"%(baseTeamUrl),method="post")
    nextMatch = response_classes.Link(link="%s/next_match"%(baseTeamUrl),method="get")

    response =  response_classes.TeamResponse(id=id,email=email,name=name,ageGroup=ageGroup,clubId=clubId,live=live,self=self,nextMatch=nextMatch,teamPlayers=players,teamFixtures=fixtures,addFixtures=addFixtures,addPlayers=addPlayers)
    print("Convert team %s"%(response))
    return response.model_dump()