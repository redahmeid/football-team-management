import json
from pydantic import TypeAdapter, ValidationError
from exceptions import AuthError
import traceback
import users_apis
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
from etag_manager import getObject,whereEqual,updateDocument,getAllObjects,whereEqualwhere,whereEqualwhereOr
from email_sender import send_email_with_template
import id_generator
from google.cloud import firestore
from cache_trigger import updateUserCache
import json
import team_backend

from classes import User,Team,TeamUser, GroupTeam

from config import app_config
import exceptions
from users_data import retrieve_user_id_by_email,update_user

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
    tokens={}
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
                    silent = False
                    if(fs_device_dict['version']):
                                    silent = str((users_apis.is_version_greater(fs_device_dict['version'],'android.3.0.34') or users_apis.is_version_greater(fs_device_dict['version'],'ios.3.0.34')))
                    isNotifiable = fs_device_dict.get('notifications',True)

                    if(isNotifiable):
                        token=fs_device_dict["token"]
                        if(not tokens[token]):
                            tokens[token] =True
                            await sendNotification(type="invitation",token=fs_device_dict["token"],message=message,silent=silent,subject="You've been added as a coach",id=team_id,metadata=metadata)
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
async def set_has_squad(team):

    if(len(team.get('squad',[]))>4):
               admins = team.get('admins',[])
            
               coaches = team.get('coaches',[])
               admins = coaches+admins
               for email in admins:
                    
                    await updateDocument('user_activity',email['email'],{'has_squad':True,'teams':firestore.ArrayUnion([team['name']])})
    else:
            admins = team.get('admins',[])
            coaches = team.get('coaches',[])
           
            for email in admins:
                activity = await getObject(email['email'],'user_activity')
                if(activity):
                    activity_dict = activity.get().to_dict()
                    has_squad = False
                    if(activity_dict.get('has_squad',False)):
                        has_squad = True
                user = await getObject(email['email'],'users_store')
                user_dict = {}
                if(user):
                    user_dict = user.get().to_dict()
                await updateDocument('user_activity',email['email'],{'name':user_dict.get('name',""),'has_squad':has_squad,'teams':firestore.ArrayUnion([team['name']])})   

@fcatimer
async def set_has_matches(team):
    matches = await whereEqual('matches_store','team_id',team['id'])
    if(len(matches)>0):
               admins = team.get('admins',[])
               coaches = team.get('coaches',[])
               admins = coaches+admins
               for email in admins:
                    await updateDocument('user_activity',email['email'],{'has_matches':True})
    else:
            admins = team.get('admins',[])
            coaches = team.get('coaches',[])
            admins = coaches+admins
            for email in admins:
                activity = await getObject(email['email'],'user_activity')
                if(activity):
                    activity_dict = activity.get().to_dict()
                    has_matches = False
                    if(activity_dict.get('has_matches',False)):
                        has_matches = True
                user = await getObject(email['email'],'users_store')
                user_dict = {}
                if(user):
                    user_dict = user.get().to_dict()
                await updateDocument('user_activity',email['email'],{'name':user_dict.get('name',""),'has_matches':has_matches}) 

@fcatimer
async def set_user_activity(event,context):
    await initialise_firebase()
    teams = await getAllObjects('teams_store')
    for team in teams:
        await set_has_squad(team)
        await set_has_matches(team)
            
           

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


@fcatimer
async def calculate_teams_stats(event,context):
    await initialise_firebase()
    teams = await getAllObjects('teams_store')
    for team in teams:
        team_dict = team
        id = team_dict['id']
        event = {'id':id}
        lambda_client = boto3.client('lambda')
         # CALCULATE TEAM GOALS 
        lambda_client.invoke(
        FunctionName=app_config.calculate_team_stats,  # Name of the target Lambda
        InvocationType='Event',
        Payload=json.dumps(event)  # Asynchronous invocation
        )

