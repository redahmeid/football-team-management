import json
from pydantic import TypeAdapter, ValidationError

from classes import Team
from config import app_config
import api_helper
import response_errors
from team_data import save_team


def create_team(event, context):
    body =json.loads(event["body"])
    
    club_id = event["pathParameters"]["club_id"]
    team = Team(club_id=club_id,name=body["name"],email=body["email"],age_group=body["age_group"],team_size=body["team_size"])
    TeamValidator = TypeAdapter(Team)

    try:
        new_team = TeamValidator.validate_python(team)
        save_response = save_team(new_team)
        if(save_response[0]==0):
            result = {"row":save_response[0]}
            response = api_helper.make_api_response(200,result,None)
        else:
            result = {"team_id":save_response[1]}
            actions = list()
            actions.append({"name":"club_details","link":"/clubs/%s" %(new_team.club_id),"method":"GET"})
            actions.append({"name":"team_details","link":"/teams/%s" %(save_response[1]),"method":"GET"})
            actions.append({"name":"add_team_admin","link":"/teams/%s/admins" %(save_response[1]),"method":"POST"})
            actions.append({"name":"add_players","link":"/teams/%s/players" %(save_response[1]),"method":"POST"})
            actions.append({"name":"add_fixture","link":"/teams/%s/fixtures" %(save_response[1]),"method":"POST"})
            response = api_helper.make_api_response(200,result,actions)
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        response = api_helper.make_api_response(400,None,None,errors)
    except ValueError as e:
        response = api_helper.make_api_response(400,None,None,None)

    print(response)
    return response