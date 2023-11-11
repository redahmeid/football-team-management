from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from validators import validate_email,validate_short_name
import datetime
from matches_state_machine import MatchState
import player_responses

from enum import Enum

class MATCH_CONSTS:
    baseUrl = "/teams/%s/matches/%s"

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

class MatchResponse(BaseModel):
    match:MatchInfo
    players:Optional[List[player_responses.PlayerResponse]]=None
    links:Optional[Dict[str,Link]]=None
