import json
from pydantic import TypeAdapter, ValidationError, BaseModel
from typing import List
from config import app_config
from dateutil.parser import parse,isoparse
import api_helper
import datetime
import response_errors
import team_backend
from matches_data import retrieve_match_by_id,save_team_fixture,retrieve_not_played_by_team,retrieve_next_match_by_team,update_match_status
import notifications
from roles import Role
from auth import check_permissions
import match_detail_screen
import response_classes
import matches_data
import match_planning_backend
import match_day_data
import matches_backend
import user_homepage_backend
import matches_state_machine
import exceptions
from secrets_util import lambda_handler, getEmailFromToken,initialise_firebase
from match_planning_backend import list_matches_by_team_backend
from matches_backend import create_match_backend
from etag_manager import deleteEtag,whereEqual,getObject,updateDocument,whereNotIn,whereEqualwhere,getAllObjects,whereIDIn,whereIn
import functools
import time
import sys
import traceback
import json

import firebase_admin
from firebase_admin import credentials, firestore
from fcatimer import fcatimer
from cache_trigger import updateTeamCache,updateMatchCache, updateUserCache,updatePlayerCache


async def create_fixtures(event, context):
    await lambda_handler(event,context)
    http_method = event['httpMethod']

    
    body =json.loads(event["body"])
    print(body)
    pathParameters = event["pathParameters"]
    team_id = pathParameters["team_id"]
    
    
    matches = body["matches"]
    created_matches = []
    for match in matches:
    
        try:
            result = await create_match_backend(match,team_id)
            
            created_matches.append(result.model_dump())
        except ValidationError as e:
            print(f"CREATE MATCH VALIDATION ERROR {e}")
            errors = response_errors.validationErrorsList(e)
            response = api_helper.make_api_response(400,None,errors)
        except ValueError as e:
            print(f"CREATE MATCH VALUE ERROR {e}")
            response = api_helper.make_api_response(400,None)

    
    response = api_helper.make_api_response(200,created_matches)
    print(f"CREATE MATCH API RESPONSE {response}")
    return response
    
async def list_matches_by_team(event, context):
    try:
        team_id = event["pathParameters"]["team_id"]
        
        response =  await list_matches_by_team_backend(team_id)
        return api_helper.make_api_response(200,response)
    except Exception as e:
        traceback.print_exception(*sys.exc_info()) 

@fcatimer
async def time_played(event,context):
    await lambda_handler(event,context)
    
    match_id = event["pathParameters"]["match_id"]
    response = await match_planning_backend.how_long_played(match_id)
    return api_helper.make_api_response(200,{"player":response})

# @fcatimer
# async def updateFromCache(event,context):
#     await lambda_handler(event,context)
#     await matches_backend.updateDBFromCache()
@fcatimer
async def edit_match(event,context):
    await lambda_handler(event,context)
    body =json.loads(event["body"])
    match_id = event["pathParameters"]["match_id"]
    
    goals_for = body.get("goals_for","")
    goals_against = body.get("goals_against","")
    players = body.get("players","")
    if(goals_for!="" and goals_against!=""):
        await matches_backend.updateScore(match_id,goals_for,goals_against)
    if(len(players)>0):
        await matches_backend.addPlayerRatings(match_id,players)
        await match_planning_backend.updateStatus(match_id,matches_state_machine.MatchState.rated)
    await updateMatchCache(match_id)
    
    result = await matches_backend.getMatchFromDB(match_id)
    await updateTeamCache(result["result"]["match"]["team"]["id"])
    await updatePlayerCache(result["result"]["match"]["team"]["id"])
    response =  api_helper.make_api_response_etag(200,[result["result"]],result["etag"])
    print(f"EDIT RESPONSE {response}")
    return response


@fcatimer
async def addGoalScorer(event,context):
    await lambda_handler(event,context)

    
    body =json.loads(event["body"])
    goal_scorer = body["scorer"]
    assister = body.get('assister')
    assist_type = body.get('assist_type',"")
    
    type = body.get('type','')
    minutes = body.get('minutes','')

