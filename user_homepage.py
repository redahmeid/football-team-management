import json
from pydantic import TypeAdapter, ValidationError

from classes import User
import response_classes
import exceptions
from team_data import retrieve_teams_by_user_id
from matches_data import retrieve_next_match_by_team
from users_data import retrieve_user_id_by_email
from secrets_util import getEmailFromToken, lambda_handler,validate_firebase_id_token
import api_helper

async def enter_screen(event, context):
    lambda_handler(event,context)
    teams_list = []
    try:
        email =  getEmailFromToken(event,context)
        teams = await retrieve_teams_by_user_id(email)
        for team in teams:
            team_response = convertTeamDataToTeamResponse(team)
            teams_list.append(team_response)
        response = api_helper.make_api_response(200,teams_list)
        # get the user
        return response
    except exceptions.AuthError as e:
        response = api_helper.make_api_response(401,None,e)

# "(ID varchar(255),"\
#         "Name varchar(255) NOT NULL,"\
#         "AgeGroup varchar(255) NOT NULL,"\
#         "Email varchar(255) NOT NULL,"\
#         "Club_ID varchar(255) NOT NULL,"\
#         "live VARCHAR(255),"\
def convertTeamDataToTeamResponse(team) -> response_classes.TeamResponse:
    print("convertTeamDataToTeamResponse: %s"%(team))
    id = team["t.ID"]
    baseTeamUrl = "/teams/%s"%(id)
    name = team["Name"]
    ageGroup = team["AgeGroup"]
    live = team["t.live"]
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