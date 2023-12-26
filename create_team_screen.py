import json
from pydantic import TypeAdapter, ValidationError

from classes import User,Team,TeamUser
import response_classes
from config import app_config
import exceptions
from users_data import retrieve_user_id_by_email
from team_data import save_team,retrieve_team_by_id
from secrets_util import getEmailFromToken, lambda_handler
import api_helper
from roles_data import save_role
import roles
from auth import set_custom_claims
import team_season_data
import notifications
import team_data
import asyncio
import id_generator

from supabase import create_client, Client
supabase: Client = create_client(app_config.supabase_url, app_config.supabase_key)
def enter_screen(event, context):
    lambda_handler(event,context)
    
    try:
        getEmailFromToken(event,context)
        
        # get the user
        return ""
    except exceptions.AuthError as e:
        response = api_helper.make_api_response(401,None,e)
async def sendMessagesOnTeamUpdate(token,message,title,team_id):
    await notifications.send_push_notification(token, title, message,"new_team",f"/teams/{team_id}")
    

async def submitTeamEvent(team:response_classes.TeamResponse):
    users = await team_data.retrieve_users_by_team_id(team.id)
    for user in users:
        tokens = await notifications.getDeviceToken(user.email)
        for token in tokens:
            new_token = token["Token"]
            asyncio.create_task(sendMessagesOnTeamUpdate(new_token, f"{team.name} has been created", "New team added",team.id))
async def submit_team(event, context):
    lambda_handler(event,context)
    body =json.loads(event["body"])
    teams = []
    try:
        email = getEmailFromToken(event,context)
        
        team = Team(age_group=body["age_group"],name=body["name"])
        id = id_generator.generate_random_number(5)
        team_id = id_generator.generate_random_number(5)
        data, count = supabase.table('teams').insert({"id": id, "name": body["name"],"age_group":body["age_group"],"season":body["season"],"team_id":team_id}).execute()
        save_response = await save_team(team,team_id)
        

        team_season_id = await team_season_data.save_team_season(team_id,body["season"],body["age_group"])
        teamUser = TeamUser(email=email,team_id=str(team_season_id),role=roles.Role.admin)
        role_id = await save_role(teamUser)
        await set_custom_claims(event=event,context=context)
        # get the user
        save_response = await retrieve_team_by_id(team_season_id)
        teams.append(save_response.model_dump())
        response = api_helper.make_api_response(200,teams)
        await submitTeamEvent(save_response)
        
    except exceptions.AuthError as e:
        print(e)
        response = api_helper.make_api_response(401,None,e)
    except Exception as e:
        print(e)
        response = api_helper.make_api_response(400,None,e)
    return response
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
    season = team[f"{team_season_data.TABLE.SEASON_NAME}"]
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

    response =  response_classes.TeamResponse(id=id,season=season,name=name,ageGroup=ageGroup,live=live,self=self,nextMatch=nextMatch,teamPlayers=players,teamFixtures=fixtures,addFixtures=addFixtures,addPlayers=addPlayers)
    print("Convert team %s"%(response))
    return response.model_dump()