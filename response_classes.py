from pydantic import BaseModel, validator
from typing import Optional, List, Dict
import datetime
import player_responses
from roles import Role
from typing import Optional, List, Dict
import datetime
from matches_state_machine import MatchState
import player_responses

from enum import Enum

class Link(BaseModel):
    link:str
    method:str
    meta_data:Optional[str]=""

class Admin(BaseModel):
    name:Optional[str]=""
    role:Optional[Role]=None
    email:str
class PlayerResponse(BaseModel):
    id:str
    name:str
    isSelected:bool=False
    live:bool
    self:Link
    deletePlayer:Link

class SelectedPlayerResponse(BaseModel):
    id:str
    selectionId:Optional[str]=None
    name:str
    isSelected:bool=False
    position:Optional[str]=None
    self:Link
    toggleStarting:Link

class TeamResponse(BaseModel):
    id:str
    name:Optional[str]=""
    ageGroup:str
    team_id:Optional[str]=""
    scorers:Optional[List]=[]
    assisters:Optional[List]=[]
    fixtures:Optional[List] = []
    results:Optional[List] = []
    squad:Optional[List] = []
    coaches:Optional[List]=[]
    season:Optional[str]=''
    wins:Optional[int]=0
    defeats:Optional[int]=0
    draws:Optional[int]=0
    season_id:Optional[str]=''
    seasons:Optional[List]=None
    live:Optional[bool]=True
    self:Optional[Link]=None 
    nextMatch:Optional[Link]=None        #save_response["next_match"] = {"ID":match["ID"],"opposition":match["Opposition"],"date":match["Date"].isoformat(),"homeOrAway":match["HomeOrAway"], "club_name":match["c.Name"], "team_name":match["Name"], "age_group":match["AgeGroup"]}
    teamPlayers:Optional[Link]=None         #save_response["players"] = {"link":"/teams/%s/players"%(save_response["ID"]),"method":"get"}
    teamFixtures:Optional[Link]=None         #save_response["fixtures"] = {"link":"/teams/%s/matches"%(save_response["ID"]),"method":"get"}
    addPlayers:Optional[Link]=None         #save_response["addPlayers"] = {"link":"/teams/%s/players"%(save_response["ID"]),"method":"post"}
    addFixtures:Optional[Link]=None  
    
# (ID varchar(255),"\
#         "Name varchar(255) NOT NULL,"\
#         "Short_Name varchar(255) NOT NULL,"\
#         "Email varchar(255),"\
#         "Phone varchar(255)NOT NULL,"\
class ClubResponse(BaseModel):
    id:str
    name:str
    teams:Optional[TeamResponse]=[]

       #save_response["addFixtures"] = {"link":"/teams/%s/matches"%(save_response["ID"]),"method":"post"}


class MATCH_CONSTS:
    baseUrl = "/matches/{}"

def getMatchUrl(team_id,match_id):
    return MATCH_CONSTS.baseUrl.format(match_id)


class HomeOrAway(str, Enum):
    home = "Home"
    away = "Away"
    neutral="Neutral"



class User(BaseModel):
    email:str
    first_name:Optional[str]=''
    surname:Optional[str]=''
    teams:Optional[List]=[]
    children:Optional[List]=[]

class MatchType(str, Enum):
    friendly = "friendly"
    league = "league"
    trophy = "trophy"
    

class MatchInfo(BaseModel):
    id:str
    team:Optional[TeamResponse]=None
    team_id:Optional[str]=""
    team_link:Optional[Link]=None
    self:Optional[Link]=None
    status:MatchState
    goals:Optional[int]=0
    conceded:Optional[int]=0
    length:int
    opposition:str
    homeOrAway:HomeOrAway
    location:Optional[str] = ''
    placeId:Optional[str] = ''
    date:datetime.date
    type:Optional[MatchType]=None
    captain:Optional[str]=None

class MatchPeriod(BaseModel):
    status:str
    time:int

class PlayerMatchStat(BaseModel):
    player: Optional[player_responses.PlayerInfo]=None
    position: Optional[str]=""
    secondary_player: Optional[player_responses.PlayerInfo]=None
    player_off: Optional[player_responses.PlayerResponse]=None
    player_on: Optional[player_responses.PlayerResponse]=None
    time: Optional[int]=0
    minute:Optional[int]=0
    type:Optional[str]=""
    assist_type:Optional[str]=""
    detail:Optional[str]=""
class MatchResponse(BaseModel):
    match:MatchInfo
    squad:Optional[List]=None
    links:Optional[Dict[str,Link]]=None

class PlannedMatchResponse(BaseModel):
    match:MatchInfo
    planned_lineups:Optional[List]=None
    links:Optional[Dict[str,Link]]=None
    captain:Optional[player_responses.PlayerResponse]=None


class Lineups(BaseModel):
    lineups:Optional[List]=[]
    subs:Optional[List]=[]



class ActualMatchResponse(BaseModel):
    match:MatchInfo
    started_at:Optional[int]=0
    how_long_left:Optional[float]=0
    refresh_at:Optional[int]=0
    current_players:Optional[List]=[]
    last_planned:Optional[List]=[]
    next_players:Optional[List]=[]
    planned_subs:Optional[List]=[]
    planned_position_changes:Optional[List]=[]
    planned_lineups:Optional[List]=[]
    actual_lineups:Optional[List]=[]
    actual_subs:Optional[List]=[]
    actual_position_changes:Optional[List]=[]
    assisters:Optional[List]=[]
    scorers:Optional[List]=[]
    opposition:Optional[List]=[]
    report:Optional[List]=[]
    links:Optional[Dict[str,Link]]=None
    captain:Optional[player_responses.PlayerResponse]=None
    links:Optional[Dict[str,Link]]=None



