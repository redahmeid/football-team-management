import json
from pydantic import TypeAdapter, ValidationError
from exceptions import AuthError
import traceback
import sys
import api_helper
import response_errors
from team_data import save_team,save_group_team
from secrets_util import getEmailFromToken, lambda_handler
from auth import set_custom_claims
import boto3
from auth import check_permissions
from roles import Role
from dateutil.parser import parse,isoparse
from team_backend import getTeamFromDB
from etag_manager import getObject,whereEqual,updateDocument
from email_sender import send_email_with_template
import id_generator
from cache_trigger import updateUserCache
import json
import team_backend

from classes import User,Team,TeamUser, GroupTeam

from config import app_config
import exceptions
from users_data import retrieve_user_id_by_email,update_user
from team_data import save_team
from secrets_util import getEmailFromToken, lambda_handler, initialise_firebase
import api_helper

from auth import set_custom_claims
from notifications import sendNotification, sendNotificationUpdatesLink
from datetime import datetime,timezone

from fcatimer import fcatimer





async def addUserToTeam(event,context):
    await lambda_handler(event,context)
    acceptable_roles = [Role.admin.value,Role.coach.value]
    team_id = event["pathParameters"]["team_id"]
    body =json.loads(event["body"])
    emails = body["emails"]
    if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
        results = []
        await team_backend.addTeamToUser(emails,team_id)
        results = await team_backend.addUserToTeam(emails,team_id,Role.coach)
            
        
        
        data = {
            "link":f"/teams/{team_id}",
            "team_id":f"{team_id}",
            "action":"new_users",
            "silent":"False"
        }
        await sendNotificationUpdatesLink(getEmailFromToken(event,context),f"Welcome your new coaches",f"New coach added to {results['team_name']}",'team',data)
        response = api_helper.make_api_response(200,results['results'])
    else:
            response = api_helper.make_api_response(403,None,"You do not have permission to edit this match")
    return response


@fcatimer
async def notifyCoaches(team_id,email):
    fs_team = await getObject(team_id,'teams_store')
    if(fs_team):
        fs_team_dict = fs_team.get().to_dict()
        

        template_data = {'team':fs_team_dict['name'],'age_group':fs_team_dict['age_group']}
        fs_user = await getObject(email,'users_store')
        if(fs_user):
            fs_user_dict = fs_user.get().to_dict()
            
            
            await send_email_with_template(email,'d-9ba5fab4e96a4a56819aeba57916356f',template_data)
            message = f"You have been added as a coach to {fs_team_dict['name']}"
            notification_id = id_generator.generate_random_number(10)
            
            fs_devices = await whereEqual('devices','email',email)
            metadata={"team_id":team_id,'notification_id':notification_id}
            if(fs_devices):
                
                for fs_device in fs_devices:
                    fs_device_dict = fs_device.to_dict()
                    
                    await sendNotification(type="invitation",token=fs_device_dict["token"],message=message,silent=False,subject="You've been added as a coach",id=team_id,metadata=metadata)
            notification = {
                            'message':message,
                            'metadata':metadata,
                            'email':email,
                            'type':'team',
                            'subject':f"You've been added as a coach",
                            'sent':datetime.now(timezone.utc)
                        }
            await updateDocument('user_notifications',str(notification_id),notification)

@fcatimer
async def notifyNewCoaches(event,context):
    await lambda_handler(event,context)
    player_id = event["pathParameters"]["team_id"]
    body =json.loads(event["body"])
    
    email = body["email"]
    await notifyCoaches(player_id,email)


@fcatimer
async def submit_team(event, context):
    await lambda_handler(event,context)
    body =json.loads(event["body"])
    teams = []
    try:
        email = getEmailFromToken(event,context)
       
        id = str(id_generator.generate_random_number(7))
        team_id = str(id_generator.generate_random_number(7))
        
        user = await retrieve_user_id_by_email(email)
        team = Team(id=team_id,age_group=body["age_group"],name=body["name"],season=body["season"],admins=[{'email':email,'role':Role.admin.value}],settings={'show_ratings':True})
        save_response = await save_team(team,team_id)
        group_team = GroupTeam(teams=[team_id],id=id)
        await save_group_team(group_team,id)
        user.admin.append(team_id)
        user.teams.append(team_id)
        await update_user(email,user)
        # data, count = supabase.table('teams').insert({"id": id, "name": body["name"],"age_group":body["age_group"],"season":body["season"],"team_id":team_id}).execute()
           
        message = f"{team.name} has been created"
        subject = 'New team added'
        data = {
            "link":f"/teams/{team_id}",
            "team_id":f"{team_id}",
            "action":"new_team",
            "silent":"True"
        }
        await sendNotificationUpdatesLink(email,message,subject,'team',data)
        await set_custom_claims(event,context)
        response = api_helper.make_api_response(200,team.model_dump())
    except exceptions.AuthError as e:
    
        traceback.print_exception(*sys.exc_info()) 
        print(e)
        response = api_helper.make_api_response(401,None,e)
    except Exception as e:
        traceback.print_exception(*sys.exc_info()) 
        print(e)
        response = api_helper.make_api_response(400,None,e)
    return response


