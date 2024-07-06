
from pydantic import BaseModel, validator
from typing import Optional, List,Dict
from validators import validate_email,validate_short_name
import datetime
import roles
import matches_state_machine
from enum import Enum



class HomeOrAway(str, Enum):
    home = "Home"
    away = "Away"
    neutral="Neutral"

class PlayerInfo(BaseModel):
    id:Optional[str]=""
    name:Optional[str]=""
    forename:Optional[str]=""
    surname:Optional[str]=""
    shortname:Optional[str]=""
    team_id:Optional[str]=""

class PlayerRating(BaseModel):
    overall:Optional[str]=""
    technical:Optional[str]=""
    physical:Optional[str]=""
    psychological:Optional[str]=""
    social:Optional[str]=""
    comments:Optional[str]=""
    potm:Optional[bool]=False

class SelectionInfo(BaseModel):
    id:Optional[str]=""
    position:Optional[str]=""

class PlayerStats(BaseModel):
    goals:Optional[int]=0
    assists:Optional[int]=0
    rating:Optional[float]=0.0
    potms:Optional[int]=0
    minutes:Optional[float]=0
    total_minutes:Optional[float]=0
    minutesPerGame:Optional[float]=0

class Player(BaseModel):
    info:PlayerInfo
    selectionInfo:Optional[SelectionInfo]=SelectionInfo()
    stats:Optional[PlayerStats]=PlayerStats()
    rating:Optional[PlayerRating]=PlayerRating()
    guardians:Optional[List]=[]
class MatchType(str, Enum):
    friendly = "friendly"
    league = "league"
    trophy = "trophy"
class Lineup(BaseModel):
    id:str
    players:List=[]
    match_id:str
    minute:float
    type:str
    deleted:bool=False
class MatchInfo(BaseModel):
    id:str
    team_id:Optional[str]=""
    time_started:Optional[datetime.datetime]=None
    time_last_started:Optional[datetime.datetime]=None
    time_ended:Optional[datetime.datetime]=None
    seconds_played_when_paused:Optional[float]=0.0
    status:matches_state_machine.MatchState
    status_history:Optional[List]=[]
    goals:Optional[int]=0
    conceded:Optional[int]=0
    scorers:Optional[List]=[]
    opposition_goals:Optional[List]=[]
    actual_lineups:Optional[List]=None
    planned_lineups:Optional[List]=None
    length:int
    opposition:str
    homeOrAway:HomeOrAway
    location:Optional[str] = ''
    placeId:Optional[str] = ''
    date:datetime.datetime
    time:Optional[datetime.time]=datetime.datetime.now(datetime.timezone.utc)
    type:Optional[MatchType]=None
    captain:Optional[str]=None


class GroupTeam(BaseModel):
    id:str
    teams:Optional[List]=[]

class Team(BaseModel):
    id:str
    name:str
    age_group:str
    season:str
    admins:Optional[List[Dict]]={}
    team_id:Optional[str]=""
    fixtures:Optional[List] = []
    squad:Optional[List] = []
    coaches:Optional[List]=[]
    guardians:Optional[List]=[]
    wins:Optional[int]=0
    defeats:Optional[int]=0
    draws:Optional[int]=0

class TeamUser(BaseModel):
    email:str
    role:roles.Role

class User(BaseModel):
    email:str
    name:Optional[str]=''
    guardians:Optional[List]=[]
    players:Optional[List]=[]
    teams:Optional[List]=[]
    admin:Optional[List]=[]




    
    
    
    
    




