import json
from pydantic import TypeAdapter, ValidationError

from classes import Player
from config import app_config
import api_helper
import response_errors
import response_classes
from player_data import save_player,retrieve_players_by_team,delete_player,retrieve_player


def create_players(event, context):
    body =json.loads(event["body"])
    
    team_id = event["pathParameters"]["team_id"]
    
    players = body["players"]
    print("CREATE PLAYERS; %s"%(players))
    created_players = []
    i = 0
    for player in players:
        print("CREATE PLAYERS INDEX; %s"%(i))
        request_player = Player(name=player["name"],team_id=team_id)
        PlayerValidator = TypeAdapter(Player)

        try:
            new_player = PlayerValidator.validate_python(request_player)
            result = convertPlayerDataToPlayerResponse(retrieve_player(save_player(new_player)))
            
            
            created_players.append(result)
                
            
        except ValidationError as e:
            errors = response_errors.validationErrorsList(e)
            response = api_helper.make_api_response(400,None,errors)
        except ValueError as e:
            response = api_helper.make_api_response(400,None,None)

    
    response = api_helper.make_api_response(200,created_players)
    return response
def create_player(event,context):
    body =json.loads(event["body"])
    
    team_id = event["pathParameters"]["team_id"]
    
    player = body["players"]
    
    request_player = Player(name=player["name"],team_id=team_id)
    PlayerValidator = TypeAdapter(Player)

    try:
        new_player = PlayerValidator.validate_python(request_player)
        save_response = save_player(new_player)
        save_response["link"] = "/players/%s"%(save_response["id"])
        
        actions = list()
            
        
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        response = api_helper.make_api_response(400,None,None,errors)
    except ValueError as e:
        response = api_helper.make_api_response(400,None,None,None)

    
    response = api_helper.make_api_response(200,save_response,actions)
    return response



def list_players_by_team(event, context):
   
    
    team_id = event["pathParameters"]["team_id"]
    
    players = []
    for player in retrieve_players_by_team(team_id):
       
        new_player = {"ID":player["ID"],"name":player["Name"]}
        try:
            
            result = convertPlayerDataToPlayerResponse(player)
            
            players.append(result)
                
            
        except ValidationError as e:
            errors = response_errors.validationErrorsList(e)
            response = api_helper.make_api_response(400,None,errors)
        except ValueError as e:
            response = api_helper.make_api_response(400,None,None)

    
    response = api_helper.make_api_response(200,players)
    return response

def delete_player_from_team(event, context):
   
    
    player_id = event["pathParameters"]["player_id"]
    
    players = []
    

    try:
        delete_player(player_id)
        save_response = {"message":"Player %s has been deleted"%(player_id)}
        save_response["link"] = "/players/%s"%(player_id)
        players.append(save_response)
        actions = list()
            
        
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        response = api_helper.make_api_response(400,None,None,errors)
    except ValueError as e:
        response = api_helper.make_api_response(400,None,None,None)

    
    response = api_helper.make_api_response(200,players,actions)
    return response

# ID varchar(255),"\
        # "Name varchar(255) NOT NULL,"\
        # "Team_ID varchar(255) NOT NULL,"\
        # "Email varchar(255),"\
        # "live varchar(255),"\
def convertPlayerDataToPlayerResponse(player) -> response_classes.PlayerResponse:
    
    id = player["ID"]
    baseTeamUrl = "/players/%s"%(id)
    name = player["Name"]
    live = player["live"]
    if(live == None):
        live = True
    self = response_classes.Link(link=baseTeamUrl,method="get")
    deletePlayer = response_classes.Link(link=baseTeamUrl,method="delete")
    response =  response_classes.PlayerResponse(id=id,name=name,live=live,self=self,deletePlayer=deletePlayer)
    print("Convert player %s"%(response))
    return response.model_dump()