import json
from pydantic import TypeAdapter, ValidationError

from classes import Team, Match
from config import app_config
import api_helper
import response_errors
from matches_data import save_team_fixture


def create_fixtures(event, context):
    body =json.loads(event["body"])
    print(body)
    team_id = event["pathParameters"]["team_id"]
    
    matches = body["matches"]
    created_matches = []
    for match in matches:
        request_player = Match(opposition=match["opposition"],homeOrAway=match["homeOrAway"],date=match["date"],team_id=team_id)
        MatchValidator = TypeAdapter(Match)

        try:
            new_match = MatchValidator.validate_python(request_player)
            save_response = save_team_fixture(new_match)
            save_response["link"] = "/matches/%s"%(save_response["id"])
            created_matches.append(save_response)
            actions = list()
                
            
        except ValidationError as e:
            errors = response_errors.validationErrorsList(e)
            response = api_helper.make_api_response(400,None,None,errors)
        except ValueError as e:
            response = api_helper.make_api_response(400,None,None,None)

    
    response = api_helper.make_api_response(200,created_matches,actions)
    return response