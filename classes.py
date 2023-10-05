
from pydantic import BaseModel, validator
from typing import Optional, List
from validators import validate_email,validate_short_name
import re

class Player(BaseModel):
    name:str
    number:int

class Coach(BaseModel):
    name:str
    role:str

class ClubAdministrator(BaseModel):
    name:str
    email:str
    role:str

class Team(BaseModel):
    id:Optional[str]=None
    name:str
    age_group:str
    email:str
    club_id:str
    players:Optional[List[Player]]

class Club(BaseModel):
    id:Optional[str]=None
    name:str
    short_name:str
    email:str
    phone:str
    admin:List[ClubAdministrator]
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
    
    
    




