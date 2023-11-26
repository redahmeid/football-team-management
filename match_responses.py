from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from validators import validate_email,validate_short_name
import datetime
from matches_state_machine import MatchState
import player_responses

from enum import Enum

class MATCH_CONSTS:
    baseUrl = "/teams/{}/matches/{}"

def getMatchUrl(team_id,match_id):
    return MATCH_CONSTS.baseUrl.format(team_id,match_id)
class Link(BaseModel):
    link:str
    method:str

class HomeOrAway(str, Enum):
    home = "Home"
    away = "Away"

class TeamResponse(BaseModel):
    id:str
    name:str
    ageGroup:str
    live:bool
    self:Link
    nextMatch:Link        #save_response["next_match"] = {"ID":match["ID"],"opposition":match["Opposition"],"date":match["Date"].isoformat(),"homeOrAway":match["HomeOrAway"], "club_name":match["c.Name"], "team_name":match["Name"], "age_group":match["AgeGroup"]}
    teamPlayers:Link        #save_response["players"] = {"link":"/teams/%s/players"%(save_response["ID"]),"method":"get"}
    teamFixtures:Link        #save_response["fixtures"] = {"link":"/teams/%s/matches"%(save_response["ID"]),"method":"get"}
    addPlayers:Link        #save_response["addPlayers"] = {"link":"/teams/%s/players"%(save_response["ID"]),"method":"post"}
    addFixtures:Link 

class MatchInfo(BaseModel):
    id:str
    team:TeamResponse
    status:MatchState
    goals:Optional[int]=0
    conceded:Optional[int]=0
    length:int
    opposition:str
    homeOrAway:HomeOrAway
    date:datetime.date

class MatchPeriod(BaseModel):
    status:str
    time:int

class PlayerMatchStat(BaseModel):
    player: player_responses.PlayerInfo
    time: float
class MatchResponse(BaseModel):
    match:MatchInfo
    squad:Optional[List]=None
    links:Optional[Dict[str,Link]]=None

class PlannedMatchResponse(BaseModel):
    match:MatchInfo
    planned_lineups:Optional[List]=None
    links:Optional[Dict[str,Link]]=None

class ActualMatchResponse(BaseModel):
    match:MatchInfo
    started_at:Optional[int]=0
    how_long_left:Optional[float]=0
    current_players:Optional[List]=None
    next_players:Optional[List]=None
    assisters:Optional[List]=None
    goals:Optional[List]=None
    opposition:Optional[List]=None
    links:Optional[Dict[str,Link]]=None
