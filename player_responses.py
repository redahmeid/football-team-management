from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from validators import validate_email,validate_short_name


class Guardian(BaseModel):
    email:str
    player_id:str
    team_id:str


class Link(BaseModel):
    link:str
    method:str

class PlayerInfo(BaseModel):
    id:Optional[str]=""
    name:Optional[str]=""
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
    minuteOn:Optional[float]=0.0

class PlayerStats(BaseModel):
    goals:Optional[int]=0
    assists:Optional[int]=0
    rating:Optional[float]=0.0
    potms:Optional[int]=0
    minutes:Optional[int]=0
    minutesPerGame:Optional[int]=0

class PlayerResponse(BaseModel):
    info:PlayerInfo
    selectionInfo:Optional[SelectionInfo]=SelectionInfo()
    stats:Optional[PlayerStats]=PlayerStats()
    rating:Optional[PlayerRating]=PlayerRating()
    guardians:Optional[List]=[]
    links:Optional[Dict[str,Link]]=None
    def __eq__(self, other):
        if isinstance(other, PlayerResponse):
            return (self.info.id == other.info.id and
                    self.selectionInfo.position == other.selectionInfo.position)
        return NotImplemented
    def __hash__(self):
        # Create a hash based on the same attributes you're using in __eq__
        return hash((self.info.id, self.selectionInfo.position))