@fcatimer
async def calculate_goals_by_minutes(homeOrAway,team_stats_dict,match_type,length,match_dict):
    index = 0
    scorers = match_dict.get('scorers',[])
    for scorer in scorers:
        scorer_minute = scorer.get('new_minutes',scorer['minute'])
        loop = True
        goal_type = scorer.get('type',"")
        assist_type =  scorer.get('assist_type',"")

        total_goal_types = team_stats_dict.get(f'total_{goal_type}_goals',0)
        total_assist_types = team_stats_dict.get(f'total_{assist_type}_assists',0)
        total_goal_types = total_goal_types+1
        total_assist_types = total_assist_types+1
        team_stats_dict[f'total_{goal_type}_goals']=total_goal_types
        team_stats_dict[f'total_{assist_type}_assists']=total_assist_types
        while (index < length and loop):
            minutes_from = index
            minutes_to = index + 5
            if(scorer_minute>=minutes_from and scorer_minute<minutes_to):
                field_name = f"goals_{minutes_from}_to_{minutes_to}"
                type_field_name = f"{match_type}_goals_{minutes_from}_to_{minutes_to}"
                home_type_field = f"{match_type}_{homeOrAway}_goals_{minutes_from}_to_{minutes_to}"
                goal_minutes = team_stats_dict.get(field_name,0)
                goal_minutes = goal_minutes+1
                type_goal_minutes = team_stats_dict.get(type_field_name,0)
                type_goal_minutes = type_goal_minutes+1
                home_goals_minutes = team_stats_dict.get(home_type_field,0)
                home_goals_minutes = home_goals_minutes+1
                team_stats_dict[home_type_field] = home_goals_minutes
                team_stats_dict[field_name] = goal_minutes
                team_stats_dict[type_field_name] = type_goal_minutes
                await updateDocument('teams_stats',team_stats_dict['id'],team_stats_dict)
                loop = False
            index = index+5
    

@fcatimer
async def calculate_team_stats(event,context):
    await initialise_firebase()
    team_id = event['id']
    print(f"TEAM_ID {team_id}")
    where_team_id = firestore.FieldFilter('team_id', '==' , team_id)
    where_status = firestore.FieldFilter('status', 'in' , ['ended','rated'])
    matches = []
    ended_matches = await whereEqualwhere('matches_store',[where_team_id,where_status])
    matches.extend(ended_matches)
    print(f"LENGTH {len(matches)}")
    new_matches= []
    for match in matches:
        match_dict = match.to_dict()
        new_matches.append(match_dict)
        await teams_stats_v1(match_dict,team_id)
    
    new_matches.sort(key=lambda match:match['date'])
    await calculate_team_rating(new_matches,team_id)
    await calculate_player_minutes(new_matches)
    await calculate_player_goals(new_matches)
    await calculate_player_rating(new_matches)


