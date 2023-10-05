import json
from pydantic import TypeAdapter, ValidationError
from classes import Club, Team
import mysql.connector
from config import app_config
import response_errors
import id_generator
from club_data import save_club


def create_club(event, context):
    body =json.loads(event["body"])
    ClubValidator = TypeAdapter(Club)
    
    try:
        new_club = ClubValidator.validate_python(body)
        save_response = save_club(new_club)
        if(save_response[0]==0):
            response = {"statusCode": 400, "body":{"row":save_response[0]}}
        else:
            response = {"statusCode": 200, "body":{"row":save_response[0],"id":save_response[1]}}
    except ValidationError as e:
        print(e)
        errors = response_errors.listCreateClubErrors(e)
        response = {"statusCode": 400, "body": {"errors":errors.errors}}
    except ValueError as e:
        response = {"statusCode": 400, "body": {"errors":e}}
   
    
    return response