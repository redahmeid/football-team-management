import json
from pydantic import TypeAdapter, ValidationError
from exceptions import AuthError
from classes import Team
import response_classes
import api_helper
import response_errors
from team_data import save_team,retrieve_team_by_id
from secrets_util import getEmailFromToken, lambda_handler
from auth import set_custom_claims
from player_data import retrieve_players_by_team
from matches_apis import list_matches_by_team_backend
from auth import check_permissions
from roles import Role

from team_backend import addSingleUser


async def create_team(event, context):
    lambda_handler(event,context)
    

    body =json.loads(event["body"])
    
    TeamValidator = TypeAdapter(Team)
    teams = []
    try:
        
        team = Team(name=body["name"],age_group=body["age_group"])
        new_team = TeamValidator.validate_python(team)
        save_response = save_team(new_team)
        set_custom_claims(getEmailFromToken(event,context))
        print("CREATE TEAM: %s"%(save_response))
        teams.append(convertTeamDataToTeamResponse(await retrieve_team_by_id(save_response)))
        response = api_helper.make_api_response(200,teams)
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        response = api_helper.make_api_response(400,None)
    except ValueError as e:
        response = api_helper.make_api_response(400,None)
    except AuthError as e:
        response = api_helper.make_api_response(401,None,e)

    print(response)
    return response
async def addUserToTeam(event,context):
    lambda_handler(event,context)
    acceptable_roles = [Role.admin.value]
    team_id = event["pathParameters"]["team_id"]
    body =json.loads(event["body"])
    emails = body["emails"]
    if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
        for email in emails:
            await addSingleUser(email,team_id)
        response = api_helper.make_api_response(200,None,"Users added")
    else:
            response = api_helper.make_api_response(403,None,"You do not have permission to edit this match")
    return response




async def retrieve_team_summary(event, context):
   
    
    team_id = event["pathParameters"]["team_id"]
    
    teams = []

    try:
        team = await retrieve_team_by_id(team_id)
        team_response = convertTeamDataToTeamResponse(team)
        players = await retrieve_players_by_team(team_response.id)
        team_response.squad = players[0]["players"]
        matches = await list_matches_by_team_backend(team_response.id)
        team_response.fixtures = matches
        teams.append(team_response.model_dump())
        actions = list()
            
        
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        print(errors)
        response = api_helper.make_api_response(400,None,errors)
        return response
    except ValueError as e:
        print(e)
        response = api_helper.make_api_response(400,None)
        return response
        
    
    response = api_helper.make_api_response(200,teams)
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
    return response