@fcatimer
async def calculate_player_minutes(matches):
  
    players_stats = {}
    i=1
    
    print(f"MATCHES LENGTH = {len(matches)}")
    
    for match in matches:
        print(f'I IS {i}')
        j=1
        lineups = match.get('actual_lineups',[])
        print(f"LINEUPS LENGTH = {len(lineups)}")
        last_minute = 0
        last_players = []
        
        for lineup in lineups:
            minutes = float(lineup['status'])
            players = lineup['players']
            
            
            print(f"PLAYERS LENGTH = {len(players)}")
            if(len(last_players)>0):
                minutes_played = minutes-last_minute
                print(f"LAST PLAYERS LENGTH = {len(last_players)}")
                for player in last_players:

                    id = player['info']['id']
                    player_stat = players_stats.get(id,{'id':id,'team_id':match['team_id']})
                    
                    if(len(player_stat)==0):
                        player_stat_doc = await getObject(id,'players_stats')
                        if(player_stat_doc):
                            player_stat = player_stat_doc.get().to_dict()
                    matches_played = player_stat.get('matches_played',0)+j
                    matches_played_type = player_stat.get(f"total_matches_played_{match['type']}",0)+j
                    matches_played_type_homeoraway = player_stat.get(f"total_matches_played_{match['type']}_{match['homeOrAway']}",0)+j
                    player_stat['matches_played']=matches_played
                    player_stat[f"total_matches_played_{match['type']}"]=matches_played_type
                    player_stat[f"total_matches_played_{match['type']}_{match['homeOrAway']}"]=matches_played_type_homeoraway
                    
                    position = player['selectionInfo']['position']
                    print(f'POSITION {position}')
                    if(position):
                        total_minutes = player_stat.get('total_minutes',0)
                        total_minutes = total_minutes+minutes_played
                        player_stat['total_minutes'] = total_minutes

                        total_minutes_position = player_stat.get(f'total_minutes_{position}',0)
                        total_minutes_position = total_minutes_position+minutes_played
                        player_stat[f'total_minutes_{position}'] = total_minutes

                        total_minutes_type_position = player_stat.get(f"total_minutes_{match['type']}_{position}",0)
                        total_minutes_type_position = total_minutes_type_position+minutes_played
                        player_stat[f"total_minutes_{match['type']}_{position}"] = total_minutes_type_position

                        total_minutes_type_home_or_away_position = player_stat.get(f"total_minutes_{match['type']}_{match['homeOrAway']}_{position}",0)
                        total_minutes_type_home_or_away_position = total_minutes_type_home_or_away_position+minutes_played
                        player_stat[f"total_minutes_{match['type']}_{match['homeOrAway']}_{position}"] = total_minutes_type_home_or_away_position
                    players_stats[id] = player_stat    
                
                    if(len(matches)==i):
                       
                        print(f'PLAYER STATS {player_stat}')
                        await updateDocument('players_stats',id,player_stat) 
                j=0  
            last_players=players  
            
            print(f"LAST PLAYERS LENGTH = {len(last_players)}")  
            last_minute = minutes
        i=i+1


@fcatimer
async def calculate_player_goals(matches):
  
    players_stats = {}
    i=1
    print(f"MATCHES LENGTH = {len(matches)}")
    for match in matches:
        print(f'I IS {i}')
        scorers = match.get('scorers',[])
       
        for scorer in scorers:
            minutes = float(scorer['new_minutes'])
            goal_scorer_id = scorer['player']['id']
            assister_id = scorer['secondary_player']['id']
            
            goal_scorer_stats_obj = await getObject(goal_scorer_id,'players_stats')
            goal_scorer_stats = {'id':goal_scorer_id,'team_id':match['team_id']}
            if(goal_scorer_stats_obj):
                goal_scorer_stats = goal_scorer_stats_obj.get().to_dict()
            
            total_goals = goal_scorer_stats.get('total_goals',0)+1
            
            total_goals_type = goal_scorer_stats.get(f"total_goals_{match['type']}",0)+1
            total_goals_type_home_or_away = goal_scorer_stats.get(f"total_goals_{match['type']}_{match['homeOrAway']}",0)+1
            goal_scorer_stats['total_goals']= total_goals
            goal_scorer_stats[f"total_goals_{match['type']}"] = total_goals_type
            goal_scorer_stats[f"total_goals_{match['type']}_{match['homeOrAway']}"] = total_goals_type_home_or_away
            
            await updateDocument('players_stats',goal_scorer_id,goal_scorer_stats)    

            assister_stats_obj = await getObject(assister_id,'players_stats')
            assister_stats = {'id':assister_id,'team_id':match['team_id']}
            if(assister_stats_obj):
                assister_stats = assister_stats_obj.get().to_dict()
            
            total_assists = assister_stats.get('total_assists',0)+1
            
            total_assists_type = assister_stats.get(f"total_assists_{match['type']}",0)+1
            total_assists_type_home_or_away = goal_scorer_stats.get(f"total_assists_{match['type']}_{match['homeOrAway']}",0)+1
            assister_stats['total_assists']= total_assists
            assister_stats[f"total_assists_{match['type']}"] = total_assists_type
            assister_stats[f"total_assists_{match['type']}_{match['homeOrAway']}"] = total_assists_type_home_or_away
            
            await updateDocument('players_stats',assister_id,assister_stats)    

        i=i+1    
