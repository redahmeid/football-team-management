
from pydantic import BaseModel, validator
from typing import Optional, List
from validators import validate_email,validate_short_name


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

class TeamAdministrator(BaseModel):
    name:str
    email:str
    team_id:str
    role:str

class Team(BaseModel):
    id:Optional[str]=None
    name:str
    age_group:str
    email:Optional[str]=None
    club_id:str
    players:Optional[List[Player]]=None

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


    
    
    
    




