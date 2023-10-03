import json
from pydantic import TypeAdapter, ValidationError
from classes import Club

def create_club(event, context):
    body =json.loads(event["body"])
    ClubValidator = TypeAdapter(Club)
    print(body)
    try:
        new_club = ClubValidator.validate_python(body)
        save_club(new_club)
        response = {"statusCode": 200, "body": new_club.model_dump_json()}
        print(response)
    except ValidationError as e:
        print(e)
        response = {"statusCode": 400, "body": "invalid club"}
    
    return response
def save_club(club:Club):
    print("here")
    # save club