@fcatimer
async def calculate_player_rating(matches):
  
    rated_player_matches = {}
    i=1
    print(f"MATCHES LENGTH = {len(matches)}")
    for match in matches:
        print(f'I IS {i}')
        match_status = match['status']
        if(match_status=='rated'):
            ratings = match.get('ratings',[])
        
            for rating in ratings:
                
                rating_id = rating['info']['id']
                # assister_id = scorer['secondary_player']['id']
                

            
                goal_scorer_stats_obj = await getObject(rating_id,'players_stats')
                goal_scorer_stats = {'id':rating_id,'team_id':match['team_id']}
                if(goal_scorer_stats_obj):
                    goal_scorer_stats = goal_scorer_stats_obj.get().to_dict()
                
                match_rating = float(rating['matchPlayerRating']['overall'])
                

                ratings_history = goal_scorer_stats.get('ratings_history',[])
                if(len(ratings_history)>0):
                    rating_history = ratings_history[-1].copy()
                    rating_history['date'] = match['date']
                else:
                    rating_history = {'date':match['date']}

                total_rating = goal_scorer_stats.get('total_rating',0)+match_rating
                total_rating_type =  goal_scorer_stats.get(f"total_rating_{match['type']}",0)+match_rating
                total_rating_type_home_or_away =  goal_scorer_stats.get(f"total_rating_{match['type']}_{match['homeOrAway']}",0)+match_rating
                matches_rated = goal_scorer_stats.get('matches_rated',0)+1
                total_matches_rated_type =  goal_scorer_stats.get(f"total_matches_rated_{match['type']}",0)+1
                total_matches_rated_type_home_or_away =  goal_scorer_stats.get(f"total_matches_rated_{match['type']}_{match['homeOrAway']}",0)+1
                goal_scorer_stats['total_rating']= total_rating
                goal_scorer_stats[f"total_rating_{match['type']}"] = total_rating_type
                goal_scorer_stats[f"total_rating_{match['type']}_{match['homeOrAway']}"] = total_rating_type_home_or_away
                goal_scorer_stats['matches_rated'] = matches_rated
                goal_scorer_stats[f"total_matches_rated_{match['type']}"] = total_matches_rated_type
                goal_scorer_stats[f"total_matches_rated_{match['type']}_{match['homeOrAway']}"] = total_matches_rated_type_home_or_away
                
                rating_history['total_rating']= total_rating
                rating_history[f"total_rating_{match['type']}"] = total_rating_type
                rating_history[f"total_rating_{match['type']}_{match['homeOrAway']}"] = total_rating_type_home_or_away
                rating_history['matches_rated'] = matches_rated
                rating_history[f"total_matches_rated_{match['type']}"] = total_matches_rated_type
                rating_history[f"total_matches_rated_{match['type']}_{match['homeOrAway']}"] = total_matches_rated_type_home_or_away


                ratings_history.append(rating_history)
                goal_scorer_stats['ratings_history'] = ratings_history
                await updateDocument('players_stats',rating_id,goal_scorer_stats)    
            i=i+1    


