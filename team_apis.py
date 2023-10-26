import json
from pydantic import TypeAdapter, ValidationError

from classes import Team
import response_classes
from config import app_config
import api_helper
import response_errors
from team_data import save_team,retrieve_teams_by_club,retrieve_team_by_id
from matches_data import retrieve_next_match_by_team


def create_team(event, context):
    body =json.loads(event["body"])
    
    club_id = event["pathParameters"]["club_id"]
    team = Team(club_id=club_id,name=body["name"],email=body["email"],age_group=body["age_group"],team_size=body["team_size"])
    TeamValidator = TypeAdapter(Team)
    teams = []
    try:
        new_team = TeamValidator.validate_python(team)
        save_response = save_team(new_team)
        print("CREATE TEAM: %s"%(save_response))
        teams.append(convertTeamDataToTeamResponse(retrieve_team_by_id(save_response)))
        response = api_helper.make_api_response(200,teams)
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        response = api_helper.make_api_response(400,None,None,errors)
    except ValueError as e:
        response = api_helper.make_api_response(400,None,None,None)

    print(response)
    return response


def list_teams_by_club(event, context):
   
    
    club_id = event["pathParameters"]["club_id"]
    
    teams = []
    for team in retrieve_teams_by_club(club_id):
        try:
            
            
            save_response =convertTeamDataToTeamResponse(team)
            teams.append(save_response)
            actions = list()
                
            
        except ValidationError as e:
            errors = response_errors.validationErrorsList(e)
            response = api_helper.make_api_response(400,None)
        except ValueError as e:
            response = api_helper.make_api_response(400,None)

    
    response = api_helper.make_api_response(200,teams)
    return response

def retrieve_team_summary(event, context):
   
    
    team_id = event["pathParameters"]["team_id"]
    
    teams = []

    try:
        
        save_response =convertTeamDataToTeamResponse(retrieve_team_by_id(team_id))
        teams.append(save_response)
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