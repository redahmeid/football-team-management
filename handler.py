import json
from pydantic import TypeAdapter, ValidationError
from classes import Club, Team
import mysql.connector
from config import app_config
import response_errors
import id_generator
import club_apis


def create_club(event, context):
    return club_apis.create_club(event,context)