
from typing import List
import json
import datetime

def make_api_response(statusCode: int, result: str, actions, errors = None):
    if statusCode >= 400:
        
        body = {"errors": errors}
    else:
        # Handle success response
        body = {"result": result, "actions": actions}

    response = {"statusCode": statusCode, "body": json.dumps(body), "headers": {"Content-Type": "application/json"}}
    return response

def serialize_datetime(obj): 
    if isinstance(obj, datetime.datetime):  
        return obj.isoformat() 
    raise TypeError("Type not serializable") 
