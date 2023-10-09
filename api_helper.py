
from typing import List
import json

def make_api_response(statusCode: int, result: str, actions, errors = None):
    if statusCode >= 400:
        
        body = {"errors": errors}
    else:
        # Handle success response
        body = {"result": result, "actions": actions}

    response = {"statusCode": statusCode, "body": json.dumps(body), "headers": {"Content-Type": "application/json"}}
    return response
