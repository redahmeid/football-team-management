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


