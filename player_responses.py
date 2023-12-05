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
    minuteOn:float
   

class PlayerResponse(BaseModel):
    info:PlayerInfo
    selectionInfo:Optional[SelectionInfo]=None
    links:Optional[Dict[str,Link]]=None
    def __eq__(self, other):
        if isinstance(other, PlayerResponse):
            return (self.info.id == other.info.id and
                    self.selectionInfo.position == other.selectionInfo.position)
        return NotImplemented
    def __hash__(self):
        # Create a hash based on the same attributes you're using in __eq__
        return hash((self.info.id, self.selectionInfo.position))