import boto3
@fcatimer
async def matchesDueToStart(event,context):
    await initialise_firebase()
    reminder = 5
    fs_config = await getObject('start_time_reminder','config')
    if(fs_config):
        fs_config_dict = fs_config.get().to_dict()
        reminder = fs_config_dict.get('value',reminder)
    now = datetime.datetime.now(datetime.timezone.utc)
    where_stats = firestore.FieldFilter('date', '<' , datetime.datetime.now(datetime.timezone.utc)+ datetime.timedelta(minutes=reminder))
    where_status = firestore.FieldFilter('status', 'not-in', ['ended','started','rated','restarted','paused','cancelled',''])
    where_today = firestore.FieldFilter('date', '>' , datetime.datetime.now(datetime.timezone.utc))

    fs_matches = await whereEqualwhere('matches_store',wheres=[where_status,where_stats,where_today])
    if(fs_matches):
        
        i = 0
        for  fs_match in fs_matches:
            fs_match_dict = fs_match.to_dict()
            
            if(not fs_match_dict.get('start_reminded',None)):
                fs_match_dict['start_reminded'] = True
                print(fs_match_dict)
                await updateDocument('matches_store',fs_match_dict['id'],fs_match_dict)
                event = {"id":fs_match_dict['id']}
                lambda_client = boto3.client('lambda')
                lambda_client.invoke(
                FunctionName=app_config.remind_to_start,  # Name of the target Lambda
                InvocationType='Event',
                Payload=json.dumps(event)  # Asynchronous invocation
                ) 

@fcatimer
async def matchesDueToEnd(event,context):
    await initialise_firebase()
    now = datetime.datetime.now(datetime.timezone.utc)
    
    where_status = firestore.FieldFilter('status', 'in', ['started','restarted','paused'])


    fs_matches = await whereEqualwhere('matches_store',wheres=[where_status])
    if(fs_matches):
        
        i = 0
        for  fs_match in fs_matches:
            fs_match_dict = fs_match.to_dict()
            
            if(not fs_match_dict.get('end_reminded',None)):
                fs_match_dict['end_reminded'] = True
                seconds_played = fs_match_dict.get('seconds_played_when_paused',0)
                time_started = fs_match_dict['time_started']
                time_last_started = fs_match_dict.get('time_last_started',time_started)
                if(not time_last_started):
                    time_last_started = time_started
                seconds_since_started = (datetime.datetime.now(datetime.timezone.utc)- time_last_started).timestamp()
                total_played =( seconds_since_started+seconds_played)/60
                if(total_played>fs_match_dict['length']-5):

                    print(fs_match_dict)
                    await updateDocument('matches_store',fs_match_dict['id'],fs_match_dict)
                    event = {"id":fs_match_dict['id']}
                    lambda_client = boto3.client('lambda')
                    lambda_client.invoke(
                    FunctionName=app_config.remind_to_start,  # Name of the target Lambda
                    InvocationType='Event',
                    Payload=json.dumps(event)  # Asynchronous invocation
                    ) 

import users_apis  
@fcatimer
async def remindToSTart(event,context):
    await initialise_firebase()

    id = event["id"]
    fs_match = await getObject(id,'matches_store')
    if(fs_match):
        fs_match_dict = fs_match.get().to_dict()
        metadata = {'match_id':id}
        await users_apis.sendToTeamAdmins(fs_match_dict['team_id'],'Press \'Start the match\' in TeamMate',f"Match vs {fs_match_dict['opposition']} starting soon",metadata,'match')
        

@fcatimer
async def notifyAllAdmins(event,context):
    await initialise_firebase()

    
    fs_teams = await getAllObjects('users_store')
#     emails = ['all','only_accepted']
 
#     fs_matches = await whereIn('devices','sync_calendar',emails)
#     if(fs_matches):
#         print(fs_matches)
#         i = 0
#         for  fs_match in fs_matches:
#             fs_match_dict = fs_match.to_dict()
            
#             await users_apis.sendNotifications([fs_match_dict['email']],f"Good afternoon\
# \n\nWe wanted to let you know that we are temporarily switching off the calendar sync feature that you are using. This is because a small number of our users have identified an issue.\
# \n\nOur developers are looking into this as we speak and we hope to get this feature back with you in a future release. Sorry for any inconvenience.",'Calendar Sync Switchoff',{},'information')
#             await updateDocument('devices',fs_match.id,{'sync_calendar':firestore.DELETE_FIELD,'default_calendar':firestore.DELETE_FIELD})
    
    if(fs_teams):
        for fs_team in fs_teams:

            fs_team_dict  =  fs_team
            if(len(fs_team_dict.get('admin',[]))>0):
                await users_apis.sendNotifications([fs_team_dict['email']],f"Sorry\
\n\nWe had failed to press the release button for iOS apps. The new version is now available.\
\n\n Good luck for the weekend!",'TeamMate iOS app now available',{},'new_version',send_os='ios')
                
 # await users_apis.sendNotifications([fs_team_dict['email']],f"Download the latest version of TeamMate.\
                




