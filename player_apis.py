import json
from pydantic import TypeAdapter, ValidationError

from classes import Player
from config import app_config
import api_helper
import response_errors
from player_data import save_player


def create_players(event, context):
    body =json.loads(event["body"])
    
    team_id = event["pathParameters"]["team_id"]
    
    players = body["players"]
    created_players = []
    for player in players:
        request_player = Player(name=player["name"],team_id=team_id)
        PlayerValidator = TypeAdapter(Player)

        try:
            new_player = PlayerValidator.validate_python(request_player)
            save_response = save_player(new_player)
            save_response["link"] = "/players/%s"%(save_response["id"])
            created_players.append(save_response)
            actions = list()
                
            
        except ValidationError as e:
            errors = response_errors.validationErrorsList(e)
            response = api_helper.make_api_response(400,None,None,errors)
        except ValueError as e:
            response = api_helper.make_api_response(400,None,None,None)

    
    response = api_helper.make_api_response(200,created_players,actions)
    return response