from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from validators import validate_email,validate_short_name


class Link(BaseModel):
    link:str
    method:str

class PlayerInfo(BaseModel):
    id:str
    name:Optional[str]=None

class SelectionInfo(BaseModel):
    id:Optional[str]=None
    position:str
    minuteOn:int
   

class PlayerResponse(BaseModel):
    info:PlayerInfo
    selectionInfo:Optional[SelectionInfo]=None
    links:Optional[Dict[str,Link]]=None