@fcatimer
async def calculate_team_rating(matches,team_id):
    team_stats = await getObject(team_id,"teams_stats")
    team_stats_dict = {'id':team_id}
    if(team_stats):
        team_stats_dict = team_stats.get().to_dict()
    numberOfMatches = 0
    overallRating = 0
    friendlyOverallRating = 0
    leagueOverallRating = 0
    trophyOverallRating = 0

    averageRating = 0
    ratingHistory = []
    friendlyAverage = 0
    numberOfFriendlyMatches = 0
    numberOfLeagueMatches = 0
    numberOfTrophyMatches = 0
    leagueAverage = 0
    trophyAverage = 0
    friendlyRatingHistory = []
    leagueRatingHistory = []
    trophyRatingHistory = []
    for match in matches:
        if(match['status']=='rated'):
            rating = match['match_rating']
            overallRating = overallRating+rating
            numberOfMatches = numberOfMatches+1
            averageRating=overallRating/numberOfMatches
            history = {'date':match['date'],'rolling_average':averageRating}
            ratingHistory.append(history)
            if(match['type']=='friendly'):
                friendlyOverallRating = friendlyOverallRating+rating
                numberOfFriendlyMatches = numberOfFriendlyMatches+1
                friendlyAverage=friendlyOverallRating/numberOfFriendlyMatches
                history = {'date':match['date'],'rolling_average':friendlyAverage}
                friendlyRatingHistory.append(history)
            elif(match['type']=='league'):
                leagueOverallRating = leagueOverallRating+rating
                numberOfLeagueMatches = numberOfLeagueMatches+1
                leagueAverage=leagueOverallRating/numberOfLeagueMatches
                history = {'date':match['date'],'rolling_average':leagueAverage}
                leagueRatingHistory.append(history)
            elif(match['type']=='trophy'):
                trophyOverallRating = trophyOverallRating+rating
                numberOfTrophyMatches = numberOfTrophyMatches+1
                trophyAverage=trophyOverallRating/numberOfTrophyMatches
                history = {'date':match['date'],'rolling_average':trophyAverage}
                trophyRatingHistory.append(history)
    team_stats_dict['average_rating'] = averageRating
    team_stats_dict['average_friendly_rating'] = friendlyAverage
    team_stats_dict['average_league_rating'] = leagueAverage
    team_stats_dict['average_trophy_rating'] = trophyAverage
    team_stats_dict['rolling_average_rating'] = ratingHistory
    team_stats_dict['friendly_rolling_average_rating'] = friendlyRatingHistory
    team_stats_dict['league_rolling_average_rating'] = leagueRatingHistory
    team_stats_dict['trophy_rolling_average_rating'] = trophyRatingHistory
    await updateDocument('teams_stats',team_id,team_stats_dict)

    

    
    

       


@fcatimer
async def calculate_stats_by_match_type(team_stats_dict,goals,conceded,match_type,homeOrAway):
    field = f'total_{match_type}'

    homeOrAwayField = f'{field}_{homeOrAway}'

    total_type_played = team_stats_dict.get(f'{field}_played',0)+1
    total_type_homeaway_played = team_stats_dict.get(f'{homeOrAwayField}_played',0)+1
    team_stats_dict[f'{field}_played']=total_type_played
    team_stats_dict[f'{homeOrAwayField}_played']=total_type_homeaway_played

    team_type_goals = team_stats_dict.get(f'{field}_goals',0)
    team_type_goals = team_type_goals+goals
    team_stats_dict[f'{field}_goals'] = team_type_goals

    team_type_conceded = team_stats_dict.get(f'{field}_conceded',0)
    team_type_conceded = team_type_conceded+conceded
    team_stats_dict[f'{field}_conceded'] = team_type_conceded

    team_type_wins = team_stats_dict.get(f'{field}_wins',0)
    team_type_wins = team_type_wins+1 if (goals>conceded) else team_type_wins
    team_stats_dict[f'{field}_wins'] = team_type_wins

    team_type_losses = team_stats_dict.get(f'{field}_losses',0)
    team_type_losses = team_type_losses+1 if (goals<conceded) else team_type_losses
    team_stats_dict[f'{field}_losses'] = team_type_losses

    team_type_draws = team_stats_dict.get(f'{field}_draws',0)
    team_type_draws = team_type_draws+1 if (goals==conceded) else team_type_draws
    team_stats_dict[f'{field}_draws'] = team_type_draws

    team_type_goals = team_stats_dict.get(f'{homeOrAwayField}_goals',0)
    team_type_goals = team_type_goals+goals
    team_stats_dict[f'{homeOrAwayField}_goals'] = team_type_goals
    
    team_type_conceded = team_stats_dict.get(f'{homeOrAwayField}_conceded',0)
    team_type_conceded = team_type_conceded+conceded
    team_stats_dict[f'{homeOrAwayField}_conceded'] = team_type_conceded

    team_type_wins = team_stats_dict.get(f'{homeOrAwayField}_wins',0)
    team_type_wins = team_type_wins+1 if (goals>conceded) else team_type_wins
    team_stats_dict[f'{homeOrAwayField}_wins'] = team_type_wins

    team_type_losses = team_stats_dict.get(f'{homeOrAwayField}_losses',0)
    team_type_losses = team_type_losses+1 if (goals<conceded) else team_type_losses
    team_stats_dict[f'{homeOrAwayField}_losses'] = team_type_losses

    team_type_draws = team_stats_dict.get(f'{homeOrAwayField}_draws',0)
    team_type_draws = team_type_draws+1 if (goals>conceded) else team_type_draws
    team_stats_dict[f'{homeOrAwayField}_draws'] = team_type_draws






