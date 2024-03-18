import json
from pydantic import ValidationError
import traceback
import exceptions
from typing import List
from player_data import retrieve_players_by_team
import sys
from matches_data import retrieve_match_by_id
import matches_data
from match_day_data import retrieve_periods_by_match,retrieveNextPlanned,retrieveAllPlannedLineups,save_actual_lineup,save_planned_lineup,retrieveCurrentActual, save_assists_for,save_goals_for,save_opposition_goal
from secrets_util import lambda_handler
import api_helper
from auth import check_permissions
from roles import Role
import matches_state_machine
import player_responses
import response_classes
import match_planning_backend
from match_planning_backend import submit_actual_lineup,submit_planned_lineup,submit_subs,getMatchPlanning,getMatchConfirmedPlanReadyToStart,getMatchStarted,getMatchCreated,setGoalsFor,getMatchGuest,updateMatchPeriod,setGoalsAgainst
from datetime import date
import logging
import time
import asyncio
import datetime
import notifications
import team_data

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def timeit(method):
    def timed(*args, **kw):
        start_time = time.time()
        result = method(*args, **kw)
        end_time = time.time()

        logging.info(f"{method.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return timed

async def addShot(event,context):
    await lambda_handler(event,context)
    acceptable_roles = [Role.admin.value]
    team_id = event["pathParameters"]["team_id"]
    match_id = event["pathParameters"]["match_id"]
    body =json.loads(event["body"])
    # player_id
    if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
        results = []
        
        response = api_helper.make_api_response(200,results)
    else:
            response = api_helper.make_api_response(403,None,"You do not have permission to edit this match")
    return response