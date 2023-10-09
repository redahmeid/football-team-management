import json
from pydantic import TypeAdapter, ValidationError

from classes import Club
from config import app_config
import api_helper
import response_errors
from club_data import save_club


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
            result = {"club_id":save_response[1]}
            actions = list()
            actions.append({"name":"create_admin","link":"/admins/%s" %(save_response[1]),"method":"POST"})
            response = api_helper.make_api_response(200,result,actions)
    except ValidationError as e:
        errors = response_errors.listCreateClubErrors(e)
        response = api_helper.make_api_response(400,None,None,errors)
    except ValueError as e:
        response = api_helper.make_api_response(400,None,None,None)
   
    print(response)
    return response