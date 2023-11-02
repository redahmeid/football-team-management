import json
from pydantic import TypeAdapter, ValidationError

from classes import User
import response_classes
from config import app_config
import api_helper
import response_errors
from users_data import save_user
from matches_data import retrieve_next_match_by_team


def new_user(event, context):
    body =json.loads(event["body"])
    
    user = User(email=body["email"])
    UserValidator = TypeAdapter(User)
    
    try:
        new_team = UserValidator.validate_python(user)
        id = save_user(new_team)
        
        response = api_helper.make_api_response(200,{"id":id})
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        response = api_helper.make_api_response(400,None,None,errors)
    except ValueError as e:
        response = api_helper.make_api_response(400,None,None,None)

    print(response)
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