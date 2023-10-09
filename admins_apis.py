import json
from pydantic import TypeAdapter, ValidationError
from classes import ClubAdministrator,TeamAdministrator
from config import app_config
import response_errors
from admins_data import save_club_admin
import api_helper


def create_club_admin(event, context):
    body =json.loads(event["body"])
    
    club_id = event["pathParameters"]["club_id"]
    club_admin = ClubAdministrator(club_id=club_id,name=body["name"],email=body["email"],role=body["role"])
    ClubValidator = TypeAdapter(ClubAdministrator)
    try:
        new_admin = ClubValidator.validate_python(club_admin)
        save_response = save_club_admin(new_admin)
        if(save_response[0]==0):
            result = {"row":save_response[0]}
            response = api_helper.make_api_response(200,result,None)
        else:
            result = {"admin_id":save_response[1]}
            actions = list()
            actions.append({"name":"club_details","link":"/clubs/%s" %(new_admin.club_id),"method":"GET"})
            actions.append({"name":"admin_details","link":"/admins/%s" %(save_response[1]),"method":"GET"})
            response = api_helper.make_api_response(200,result,actions)
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        response = api_helper.make_api_response(400,None,None,errors)
    except ValueError as e:
        response = api_helper.make_api_response(400,None,None,None)

    print(response)
    return response

def create_team_admin(event, context):
    body =json.loads(event["body"])
    
    team_id = event["pathParameters"]["team_id"]
    club_admin = TeamAdministrator(team_id=team_id,name=body["name"],email=body["email"],role=body["role"])
    ClubValidator = TypeAdapter(ClubAdministrator)
    try:
        new_admin = ClubValidator.validate_python(club_admin)
        save_response = save_club_admin(new_admin)
        if(save_response[0]==0):
            result = {"row":save_response[0]}
            response = api_helper.make_api_response(200,result,None)
        else:
            result = {"admin_id":save_response[1]}
            actions = list()
            actions.append({"name":"club_details","link":"/clubs/%s" %(new_admin.club_id),"method":"GET"})
            actions.append({"name":"admin_details","link":"/admins/%s" %(save_response[1]),"method":"GET"})
            response = api_helper.make_api_response(200,result,actions)
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        response = api_helper.make_api_response(400,None,None,errors)
    except ValueError as e:
        response = api_helper.make_api_response(400,None,None,None)

    print(response)
    return response