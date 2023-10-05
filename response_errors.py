from pydantic import TypeAdapter, ValidationError, BaseModel
from typing import Optional, List

class CreateClubError(BaseModel):
    type:str=""
    field:str=""

class CreateClubErrors(BaseModel):
    errors:List=[]


def listCreateClubErrors(e: ValidationError):
    errors = CreateClubErrors()
    for error in e.errors():
        baseError = {"type":error["type"],"field":error["loc"][0]}
        
        errors.errors.append(baseError)
    
    return errors