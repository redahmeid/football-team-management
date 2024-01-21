
from typing import List
import json
import datetime
import hashlib
def make_api_response(statusCode: int, result: str,  errors = None):
    
    
    if statusCode == 404:
        body = {}
    elif statusCode >= 400:
        body = {"errors": errors}
    else:
        # Handle success response
        body = {"result": result}

    response = {"statusCode": statusCode, "body": json.dumps(body,default=str), "headers": {"Access-Control-Allow-Origin": "*","Content-Type": "application/json"}}
    return response

def make_api_response_etag(statusCode: int, result: str,etag,  errors = None):
    print(f"STATUS CODE RESPONSE {statusCode}")
    if statusCode == 404:
        body = {}
    elif statusCode >= 400:
        body = {"errors": errors}
    elif statusCode==304:
        response = {"statusCode": statusCode, "headers": {"Access-Control-Allow-Origin": "*","Access-Control-Expose-Headers" :"*","Content-Type": "application/json","ETag":etag}}
        return response
    else:
        # Handle success response
        body = {"result": result}

    response = {"statusCode": statusCode, "body": json.dumps(body,default=str), "headers": {"Access-Control-Allow-Origin": "*","Access-Control-Expose-Headers" :"*","Content-Type": "application/json","ETag":etag}}
    return response

def serialize_datetime(obj): 
    if isinstance(obj, datetime.date):  
        return obj.isoformat() 
