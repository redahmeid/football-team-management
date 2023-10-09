from pydantic import TypeAdapter, ValidationError, BaseModel
from typing import Optional, List



def validationErrorsList(e: ValidationError):
    errors = list()
    for error in e.errors():
        baseError = {"type":error["type"],"field":error["loc"][0]}
        
        errors.append(baseError)
    
    return errors