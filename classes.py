
from pydantic import BaseModel, validator
from typing import Optional, List
from validators import validate_email,validate_short_name
import datetime
import roles


class PlayerMatch(BaseModel):
    match_id:str
    player_id:str
    start_time_minutes:int
    end_time_minutes:int
    position:str

class Match(BaseModel):
    team_id:str
    opposition:str
    homeOrAway:str
    status:str
    length:int
    date:datetime.date

class Player(BaseModel):
    name:str
    team_id:str

class Players(BaseModel):
    players:List[Player]

class Coach(BaseModel):
    name:str
    role:str

class ClubAdministrator(BaseModel):
    name:str
    email:str
    club_id:str
    role:str

class TeamUser(BaseModel):
    user_id:str
    team_id:str
    role:roles.Role

class Team(BaseModel):
    name:str
    age_group:str

class Club(BaseModel):
    id:Optional[str]=None
    name:str
    short_name:str
    email:str
    phone:str
    admin:Optional[List[ClubAdministrator]]=None
    teams:Optional[List[Team]] = None

    @validator('email')
    def validate_email_format(cls, value):
        print("In validator email")
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if validate_email(value):
            return value
        raise ValueError("Invalid email")

    @validator('short_name')
    def validate_short_name_format(cls, value):
       
      if validate_short_name(value):
        return value
      raise ValueError("Short Name must have no spaces")

class User(BaseModel):
    email:str
    
    
    
    




