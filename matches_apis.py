import json
from pydantic import TypeAdapter, ValidationError, BaseModel

from classes import Team, Match,PlayerMatch
from config import app_config
import api_helper
import response_errors
from matches_data import retrieve_match_by_id,save_team_fixture,save_planned_match_squad,retrieve_planned_match_squad, retrieve_fixture_team_size, retrieve_matches_by_team,retrieve_next_match_by_team
import response_classes

def create_fixtures(event, context):
    body =json.loads(event["body"])
    print(body)
    team_id = event["pathParameters"]["team_id"]
    
    matches = body["matches"]
    created_matches = []
    for match in matches:
        request_player = Match(opposition=match["opposition"],homeOrAway=match["homeOrAway"],date=match["date"],length=match["length"],team_id=team_id)
        MatchValidator = TypeAdapter(Match)

        try:
            new_match = MatchValidator.validate_python(request_player)
            result = convertMatchDatatoMatchResponse(retrieve_match_by_id(save_team_fixture(new_match)))
            
            created_matches.append(result)
            
                
            
        except ValidationError as e:
            errors = response_errors.validationErrorsList(e)
            response = api_helper.make_api_response(400,None)
        except ValueError as e:
            response = api_helper.make_api_response(400,None)

    
    response = api_helper.make_api_response(200,created_matches)
    return response

# {
    # player_id:""
    # start_time_minutes:0
    # end_time_minutes:10
    # position:"CM"
# }
def plan_match_squad(event,context):
    class PlayerMatch:
        def __init__(self, match_id, player_id,start_time_minutes,end_time_minutes,position):
            self.player_id = player_id
            self.start_time_minutes = start_time_minutes
            self.end_time_minutes = end_time_minutes
            self.match_id=match_id
            self.position = position
    


    body =json.loads(event["body"])
    
    match_id = event["pathParameters"]["match_id"]
    
    team_size = retrieve_fixture_team_size(match_id)

    players = body["players"]
    start_times = []
    for player in players:
        player_id = player["player_id"]
        start_time_minutes = player["start_time_minutes"]
        start_times.append(start_time_minutes)
        end_time_minutes = player["end_time_minutes"]
        position = player["position"]
    
    unique_start_times = list(set(start_times))
    on_pitch = list()
    for start_time in unique_start_times:
        def on_pitch_check(playerMatch):
            return playerMatch["start_time_minutes"] <= start_time and playerMatch["end_time_minutes"] > start_time
        on_pitch_filtered = list(filter(on_pitch_check,players))
        print("TEAM SIZE "+str(len(on_pitch_filtered)))
        print("TEAM SIZE "+str(team_size))
        if(len(on_pitch_filtered)!=team_size):
            return api_helper.make_api_response(400,None,None,[{"messages":"Team size is too small"}])
    
    for player in players:
        player_id = player["player_id"]
        start_time_minutes = player["start_time_minutes"]
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

def list_matches_by_team(event, context):
    team_id = event["pathParameters"]["team_id"]
    
    matches = []
    for match in retrieve_matches_by_team(team_id):
        try:
            
            save_response =convertMatchDatatoMatchResponse(match)
            matches.append(save_response)
            
                
            
        except ValidationError as e:
            errors = response_errors.validationErrorsList(e)
            print(errors)
            response = api_helper.make_api_response(400,None,errors)
            return response
        except ValueError as e:
            print(e)
            response = api_helper.make_api_response(400,None)
            return response
            
    
    response = api_helper.make_api_response(200,matches)
    return response

def next_match_by_team(event, context):
    team_id = event["pathParameters"]["team_id"]
    
    matches = []
    
    try:
        
        save_response =convertMatchDatatoMatchResponse(retrieve_next_match_by_team(team_id))
        matches.append(save_response)
        
            
        
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        print(errors)
        response = api_helper.make_api_response(400,None,errors)
        return response
    except ValueError as e:
        print(e)
        response = api_helper.make_api_response(400,None)
        return response
            
    
    response = api_helper.make_api_response(200,matches)
    return response

# (ID varchar(255),"\
#         "Opposition varchar(255) NOT NULL,"\
#         "Team_ID varchar(255) NOT NULL,"\
#         "HomeOrAway varchar(255),"\
#         "Date datetime,"\
#         "Team_Size int NOT NULL,"\
def convertMatchDatatoMatchResponse(match) -> response_classes.MatchResponse:
    
    id = match["ID"]
    baseTeamUrl = "/matches/%s"%(id)
    opposition = match["Opposition"]
    homeOrAway = match["HomeOrAway"]
    length = match["Length"]
    date=match["Date"]
    self = response_classes.Link(link=baseTeamUrl,method="get")
    

    response =  response_classes.MatchResponse(id=id,opposition=opposition,homeOrAway=homeOrAway,date=date,self=self,length=length)
    print("Convert team %s"%(response))
    return response.model_dump()