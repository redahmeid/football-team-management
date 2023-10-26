import json
from pydantic import TypeAdapter, ValidationError

from classes import Club
from config import app_config
import api_helper
import response_errors
import response_classes
from club_data import save_club,retrieve_club


def create_club(event, context):
    body =json.loads(event["body"])
    
    ClubValidator = TypeAdapter(Club)
    
    try:
        new_club = ClubValidator.validate_python(body)
        save_response = save_club(new_club)
        if(save_response[0]==0):
            result = {"row":save_response[0]}
            response = api_helper.make_api_response(200,result,None)
        else:
            data = retrieve_club(save_response[1])
        
            response = api_helper.make_api_response(200,convertClubDataToClubResponse(data))
           
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        response = api_helper.make_api_response(400,None)
    except ValueError as e:
        response = api_helper.make_api_response(400,None,None)
   
    print(response)
    return response

def retrieve_club_summary(event, context):
    club_id = event["pathParameters"]["club_id"]
    
    
    try:
        data = retrieve_club(club_id)
        
        response = api_helper.make_api_response(200,convertClubDataToClubResponse(data))
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        response = api_helper.make_api_response(400,None,None,errors)
    except ValueError as e:
        response = api_helper.make_api_response(400,None,None,None)
   
    print(response)
    return response

# (ID varchar(255),"\
#         "Name varchar(255) NOT NULL,"\
#         "Short_Name varchar(255) NOT NULL,"\
#         "Email varchar(255),"\
#         "Phone varchar(255)NOT NULL,"\
# class ClubResponse(BaseModel):
#     id:str
#     name:str
#     shortName:str
#     email:str
#     phone:str
#     self:Link
#     createTeams:Link
#     listTeams:Link
def convertClubDataToClubResponse(club) -> response_classes.ClubResponse:
    print("convertClubDataToClubResponse: %s"%club)
    id = club["ID"]
    baseTeamUrl = "/clubs/%s"%(id)
    name = club["Name"]
    shortName = club["Short_Name"]
    email = club["Email"]
    phone = club["Phone"]
    self = response_classes.Link(link=baseTeamUrl,method="get")
    createTeams = response_classes.Link(link="%s/teams"%(baseTeamUrl),method="post")
    listTeams = response_classes.Link(link="%s/teams"%(baseTeamUrl),method="get")
    

    response =  response_classes.ClubResponse(id=id,email=email,name=name,shortName=shortName,phone=phone,self=self,createTeams=createTeams,listTeams=listTeams)
    print("Convert team %s"%(response))
    return response.model_dump()