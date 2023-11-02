
from typing import List
import json
import datetime

def make_api_response(statusCode: int, result: str,  errors = None):
    if statusCode >= 400:
        
        body = {"errors": errors}
    else:
        # Handle success response
        body = {"result": result}

    response = {"statusCode": statusCode, "body": json.dumps(body,default=str), "headers": {"Content-Type": "application/json"}}
    return response

def serialize_datetime(obj): 
    if isinstance(obj, datetime.date):  
        return obj.isoformat() 
