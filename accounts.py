import json
from pydantic import ValidationError
import traceback
import exceptions
from typing import List
from player_data import retrieve_players_by_team_with_stats
import sys
from matches_data import retrieve_match_by_id
import matches_data
from match_day_data import retrieve_periods_by_match,retrieveNextPlanned,retrieveAllPlannedLineups,save_actual_lineup,save_planned_lineup,retrieveCurrentActual, save_assists_for,save_goals_for,save_opposition_goal
from secrets_util import lambda_handler,delete_firebase_account
import api_helper
from auth import check_permissions
from roles import Role

import match_planning_backend
import firebase_admin
from match_planning_backend import  submit_starting_lineup,submit_planned_lineup,submit_subs,getMatchPlanning,getMatchConfirmedPlanReadyToStart,getMatchStarted,getMatchCreated,setGoalsFor,getMatchGuest,updateMatchPeriod,setGoalsAgainst
from datetime import date
import logging
import time
import users_data
import auth
import roles_data


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fcatimer(method):
    def timed(*args, **kw):
        start_time = time.time()
        result = method(*args, **kw)
        end_time = time.time()

        logging.info(f"{method.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return timed

@fcatimer
async def delete_account(event,context):
    await lambda_handler(event,context)
    email = auth.getEmailFromToken(event,context)
    await users_data.delete_user(email)
    await roles_data.delete_roles_by_email(email)
    await delete_firebase_account(event)
    
    