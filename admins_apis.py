import json
from pydantic import TypeAdapter, ValidationError
from classes import Club
from config import app_config
import response_errors
from club_data import save_club


def create_club(event, context):
    body =json.loads(event["body"])
    ClubValidator = TypeAdapter(Club)
    
    try:
        new_club = ClubValidator.validate_python(body)
        save_response = save_club(new_club)
        if(save_response[0]==0):
            response = {"isBase64Encoded": "false","statusCode": 400, "body":json.dumps({"row":save_response[0]}),'headers': {'Content-Type': 'application/json'}}
        else:
            response = {"isBase64Encoded": "false","statusCode": 200, "body":json.dumps({"row":save_response[0],"id":save_response[1]}),'headers': {'Content-Type': 'application/json'}}
    except ValidationError as e:
        print(e)
        errors = response_errors.listCreateClubErrors(e)
        response = {"isBase64Encoded": "false","statusCode": 400, "body": json.dumps({"errors":errors.errors}),'headers': {'Content-Type': 'application/json'}}
    except ValueError as e:
        response = {"isBase64Encoded": "false","statusCode": 400, "body": json.dumps({"errors":e}),'headers': {'Content-Type': 'application/json'}}
   
    print(response)
    return response