@fcatimer
async def notifyIndividuals(event,context):
    await initialise_firebase()

    notified = await getObject('new_version','notify')
   
    if(notified):
        notified_dict = notified.get().to_dict()
        print(notified_dict)
        emails = notified_dict['emails']
        await users_apis.sendNotifications(emails,f"Download the latest version of TeamMate.\
\n\nTeam Mate Update: Smarter, sleeker & more powerful! \
\nWe’ve been working hard to make Team Mate even better for football coaches, players, and parents! Here’s what’s new:\
\n\n- Fresh new look & feel: A redesigned of the App that’s more intuitive and engaging for a seamless experience.\
\n- AI-Powered training plans: Coaches simply enter their training session needs, and our AI generates structured UEFA-based training plans to level up their sessions!\
\n- Match history feature: Get valuable insights by viewing past results of your upcoming opponents to help your team prepare smarter.\
\n\nThese upgrades mean easier coaching, better insights, and smoother communication for everyone involved. Update now and take your team to the next level!",'Download the latest version of TeamMate',{},'new_version',versions=['android.3.0.36','ios.3.0.36'])
        

            

@fcatimer
async def notifyAllWithNews(event,context):
    await initialise_firebase()

    
    fs_teams = await getAllObjects('users_store')
    if(fs_teams):
        for fs_team in fs_teams:

            fs_team_dict  =  fs_team
            
            await users_apis.sendNotifications([fs_team_dict['email']],f"Download the latest version of TeamMate.\
\n\nTeam Mate Update: Smarter, sleeker & more powerful! \
\nWe’ve been working hard to make Team Mate even better for football coaches, players, and parents! Here’s what’s new:\
\n\n- Fresh new look & feel: A redesigned of the App that’s more intuitive and engaging for a seamless experience.\
\n- AI-Powered training plans: Coaches simply enter their training session needs, and our AI generates structured UEFA-based training plans to level up their sessions!\
\n- Match history feature: Get valuable insights by viewing past results of your upcoming opponents to help your team prepare smarter.\
\n\nThese upgrades mean easier coaching, better insights, and smoother communication for everyone involved. Update now and take your team to the next level!",'Download the latest version of TeamMate.',{},'new_version',versions=['android.3.0.39','ios.3.0.39'])
                   



@fcatimer
async def daily_update_matches(event,context):

    await initialise_firebase()
    where_status = firestore.FieldFilter('status', 'not-in', ['ended','started','rated','restarted','paused','cancelled'])
    

    fs_matches = await whereEqualwhere('matches_store',wheres=[where_status])
    if(fs_matches):
        
        i = 0
        for  fs_match in fs_matches:
            try:
                fs_match_dict = fs_match.to_dict()
                date_string = fs_match_dict['date']
                date = parse(date_string)
                date = date -datetime.timedelta(hours=1)
                new_date = date.replace(tzinfo=datetime.timezone.utc)
                fs_match_dict['date'] = date
                await updateDocument('matches_store',fs_match_dict['id'],fs_match_dict)
            except (ValueError, TypeError) as e:
                # Handle invalid date formats and non-string inputs
                print(f"Error parsing date: {date}. Reason: {e}")

@fcatimer
async def retrieve_match_by_id(event,context):
    await lambda_handler(event,context)
    pathParameters = event["pathParameters"]
    queryParameters = event.get("queryStringParameters",{})
    match_id = pathParameters["match_id"]
    headers = event['headers']
    etag = headers.get('etag',None)
    print(f"USER HEADERS {headers}")
    refresh= None
    if(queryParameters):
        refresh = queryParameters.get("refresh",None)
    print(f"QUERY PARAMETERS: {queryParameters}")
    matches = []

    try:
        response = await matches_backend.getMatchFromDB(match_id)
        api_helper.make_api_response(200,response)
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        print(errors)
        response = api_helper.make_api_response(400,None,errors)
        return response
    except ValueError as e:
        print(e)
        response = api_helper.make_api_response(400,None)
        return response





@fcatimer
async def updateStatus(event,context):
    pathParameters = event["pathParameters"]
    match_id = pathParameters["match_id"]
    status = pathParameters["status"]
    matches_backend.updateStatus(match_id,status)

    await deleteEtag(match_id,'matches')
    response = api_helper.make_api_response(200,{})