@fcatimer
async def teams_stats_v1(match_dict,team_id):
    
    goals = match_dict.get('goals',0)
    conceded = match_dict.get('conceded',0)
    homeOrAway = match_dict['homeOrAway']
    homeOrAwayGoalsField = f'total_{homeOrAway}_goals'
    homeOrAwayConcededField = f'total_{homeOrAway}_conceded'
    match_type = match_dict.get('type','')
    team_stats = await getObject(team_id,"teams_stats")
    
    team_stats_dict = {'id':team_id}
    if(team_stats):
        team_stats_dict = team_stats.get().to_dict()
    await calculate_goals_by_minutes(homeOrAway,team_stats_dict,match_type,match_dict['length'],match_dict)
    # await calculate_stats_by_goal_type(homeOrAway,team_stats_dict,match_type,match_dict['length'],match_dict)
    
    total_played = team_stats_dict.get('total_played',0)+1
    total_goals = team_stats_dict.get('total_goals',0)
    total_home_away_goals = team_stats_dict.get(homeOrAwayGoalsField,0)
    total_home_away_goals = total_home_away_goals+goals
    total_home_away_conceded = team_stats_dict.get(homeOrAwayConcededField,0)
    total_home_away_conceded = total_home_away_conceded+conceded
    total_goals = total_goals+goals
    total_conceded = team_stats_dict.get('total_conceded',0)
    total_conceded = total_conceded+conceded
    total_wins = team_stats_dict.get('total_wins',0)
    total_draws = team_stats_dict.get('total_draws',0)
    total_losses = team_stats_dict.get('total_losses',0)
    if(goals>conceded):
        total_wins = total_wins+1
    elif(goals<conceded):
        total_losses = total_losses+1
    else:
        total_draws = total_draws+1
    team_stats_dict['total_played'] = total_played
    team_stats_dict['total_wins'] = total_wins
    team_stats_dict['total_draws'] = total_draws
    team_stats_dict['total_losses'] = total_losses
    team_stats_dict['total_goals'] = total_goals
    team_stats_dict['total_conceded'] = total_conceded
    team_stats_dict[homeOrAwayGoalsField] = total_home_away_goals
    team_stats_dict[homeOrAwayConcededField] = total_home_away_conceded

    await calculate_stats_by_match_type(team_stats_dict,goals,conceded,match_type,homeOrAway)
    match_dict['v1_stats_completed'] = True
    await updateDocument('matches_store',match_dict['id'],match_dict)
    await updateDocument('teams_stats',team_id,team_stats_dict)
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