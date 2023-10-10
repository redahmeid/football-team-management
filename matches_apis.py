import json
from pydantic import TypeAdapter, ValidationError, BaseModel

from classes import Team, Match,PlayerMatch
from config import app_config
import api_helper
import response_errors
from matches_data import save_team_fixture,save_planned_match_squad,retrieve_planned_match_squad


def create_fixtures(event, context):
    body =json.loads(event["body"])
    print(body)
    team_id = event["pathParameters"]["team_id"]
    
    matches = body["matches"]
    created_matches = []
    for match in matches:
        request_player = Match(opposition=match["opposition"],homeOrAway=match["homeOrAway"],date=match["date"],team_size=match["team_size"],team_id=team_id)
        MatchValidator = TypeAdapter(Match)

        try:
            new_match = MatchValidator.validate_python(request_player)
            save_response = save_team_fixture(new_match)
            actions = list()
            actions.append({"name":"match_details","link":"/matches/%s"%(save_response["id"]),"method":"GET"})
            actions.append({"name":"plan_match_day_squad","link":"/matches/%s/planned_squad"%(save_response["id"]),"method":"POST"})
            save_response["actions"] = actions
            created_matches.append(save_response)
            actions = list()
                
            
        except ValidationError as e:
            errors = response_errors.validationErrorsList(e)
            response = api_helper.make_api_response(400,None,None,errors)
        except ValueError as e:
            response = api_helper.make_api_response(400,None,None,None)

    
    response = api_helper.make_api_response(200,created_matches,actions)
    return response

# {
    # player_id:""
    # start_time_minutes:0
    # end_time_minutes:10
    # position:"CM"
# }
def plan_match_squad(event,context):
    class PlayerMatch:
        def __init__(self, match_id, player_id,player_name,start_time_minutes,end_time_minutes,position):
            self.player_id = player_id
            self.player_name = player_name
            self.start_time_minutes = start_time_minutes
            self.end_time_minutes = end_time_minutes
            self.position = position
    


    body =json.loads(event["body"])
    
    match_id = event["pathParameters"]["match_id"]
    
    players = body["players"]
    start_times = []
    for player in players:
        player_id = player["player_id"]
        start_time_minutes = player["start_time_minutes"]
        start_times.append(start_time_minutes)
        end_time_minutes = player["end_time_minutes"]
        position = player["position"]

        new_player = PlayerMatch(player_id=player_id,match_id=match_id,start_time_minutes=start_time_minutes,end_time_minutes=end_time_minutes,position=position)
        id = save_planned_match_squad(new_player)

    response = api_helper.make_api_response(200,match_id,None)

    return response

# {
    # player_id:""
    # start_time_minutes:0
    # end_time_minutes:10
    # position:"CM"
# }
def show_planned_match_day_squad(event,context):
    

    class PlayerMatch:
        def __init__(self, match_id, player_id,player_name,start_time_minutes,end_time_minutes,position):
            self.player_id = player_id
            self.player_name = player_name
            self.start_time_minutes = start_time_minutes
            self.end_time_minutes = end_time_minutes
            self.position = position
    
    match_id = event["pathParameters"]["match_id"]
    
    squad = retrieve_planned_match_squad(matchId=match_id)
    print(squad)
    players = list()
    sub_times = []
    start_times=[]
    for player in squad:
        player_id = player["Player_ID"]
        player_name = player["Name"]
        position = player["Position"]
        start_time_minutes = player["Start_Time_Minutes"]
        
        end_time_minutes = player["End_Time_Minutes"]
        start_times.append(start_time_minutes)
        sub_times.append(end_time_minutes)
        player_match = PlayerMatch(match_id,player_id,player_name,start_time_minutes,end_time_minutes,position)
        players.append(player_match.__dict__)
    unique_sub_times = list(set(sub_times))
    unique_start_times = list(set(start_times))
    players.sort(key=lambda x: x["start_time_minutes"])
    subs = list()
    on_pitch = list()
    for sub_time in unique_sub_times:
        def sub_time_is_equal_to(playerMatch):
            return playerMatch["end_time_minutes"] == sub_time
        filtered_list = list(filter(sub_time_is_equal_to,players)) 
        subs.append({"sub_time":sub_time,"subs":filtered_list})
    subs.sort(key=lambda x:x["sub_time"])
    
    for start_time in unique_start_times:
        def on_pitch_check(playerMatch):
            return playerMatch["start_time_minutes"] <= start_time and playerMatch["end_time_minutes"] > start_time
        on_pitch_filtered = list(filter(on_pitch_check,players))
        on_pitch.append({"time":start_time,"on_pitch_team":on_pitch_filtered})
    
    on_pitch.sort(key=lambda x:x["time"])
        


                             
    match_squad = {"match_id":match_id,"on_pitch":on_pitch,"subs":subs,"team_times":players}
    print(players)
    response = api_helper.make_api_response(200,match_squad,None)

    return response