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

class MatchInfo(BaseModel):
    id:str
    status:MatchState
    length:int
    opposition:str
    homeOrAway:HomeOrAway
    date:datetime.date
    how_long_ago_started:int=0

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
    current_players:Optional[List]=None
    next_players:Optional[List]=None
    links:Optional[Dict[str,Link]]=None