# @fcatimer
# async def sendGuardianEmail(player_id,email):
#     fs_player = await getObject(player_id,'players_store')
#     if(fs_player):
#         fs_player_dict = fs_player.get().to_dict()
#         fs_team = await getObject(fs_player_dict['info']['team_id'],'teams_store')
#         if(fs_team):
#             fs_team_dict = fs_team.get().to_dict()
            

#             template_data = {'player':fs_player_dict['info']['forename'],'team':fs_team_dict['name']}
#             fs_user = await getObject(email,'users_store')
#             if(fs_user):
#                 fs_user_dict = fs_user.get().to_dict()
                
#                 if(fs_user_dict.get('last_seen',None)):
#                     await send_email_with_template(email,'d-d84865ab98a44c9aa6770e86364df6e5',template_data)
#                 else:
#                     await send_email_with_template(email,'d-0904ad249669492fb6999ff0102742f1',template_data)
#                 message = f"You have been added as a guardian to {fs_player_dict['info']['forename']}"
#                 notification_id = id_generator.generate_random_number(10)
               
#                 fs_devices = await whereEqual('devices','email',email)
#                 metadata={"player_id":fs_player_dict["info"]["id"],'notification_id':notification_id}
#                 if(fs_devices):
                    
#                     for fs_device in fs_devices:
#                         fs_device_dict = fs_device.to_dict()
                        
#                         await sendNotification(type="invitation",token=fs_device_dict["token"],message=message,silent=False,subject="You've been added as a guardian",id=fs_player_dict["info"]["id"],metadata=metadata)
#                 notification = {
#                                 'message':message,
#                                 'metadata':metadata,
#                                 'email':email,
#                                 'type':'guardian_add',
#                                 'subject':f"You've been added to {fs_player_dict['info']['forename']}",
#                                 'sent':datetime.now(timezone.utc)
#                             }
#                 await updateDocument('user_notifications',str(notification_id),notification)


@fcatimer
async def retrieve_team_summary(event, context):
    await lambda_handler(event,context)
    
    team_id = event["pathParameters"]["team_id"]
    headers = event['headers']
    etag = headers.get('etag',None)
    print(f"USER HEADERS {headers}")
    
    teams = []

    try:
       
        response = await getTeamFromDB(team_id)

        print(f"RETRIEVE TEAM SUMMARY RESPONSE {response}")    
        return api_helper.make_api_response_etag(200,[response.model_dump()],etag)    
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
async def delete_team(event, context):
    await lambda_handler(event,context)
    
    team_id = event["pathParameters"]["team_id"]
    headers = event['headers']
 

    try:
        
        await team_backend.deleteTeam(team_id)
        await updateUserCache(getEmailFromToken(event,context))
        return api_helper.make_api_response(201,[])    
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
async def player_team_conceded_calculation(event,context):
    await initialise_firebase()
    team_id = event['team_id']
    fs_matches = await whereEqual('matches_store','team_id',team_id)
    if(fs_matches):
        for fs_match in fs_matches:
            fs_match_dict = fs_match.to_dict()
            
            if(fs_match_dict.get('status','')=='ended' or fs_match_dict.get('status','')=='rated'):
                fs_match_conceded = fs_match_dict.get('opposition_goals',[])
        
                
                lineups = fs_match_dict['actual_lineups']
                for i in range(len(lineups)):
                    j = i+1
                    this_lineup = lineups[i]
                    if(j<len(lineups)):
                        next_lineup = lineups[j]
                        next_lineup_minute = float(next_lineup["status"])
                
                        
                    this_lineup_minute = float(this_lineup["status"])
                    
                    team_conceded_analysis = fs_match_dict.get("team_conceded_analysis",False)
                    if(not team_conceded_analysis):
                        for conceded in fs_match_conceded:
                            minute = conceded["new_minutes"]
                            if(minute<next_lineup_minute and minute>this_lineup_minute) or (not next_lineup_minute and minute>this_lineup_minute):
                                for player in this_lineup["players"]:
                                    if(player["selectionInfo"]["position"]!=""):
                                        fs_player = await getObject(player['info']['id'],"players_store")
                                        if(fs_player):
                                            fs_player_dict = fs_player.get().to_dict()
                                            player_stats = fs_player_dict['playerStats']
                                            player_stats_conceded = player_stats.get('team_conceded',0)
                                            player_stats_conceded = player_stats_conceded+1
                                            player_stats['team_conceded'] = player_stats_conceded
                                            fs_player_dict['playerStats'] = player_stats
                                            await updateDocument('players_store',fs_player_dict['info']['id'],fs_player_dict)
                fs_match_dict["team_conceded_analysis"] = True
                await updateDocument('matches_store',fs_match_dict["id"],fs_match_dict)

