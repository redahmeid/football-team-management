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

def enter_screen(event, context):
    lambda_handler(event,context)
    
    try:
        getEmailFromToken(event,context)
        
        # get the user
        return ""
    except exceptions.AuthError as e:
        response = api_helper.make_api_response(401,None,e)

def submit_team(event, context):
    lambda_handler(event,context)
    body =json.loads(event["body"])
    teams = []
    try:
        email = getEmailFromToken(event,context)
        print("SUBMIT TEAM EMAIL %s"%email)
        print("SUBMIT TEAM BODY %s"%body)
        team = Team(age_group=body["age_group"],name=body["name"])
        print("SUBMIT TEAM TEAM %s"%team)
        team_id = save_team(team)
        print("SUBMIT TEAM TEAM ID %s"%team_id)
        user_id = retrieve_user_id_by_email(email)
        print("SUBMIT TEAM USER ID %s"%user_id)
        teamUser = TeamUser(user_id=user_id,team_id=str(team_id),role=roles.Role.admin)
        role_id = save_role(teamUser)
        print("SUBMIT TEAM ROLE ID %s"%role_id)
        # get the user
        save_response =convertTeamDataToTeamResponse(retrieve_team_by_id(team_id))
        teams.append(save_response)
        response = api_helper.make_api_response(200,teams)
        print("SUBMIT TEAM RESPONSE %s"%response)
        
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

    response =  response_classes.TeamResponse(id=id,name=name,ageGroup=ageGroup,live=live,self=self,nextMatch=nextMatch,teamPlayers=players,teamFixtures=fixtures,addFixtures=addFixtures,addPlayers=addPlayers)
    print("Convert team %s"%(response))
    return response.model_dump()