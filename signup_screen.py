import json
from pydantic import TypeAdapter, ValidationError

from classes import User
import response_classes
from config import app_config
import exceptions
from users_apis import new_user
from matches_data import retrieve_next_match_by_team
from secrets_util import getEmailFromToken, lambda_handler,validate_firebase_id_token
import api_helper

def signup_submit(event, context):
    await lambda_handler(event,context)
    
    try:
        return new_user(event,context)
    except exceptions.AuthError as e:
        response = api_helper.make_api_response(401,None,e)