@fcatimer
async def player_team_goals_calculation(event,context):
    await initialise_firebase()
    

    

    team_id = event['team_id']
    fs_matches = await whereEqual('matches_store','team_id',team_id)
    
    if(fs_matches):
        for fs_match in fs_matches:
            fs_match_dict = fs_match.to_dict()
            
            if(fs_match_dict.get('status','')=='ended' or fs_match_dict.get('status','')=='rated'):
               
                print(f"FS MATCH {fs_match_dict['id']}")
                fs_match_goals = fs_match_dict.get('scorers',[])
                print(f"FS MATCH GOALS {len(fs_match_goals)}")
                lineups = fs_match_dict['actual_lineups']
                print(f"FS MATCH LINEUPS {len(lineups)}")
                for i in range(len(lineups)):
                    print(f"FS MATCH COUNT {i}")
                    j = i+1
                    this_lineup = lineups[i]
                    if(j<len(lineups)):
                        next_lineup = lineups[j]
                        next_lineup_minute = float(next_lineup["status"])
                    else:
                        next_lineup_minute = None

                        
                    this_lineup_minute = float(this_lineup["status"])
                        
                    team_goals_analysis = fs_match_dict.get("team_goals_analysis",False)
                    if(not team_goals_analysis):
                        for goal in fs_match_goals:
                            
                            minute = goal["new_minutes"]
                            print(f"MINUTE {minute} NEXT LINE UP {next_lineup_minute} THIS LINE UP {this_lineup_minute}")
                            if(minute<=next_lineup_minute and minute>this_lineup_minute) or (not next_lineup_minute and minute>=this_lineup_minute):
                                print(f"IN ADD TEAM GOALS")
                                for player in this_lineup["players"]:
                                    print(f"PLAYER {player['info']['forename']} POSITION {player['selectionInfo']['position']}")
                                    if(player["selectionInfo"]["position"]!=""):
                                        fs_player = await getObject(player['info']['id'],"players_store")
                                        if(fs_player):
                                            print(f"FOUND PLAYER")
                                            fs_player_dict = fs_player.get().to_dict()
                                            player_stats = fs_player_dict['playerStats']
                                            player_stats_goals = player_stats.get('team_goals',0)
                                            player_stats_goals = player_stats_goals+1
                                            print(f"PLAYER STATS GOALS {player_stats_goals}")
                                            player_stats['team_goals'] = player_stats_goals
                                            print(f"PLAYER STATS {player_stats}")
                                            fs_player_dict['playerStats'] = player_stats
                                            await updateDocument('players_store',fs_player_dict['info']['id'],fs_player_dict)
                fs_match_dict["team_goals_analysis"] = True 
                await updateDocument('matches_store',fs_match_dict["id"],fs_match_dict)


from datetime import datetime

def is_date_in_past(date_str):
  date_obj = datetime.strptime(date_str, '%Y-%m-%d')  # Replace with correct format
  return date_obj < datetime.now().date()


@fcatimer
async def player_training_attended_calculation(event,context):
    await initialise_firebase()

    team_id = event['team_id']
    fs_matches = await whereEqual('matches_store','team_id',team_id)
    
    if(fs_matches):
        for fs_match in fs_matches:
            fs_match_dict = fs_match.to_dict()
            in_past = is_date_in_past(fs_match_dict['date'])
            if(in_past):
                fs_match_invitees = fs_match_dict.get('invites',[])
                if(fs_match_invitees):
                    for invite in fs_match_invitees:
                        response = invite.get('response','')
                        id = invite['player']['info']['id']
                        if(response=='accepted'):
                            fs_player = await getObject(id,'players_store')
                            if(fs_player):
                                fs_player_dict = fs_player.get().to_dict()
                                player_stats = fs_player_dict.get('playerStats',{})
                                player_stats_training_attended = player_stats.get('training_attended',0)
                                player_stats_training_attended = player_stats_training_attended+1
                                player_stats['training_attended'] = player_stats_training_attended
                                fs_player_dict['playerStats'] = player_stats
                                await updateDocument('players_store',id,fs_player_dict)
                fs_match_dict["training_attendance_analysis"] = True 
                await updateDocument('matches_store',fs_match_dict["id"],fs_match_dict)


@fcatimer
async def team_stats_calculator(event,context):
    await lambda_handler(event,context)
    params = event.get('pathParameters',None)
    if(params):
        team_id = event["pathParameters"]["team_id"]
    else:
        team_id = event['team_id']
    event = {'team_id':team_id}
    fs_flags = await getObject('team_stats_calculator','feature_flags')
    if(fs_flags):
        fs_flags_dict = fs_flags.get().to_dict()
        if(fs_flags_dict['enabled']==True):
            lambda_client = boto3.client('lambda')
            
            # CALCULATE TEAM GOALS 
            lambda_client.invoke(
            FunctionName=app_config.calculate_team_goals,  # Name of the target Lambda
            InvocationType='Event',
            Payload=json.dumps(event)  # Asynchronous invocation
            )

            # CALCULATE TEAM CONCEDED
            lambda_client.invoke(
            FunctionName=app_config.calculate_team_conceded,  # Name of the target Lambda
            InvocationType='Event',
            Payload=json.dumps(event)  # Asynchronous invocation
            ) 

            # CALCULATE TEAM CONCEDED
            lambda_client.invoke(
            FunctionName=app_config.calculate_training_attended,  # Name of the target Lambda
            InvocationType='Event',
            Payload=json.dumps(event)  # Asynchronous invocation
            ) 


# Schedule every 3 hours but will only update those that were checked more than 1 day ago
# This is to allow handling of too many teams (i.e. only loop round teams that have not recently been checked)
@fcatimer
async def updateTeamStats(event,context):
    await initialise_firebase()
    fs_matches = await whereEqual('teams_store','stats_last_checked',)
    for fs_match in fs_matches:
        secretsmanager = boto3.client('secretsmanager')
        event = fs_match.to_dict()
        lambda_client = boto3.client('lambda')
        lambda_client.invoke(
        FunctionName=app_config.schedule_invitations,  # Name of the target Lambda
        InvocationType='Event',
        Payload=json.dumps(event)  # Asynchronous invocation
        ) 


# @fcatimer
# def convertTeamDataToTeamResponse(team) -> response_classes.TeamResponse:
#     print("convertTeamDataToTeamResponse: %s"%(team))
#     id = team["ts.ID"]
#     baseTeamUrl = "/teams/%s"%(id)
#     name = team["Name"]
#     ageGroup = team["Age_Group"]
#     live = team["live"]
#     print("Convert team live %s"%(live))
#     if(live == None):
#         live = True
#     self = response_classes.Link(link=baseTeamUrl,method="get")
#     players = response_classes.Link(link="%s/players"%(baseTeamUrl),method="get")
#     fixtures= response_classes.Link(link="%s/matches"%(baseTeamUrl),method="get")
#     addPlayers = response_classes.Link(link="%s/players"%(baseTeamUrl),method="post")
#     addFixtures = response_classes.Link(link="%s/matches"%(baseTeamUrl),method="post")
#     nextMatch = response_classes.Link(link="%s/next_match"%(baseTeamUrl),method="get")

#     response =  response_classes.TeamResponse(id=id,name=name,ageGroup=ageGroup,live=live,self=self,nextMatch=nextMatch,teamPlayers=players,teamFixtures=fixtures,addFixtures=addFixtures,addPlayers=addPlayers)
#     print("Convert team %s"%(response))
#     return responseitemAxis