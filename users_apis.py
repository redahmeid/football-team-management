import json


from fcatimer import fcatimer
from etag_manager import getObject,updateDocument, whereEqual,whereContains, whereNested,whereEqualwhere
from config import app_config
import id_generator
from datetime import datetime,timezone,timedelta
from dateutil.parser import parse,isoparse
import boto3
import classes
import api_helper
import response_errors
from users_data import save_user,retrieve_user_id_by_email,update_user
from matches_data import retrieve_next_match_by_team
from auth import getToken, getEmailFromToken
from secrets_util import lambda_handler, initialise_firebase
from notifications import save_token,sendNotificationUpdatesLink,sendNotification
import asyncio
from email_sender import send_email,send_email_with_template
import firebase_admin
from firebase_admin import credentials, firestore

async def new_user(event, context):
    await lambda_handler(event,context)
    try:
        body =json.loads(event["body"])
        print(body)
        email = getToken(event)["email"]
        await saveDeviceToken(event)
        fs_user = await getObject(email,'users_store')
        template_data = {'name':body['name']}
        
        
        if(fs_user):
            fs_user.update({'name':body['name']})
            template_id="d-f25c6f27e6d14af58f8a3457ecfebee2"
            await send_email_with_template(email,template_id,template_data)
        else:
            # fs_user = await getObject(str(str(email).lower.__hash__),'users_store')
            # if(not fs_user):

            template_id="d-f25c6f27e6d14af58f8a3457ecfebee2"
            await send_email_with_template(email,template_id,template_data)
        await updateDocument('users_store',email,{'email':email,'name':body['name']})
        
        response = api_helper.make_api_response(200,{"id":id})
    
    except ValueError as e:
        response = api_helper.make_api_response(400,None,e)

    print(response)
    return response



def sort_by_date(item):
    return item["date"]



@fcatimer
async def sendNotificationUpdatesLink(match_id,message,subject,type,data):
    secretsmanager = boto3.client('secretsmanager')
    event = {
        "type":type,
        "id":match_id,
        "message":message,
        "subject":subject,
        "data":data
    }
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
    FunctionName=app_config.send_notifications,  # Name of the target Lambda
    InvocationType='Event',
    Payload=json.dumps(event)  # Asynchronous invocation
    ) 

#Schedule every 5 minutes check
@fcatimer
async def findAndSendInvites(event,context):
    await initialise_firebase()
    reminder = 7
   
    
    where_stats = firestore.FieldFilter('date', '<' , datetime.now(timezone.utc)+ timedelta(days=reminder))
    where_today = firestore.FieldFilter('date', '>' , datetime.now(timezone.utc))
    where_not_invited = firestore.FieldFilter('invited', '==' , False)
    fs_matches = await whereEqualwhere('matches_store',wheres=[where_not_invited,where_stats,where_today])
    print(len(fs_matches))
    for fs_match in fs_matches:
        secretsmanager = boto3.client('secretsmanager')
        fs_match_dict = fs_match.to_dict()
        if(fs_match_dict.get('whenInvite',-1)>-1):
            event = {"id":fs_match_dict['id']}
            lambda_client = boto3.client('lambda')
            lambda_client.invoke(
            FunctionName=app_config.schedule_invitations,  # Name of the target Lambda
            InvocationType='Event',
            Payload=json.dumps(event)  # Asynchronous invocation
            ) 
        
# Each match invite
@fcatimer
async def backgroundSendInvites(event,context):
    await initialise_firebase()

    id = event["id"]
    fs_match = await getObject(id,'matches_store')
    if(fs_match):
        fs_match_dict = fs_match.get().to_dict()

        if(fs_match_dict.get('whenInvite',0)!=0 and not fs_match_dict.get('invited',False) and fs_match_dict.get('status','')!='cancelled') :   
            fs_match_dict = await invites(id)
            print(f'FS MATCH DICT FROM BACKGROUND SEND INVITES {fs_match_dict}')
            await updateDocument('matches_store',str(id),fs_match_dict)





@fcatimer
async def invite_all_players(fs_players,date_string,opposition,match_id):
    invitees = []
    fs_match = await getObject(match_id,'matches_store')
    tokens={}
    type = 'invite'
    if(fs_match):
        fs_match_dict = fs_match.get().to_dict()
        print(f"invite_all_players-FS PLAYERS {fs_players}")
        if(fs_players):

            for fs_player in fs_players:
                id = id_generator.generate_random_number(10)
                fs_player_dict = fs_player.to_dict()
                archived = fs_player_dict.get('archived',False)
                print(f"invite_all_players-ARCHIVED {archived}")
                if(archived == False or archived == None):
                    fs_guardians = fs_player_dict['guardians']
                    for fs_guardian in fs_guardians:
                        notification_id = str(id_generator.generate_random_number(10))
                        print(f"GUARDIAN {fs_guardian}")
                        fs_devices = await whereEqual('devices','email',fs_guardian)
                        print(f"DEVICES {fs_devices}")
                        if(fs_match_dict['type']=='training'):
                            message=f"{fs_player_dict['info']['forename']} has been invited to training on {date_string}"
                            subject = "Training invite"
                        else:
                            message=f"{fs_player_dict['info']['forename']} has been invited to play against {opposition} on {date_string}"
                            subject = f"{fs_match_dict['opposition']} invite"
                        metadata={"invited_id":str(id),"player_id":fs_player_dict["info"]["id"],"match_id":match_id,"team_id":fs_match_dict["team_id"],"email":fs_guardian,'notification_id':notification_id}
                        if(fs_devices):
                            
                            for fs_device in fs_devices:
                                fs_device_dict = fs_device.to_dict()
                                silent = False
                                if(fs_device_dict['version']):
                                    silent = str((is_version_greater(fs_device_dict['version'],'android.3.0.34') or is_version_greater(fs_device_dict['version'],'ios.3.0.34')))
                                isNotifiable = fs_device_dict.get('notifications',True)

                                if(isNotifiable):
                                    token=fs_device_dict["token"]
                                    if(tokens.get(token,None) is None):
                                        tokens[token] =True
                                        await sendNotification(type=type,token=fs_device_dict["token"],message=message,silent=silent,subject="New invitation",id=match_id,metadata=metadata)
                        notification = {
                            'message':message,
                            'metadata':metadata,
                            'email':fs_guardian,
                            'type':type,
                            'subject':subject,
                            'sent':datetime.now(timezone.utc)
                        }
                        await updateDocument('user_notifications',str(notification_id),notification)
                        invitee = {}
                        
                    invitee['id']=str(id)
                    invitee['player']=fs_player_dict
                    invitee['status']='notified'
                        
                    invitees.append(invitee)
        
            fs_match_dict['invites'] = invitees
            fs_match_dict['invited'] = True
            await updateDocument('matches_store',str(match_id),fs_match_dict)


@fcatimer
async def invite_invitee_players(fs_invites,date_string,opposition,match_id,fs_match_dict):
    invitees = []
    tokens={}
    type = 'invite'
    if(fs_invites):
        for fs_player in fs_invites:
            fs_invited = fs_player['status']
            fs_history = fs_player.get('inviteHistory',[])
            print(f"INVITE HISTORY {fs_history}")
            if(fs_invited=='invited'):
                
                send_invite = True
               
                if send_invite: 
                    fs_guardians = fs_player['player']['guardians']
                    for fs_guardian in fs_guardians:
                        notification_id = id_generator.generate_random_number(10)
                        print(f"GUARDIAN {fs_guardian}")
                        fs_devices = await whereEqual('devices','email',fs_guardian)
                        print(f"DEVICES {fs_devices}")
                        if(fs_match_dict['type']=='training'):
                            message=f"{fs_player['player']['info']['forename']} has been invited to training on {date_string}"
                            subject = "Training invite"
                        else:
                            message=f"{fs_player['player']['info']['forename']} has been invited to play against {opposition} on {date_string}"
                            subject = f"{fs_match_dict['opposition']} invite"
                        metadata={"invited_id":fs_player['id'],"player_id":fs_player['player']["info"]["id"],"match_id":match_id,"team_id":fs_match_dict["team_id"],"email":fs_guardian,'notification_id':notification_id}
                        if(fs_devices):
                            
                            for fs_device in fs_devices:
                                fs_device_dict = fs_device.to_dict()
                                silent = False
                                if(fs_device_dict['version']):
                                    silent = str((is_version_greater(fs_device_dict['version'],'android.3.0.34') or is_version_greater(fs_device_dict['version'],'ios.3.0.34')))
                                isNotifiable = fs_device_dict.get('notifications',True)

                                if(isNotifiable):
                                        token=fs_device_dict["token"]
                                        if(tokens.get(token,None) is None):
                                            tokens[token] =True
                                            await sendNotification(type=type,token=fs_device_dict["token"],message=message,silent=silent,subject="New invitation",id=notification_id,metadata=metadata)
                        fs_player['status'] = 'notified'
                        
                        notification = {
                            'message':message,
                            'metadata':metadata,
                            'email':fs_guardian,
                            'type':type,
                            'subject':f"{fs_match_dict['opposition']} invite",
                            'sent':datetime.now(timezone.utc)
                        }
                        await updateDocument('user_notifications',str(notification_id),notification)
            invitees.append(fs_player)
        
            fs_match = await getObject(match_id,'matches_store')

            
            fs_match_dict = fs_match.get().to_dict()
            fs_match_dict['invited'] = True
            fs_match_dict['invites'] = invitees
            fs_match_dict['whenInvite'] = 0
    print(f'FS MATCH DICT FROM BACKGROUND SEND INVITES {fs_match_dict}')
    return fs_match_dict
    
                     

@fcatimer
async def invites(match_id):
    fs_match = await getObject(match_id,"matches_store")
    if(fs_match):
        fs_match_dict = fs_match.get().to_dict()
        print(f"MATCH {fs_match_dict}")
        opposition = fs_match_dict['opposition']
        date = fs_match_dict['date']
        when = fs_match_dict['whenInvite']
        

        print
        format_string = "%Y-%m-%d"  # Year-Month-Day format
        carry_on = True
        
        try:
            offset = timedelta(hours=0)
            try:
                formatted_date = parse(date)
                new_date = formatted_date.replace(tzinfo=timezone.utc)
            except:
                formatted_date = date
                new_date = date
            

            # Convert to offset-aware datetime
            if(int(when)>0):
                now = datetime.now(timezone.utc)
                difference = new_date - now
                print(f"DIFFERENCE {difference}")
                if(difference.days>int(when)):
                    carry_on = False
            date_string = formatted_date.strftime("%B %d, %Y")
            print(date_string)
            print(formatted_date)  # Output: July 02, 2024 (formatted differently)
        except ValueError:
            print("Invalid date format!")
        
        if(carry_on):
            fs_invite_group = fs_match_dict.get('invite_group',None)
            print(f'FS INVITE GROUP {fs_invite_group}')
            players = []
            if(fs_invite_group):
                if(fs_invite_group=='players'):
                    fs_invites = await whereNested('players_store','info.team_id',fs_match_dict['team_id'])
                    print(f'FS TEAM ID {fs_match_dict["team_id"]}')
                    print(f'FS PLAYERS {fs_invites}')
                    await invite_all_players(fs_players=fs_invites,date_string=date_string,opposition=opposition,match_id=match_id)
                elif(fs_invite_group=='guardians'):
                    fs_invites = await whereContains('users_store','guardians',fs_match_dict['team_id'])
            else:
                fs_invites = fs_match_dict['invites']
                fs_match_dict = await invite_invitee_players(fs_invites=fs_invites,date_string=date_string,opposition=opposition,match_id=match_id,fs_match_dict=fs_match_dict)
                print(f'FS MATCH DICT FROM INVITES {fs_match_dict}')
                return fs_match_dict


@fcatimer
async def notifyCancellation(match_id):
    fs_match = await getObject(match_id,"matches_store")
    if(fs_match):
        fs_match_dict = fs_match.get().to_dict()
        print(f"MATCH {fs_match_dict}")
        date_string = fs_match_dict['date']
        if(fs_match_dict['type']=='training'):
            message=f"Training on {date_string} has been cancelled"
            subject = "Training cancellation"
        else:
            message=f"Match against {fs_match_dict['opposition']} on {date_string} has been cancelled"
            subject = f"Match cancellation"
     
        await notifyInvitees(fs_match_dict=fs_match_dict,message=message,subject=subject,template_data={})

@fcatimer
async def notifyReminder(match_id):
    fs_match = await getObject(match_id,"matches_store")
    
    if(fs_match):
        fs_match_dict = fs_match.get().to_dict()
        fs_team = await getObject(fs_match_dict["team_id"],"teams_store")
        fs_team_dict = fs_team.get().to_dict()
        team_name = f"{fs_team_dict['name']} {fs_team_dict['age_group']}"
        print(f"MATCH {fs_match_dict}")
        date = fs_match_dict['date']
        
        try:
            formatted_date = parse(date)
            
        except:
            formatted_date = date
        
        date_string = formatted_date.strftime("%B %d, %Y")
        if(fs_match_dict['type']=='training'):
            message=f"Please respond to the training invite for {date_string}"
            subject = "Training response reminder"
            event_name = 'training'
        else:
            message=f"Please respond to the match invite against {fs_match_dict['opposition']} on {date_string}"
            subject = f"Match response reminder"
            event_name = f"a match vs {fs_match_dict['opposition']}"
        template_data = {
                        "event_name":event_name,
                        "date":date_string,
                        "team_name":team_name
                    }
        await notifyInvitees(fs_match_dict=fs_match_dict,message=message,subject=subject,template_data=template_data,if_unanswered=True,send_email=True)
        

    
@fcatimer
async def notifyInvitees(fs_match_dict,message,subject,template_data,if_unanswered=False,send_push=True,send_email=False):
    invitees = fs_match_dict.get('invites',[])
    tokens = {}

    if(invitees):
        for fs_player in invitees:
            carry_on = True
            if(if_unanswered):
                carry_on = False if (fs_player['response']) else True
            if(carry_on):
                fs_guardians = fs_player['player']['guardians']
                for fs_guardian in fs_guardians:
                    notification_id = id_generator.generate_random_number(10)
                    print(f"GUARDIAN {fs_guardian}")
                    fs_devices = await whereEqual('devices','email',fs_guardian)
                    print(f"DEVICES {fs_devices}")
                
                    metadata={"invited_id":fs_player['id'],"player_id":fs_player['player']["info"]["id"],"match_id":fs_match_dict['id'],"team_id":fs_match_dict["team_id"],"email":fs_guardian,'notification_id':notification_id}
                    if(send_push):
                        if(fs_devices):
                            
                            for fs_device in fs_devices:
                                fs_device_dict = fs_device.to_dict()
                                silent = False
                                if(fs_device_dict['version']):
                                    silent = str((is_version_greater(fs_device_dict['version'],'android.3.0.34') or is_version_greater(fs_device_dict['version'],'ios.3.0.34')))
                                isNotifiable = fs_device_dict.get('notifications',True)

                                if(isNotifiable):
                                    token=fs_device_dict["token"]
                                    if(tokens.get(token,None) is None):
                                        tokens[token] =True
                                        await sendNotification(type="match",token=token,message=message,silent=silent,subject=subject,id=fs_match_dict['id'],metadata=metadata)
                    
                    fs_player['status'] = 'notified'
                    
                    notification = {
                        'message':message,
                        'metadata':metadata,
                        'email':fs_guardian,
                        'type':'match',
                        'subject':subject,
                        'sent':datetime.now(timezone.utc)
                    }
                    await updateDocument('user_notifications',str(notification_id),notification)
                    
                    if(send_email):
                        await send_email_with_template(fs_guardian,"d-681a68cd271649e38403dbdb70a79c7f",template_data)

                    
                    
                    print(f'FS MATCH DICT FROM BACKGROUND SEND INVITES {fs_match_dict}')
 
@fcatimer
async def notify_match_update(event,context):
    await lambda_handler(event,context)
    match_id = event["pathParameters"]["match_id"]
    fs_match = await getObject(match_id,"matches_store")
    if(fs_match):
        fs_match_dict = fs_match.get().to_dict()
        try:
            formatted_date = parse(fs_match_dict['date'])
        except:
            formatted_date = fs_match_dict['date']
        date_string = formatted_date.strftime("%B %d, %Y")
        if(fs_match_dict['type']=='training'):
            message = f"Training on {date_string} has been updated"
            subject = f"Training Updated"
        else:
            message = f"Match vs {fs_match_dict['opposition']} on {date_string} has been updated"
            subject = f"Match vs {fs_match_dict['opposition']} Updated"
        await notifyInvitees(fs_match_dict,message,subject,True,False)

@fcatimer
async def sendReminder(event,context):
    await lambda_handler(event,context)
    match_id = event["pathParameters"]["match_id"]
    
    await notifyReminder(match_id)

@fcatimer
async def sendInvites(event,context):
    await lambda_handler(event,context)
    match_id = event["pathParameters"]["match_id"]
    fs_match = await getObject(match_id,"matches_store")
    if(fs_match):
        fs_match_dict = fs_match.get().to_dict()
        print(f"MATCH {fs_match_dict}")
        opposition = fs_match_dict['opposition']
        date = fs_match_dict['date']
        when = fs_match_dict['whenInvite']
        if(int(when)==0):
            fs_match_dict = await invites(match_id)
            
            await updateDocument('matches_store',str(match_id),fs_match_dict)

@fcatimer
async def send_cancellation_message(event,context):
    await lambda_handler(event,context)
    match_id = event["pathParameters"]["match_id"]
    fs_match = await getObject(match_id,"matches_store")
    if(fs_match):
        fs_match_dict = fs_match.get().to_dict()
        print(f"MATCH {fs_match_dict}")
        
        
        await notifyCancellation(match_id)
        


@fcatimer
async def updatePlans(event,context):
    await lambda_handler(event,context)
    player_id = event["pathParameters"]["player_id"]

    match_id = event["pathParameters"]["match_id"]
    fs_match = await getObject(match_id,'matches_store')
    tokens={}
    if(fs_match):
        fs_match_dict = fs_match.get().to_dict()
        emails = set()
        team_id = fs_match_dict['team_id']
        fs_team = await getObject(team_id,'teams_store')
        if(fs_team):
            fs_team_dict = fs_team.get().to_dict()
            fs_admins = fs_team_dict['admins']
            for fs_admin in fs_admins:
                emails.add(fs_admin['email'])
            fs_coaches = fs_team_dict['coaches']
            for fs_coach in fs_coaches:
                emails.add(fs_coach['email'])
        fs_invites = fs_match_dict['invites'] 
        send_notification = False
        if(fs_invites):
            for player_dict in fs_invites:
                if player_dict['player']['info']['id'] == player_id:
                    response = player_dict['response']
                    if(response=='declined'):
                        fs_planned_lineups = fs_match_dict['planned_lineups']
                        lineupIndex = 0
                        for lineup in fs_planned_lineups:
                            removeIndex = 0
                            fs_players = lineup['players']
                            for player in fs_players:
                                
                                if(player['info']['id']==player_id):
                                    del fs_players[removeIndex]
                                    send_notification = True
                                    message = f"{player['info']['forename']} has been removed from the match against {fs_match_dict['opposition']} as they can no longer attend. You may wish to replan."
                                    subject = f"Planned lineup change"
                                removeIndex = removeIndex+1
                            lineup['players'] = fs_players
                            fs_planned_lineups[lineupIndex]=lineup
                            lineupIndex = lineupIndex+1
                        fs_match_dict['planned_lineups'] = fs_planned_lineups
                        await updateDocument('matches_store',match_id,fs_match_dict)
                    if(response=='accepted'):
                        fs_planned_lineups = fs_match_dict['planned_lineups']
                        lineupIndex = 0
                        for lineup in fs_planned_lineups:
                            
                            fs_players = lineup['players']
                            found = False
                            for player in fs_players:
                                if(player['info']['id']==player_id):
                                    found = True
                                    print("PLAYER EXISTS")
                            if(not found):
                                stored_player = await getObject(player_id,'players_store')
                                player_dict = stored_player.get().to_dict()
                                fs_players.append(player_dict)
                                message = f"{player_dict['info']['forename']} has been put on the subs bench for the match against {fs_match_dict['opposition']} as they can attend now. You may wish to replan."
                                subject = f"Planned lineup change"
                                send_notification = True
                            lineup['players'] = fs_players
                            fs_planned_lineups[lineupIndex]=lineup
                            lineupIndex = lineupIndex+1
                        fs_match_dict['planned_lineups'] = fs_planned_lineups
                        await updateDocument('matches_store',match_id,fs_match_dict)
            if(send_notification):
                for email in emails:
                        notification_id = id_generator.generate_random_number(10)
                        fs_devices = await whereEqual('devices','email',email)
                        metadata={"player_id":player_id,"match_id":match_id,"team_id":team_id,"email":email,'notification_id':notification_id}
                        print(f"DEVICES {fs_devices}")
                        if(fs_devices):
                            for fs_device in fs_devices:
                                fs_device_dict = fs_device.to_dict()
                                silent = False
                                if(fs_device_dict['version']):
                                    silent = str((is_version_greater(fs_device_dict['version'],'android.3.0.34') or is_version_greater(fs_device_dict['version'],'ios.3.0.34')))
                                isNotifiable = fs_device_dict.get('notifications',True)

                                if(isNotifiable):
                                    token=fs_device_dict["token"]
                                    if(tokens.get(token,None) is None):
                                        tokens[token] =True
                                        await sendNotification(type="match",token=fs_device_dict["token"],message=message,silent=silent,subject="Match response",id=match_id,metadata=metadata)
                        notification = {
                            'message':message,
                            'metadata':metadata,
                            'email':email,
                            'type':'match',
                            'subject':subject,
                            'sent':datetime.now(timezone.utc)
                        }
                        await updateDocument('user_notifications',str(notification_id),notification)


@fcatimer
async def sendToTeamAdmins(team_id,message,subject,metadata,type):
    emails = set()
    fs_team = await getObject(team_id,'teams_store')
    if(fs_team):
        fs_team_dict = fs_team.get().to_dict()
        fs_admins = fs_team_dict['admins']
        for fs_admin in fs_admins:
            emails.add(fs_admin['email'])
        
        
        fs_coaches = fs_team_dict['coaches']
        
        for fs_coach in fs_coaches:
            emails.add(fs_coach['email'])
        await sendNotifications(emails,message,subject,metadata,type)

from packaging import version

def is_version_greater(current_version: str, base_version: str) -> bool:
    """
    Compare two version strings of the format android.X.Y.Z or ios.X.Y.Z.
    Returns True if current_version is greater than base_version.
    """
    # Extract the numeric part after the prefix
    current_numeric = current_version.split('.', 1)[-1]  # Split only at the first dot
    base_numeric = base_version.split('.', 1)[-1]
    
    # Use packaging.version for comparison
    return version.parse(current_numeric) > version.parse(base_numeric)
@fcatimer
async def sendNotifications(emails, message, subject,metadata,type,versions=[],send_os=""):
    for email in emails:
        notification_id = id_generator.generate_random_number(10)
        metadata['notification_id'] = notification_id
        fs_devices = await whereEqual('devices','email',email)
        tokens={}
        notification_sent = False
        if(fs_devices):
            for fs_device in fs_devices:
                fs_device_dict = fs_device.to_dict()
                print(f"DEVICES {fs_device_dict}")
                go = True
                go = fs_device_dict.get('version') is not None and send_os in fs_device_dict['version']

                
                if(versions):
                    for version in versions:
                        if(fs_device_dict['version']==version):
                            go = False
                
                if(go):
                    silent = False
                    if(fs_device_dict.get('notifications',True)):
                        silent = str((is_version_greater(fs_device_dict['version'],'android.3.0.34') or is_version_greater(fs_device_dict['version'],'ios.3.0.34')))
                        notification_sent = True
                        token=fs_device_dict["token"]
                        if(tokens.get(token,None) is None):
                            tokens[token] =True
                            await sendNotification(type=type,token=fs_device_dict["token"],message=message,silent=silent,subject=subject,id=notification_id,metadata=metadata)
      
            notification = {
                'message':message,
                'metadata':metadata,
                'email':email,
                'type':type,
                'subject':subject,
                'sent':datetime.now(timezone.utc)
            }
            await updateDocument('user_notifications',str(notification_id),notification)
            

@fcatimer
async def sendInviteResponse(event,context):
    await lambda_handler(event,context)
    player_id = event["pathParameters"]["player_id"]
    match_id = event["pathParameters"]["match_id"]
    
    fs_match = await getObject(match_id,'matches_store')
    tokens={}
 
    sent_by = getEmailFromToken(event,context)

    sent_by_user = await getObject(sent_by,'users_store')
    if(sent_by_user):
        sent_by_user_dict = sent_by_user.get().to_dict()
        sent_by_name = sent_by_user_dict.get('name',sent_by)
        if(sent_by_name==''):
            sent_by_name = sent_by
    fs_player_match_invite_history = await getObject(f"{match_id}+{player_id}",'player_match_invite_history')

    emails = set()
    if(fs_match):
        fs_match_dict = fs_match.get().to_dict()
        date = fs_match_dict['date']
        
        print
        format_string = "%Y-%m-%d"  # Year-Month-Day format

        try:
            formatted_date = parse(date)
            
            print(formatted_date)  # Output: July 02, 2024 (formatted differently)
        except:
            formatted_date = date
            print("Invalid date format!")
        date_string = formatted_date.strftime("%B %d, %Y")
        print(date_string)
        fs_invites = fs_match_dict['invites'] 
        team_id = fs_match_dict['team_id']
        fs_team = await getObject(team_id,'teams_store')
        if(fs_team):
            fs_team_dict = fs_team.get().to_dict()
            fs_admins = fs_team_dict['admins']
            for fs_admin in fs_admins:
                emails.add(fs_admin['email'])
            
            
            fs_coaches = fs_team_dict['coaches']
            for fs_coach in fs_coaches:
                user_coach = await getObject(fs_coach['email'],'users_store')
                if(user_coach):
                    user_coach_dict = user_coach.get().to_dict()
                    notifications_config = user_coach_dict.get('notifications',{})
                    send_response = notifications_config.get('invite_response',False)
                emails.add(fs_coach['email'])

        if(fs_invites):
            for player_dict in fs_invites:
                
                if player_dict['player']['info']['id'] == player_id:
                    
                    response = player_dict['response']
                    fs_guardians = player_dict['player']['guardians']
                    for guardian in fs_guardians:
                        if(guardian!=sent_by):
                            emails.add(guardian)
                    last_response = ""
                    if(fs_player_match_invite_history):
                        fs_player_match_invite_history_dict = fs_player_match_invite_history.get().to_dict()
                        last_response = fs_player_match_invite_history_dict.get("response","")
                    if(response != last_response):
                        await updateDocument("player_match_invite_history",f"{match_id}+{player_id}",{"response":response})
                        message = ''
                        if response=='accepted':
                            if(fs_match_dict['type']=='training'):
                                message = f"{player_dict['player']['info']['forename']} {player_dict['player']['info']['surname']} can make training on {date_string} - from {sent_by_name}"
                                subject = f"{player_dict['player']['info']['forename']} Training response"
                            else:
                                message = f"{player_dict['player']['info']['forename']} {player_dict['player']['info']['surname']} can make the game against {fs_match_dict['opposition']} on {date_string} - from {sent_by_name}"
                                subject = f"{player_dict['player']['info']['forename']} Match response"
                            
                        elif response=='declined':
                            if(fs_match_dict['type']=='training'):
                                message = f"{player_dict['player']['info']['forename']} {player_dict['player']['info']['surname']} can't make training on {date_string} - from {sent_by_name}"
                                subject = f"{player_dict['player']['info']['forename']} Training response"
                            else:
                                message = f"{player_dict['player']['info']['forename']} {player_dict['player']['info']['surname']} can't make the game against {fs_match_dict['opposition']} on {date_string} - from {sent_by_name}"
                                subject = f"{player_dict['player']['info']['forename']} Match response"
                            
                        for email in emails:
                            notification_id = id_generator.generate_random_number(10)
                            fs_devices = await whereEqual('devices','email',email)
                            metadata={"player_id":player_id,"match_id":match_id,"team_id":team_id,"email":email,'notification_id':notification_id}
                            print(f"DEVICES {fs_devices}")
                            if(fs_devices):
                                for fs_device in fs_devices:
                                    fs_device_dict = fs_device.to_dict()
                                    silent = False
                                    if(fs_device_dict['version']):
                                        silent = str((is_version_greater(fs_device_dict['version'],'android.3.0.34') or is_version_greater(fs_device_dict['version'],'ios.3.0.34')))
                                    isNotifiable = fs_device_dict.get('notifications',True)

                                    if(isNotifiable):
                                        token=fs_device_dict["token"]
                                        if(tokens.get(token,None) is None):
                                            tokens[token] =True
                                            await sendNotification(type="match",token=fs_device_dict["token"],message=message,silent=silent,subject="Match response",id=match_id,metadata=metadata)
                            notification = {
                                'message':message,
                                'metadata':metadata,
                                'email':email,
                                'type':'match',
                                'subject':subject,
                                'sent':datetime.now(timezone.utc)
                            }
                            await updateDocument('user_notifications',str(notification_id),notification)
        await updatePlans(event,context)

async def saveDeviceToken(event):
    headers = event["headers"]
    try:
        device_token = event["headers"]['x-device-token']
    except:
        device_token = getToken(event)["uid"]
    try:
        device_id = event["headers"]['x-device-id']
    except:
        device_id = str(id_generator.generate_random_number(12))
    email = getToken(event)["email"]
    version = headers.get('x-football-app',None)
    await save_token(email=email,token=device_token,device=device_id,version=version)


# "(ID varchar(255),"\
# #         "Name varchar(255) NOT NULL,"\
# #         "AgeGroup varchar(255) NOT NULL,"\
# #         "Email varchar(255) NOT NULL,"\
# #         "Club_ID varchar(255) NOT NULL,"\
# #         "live VARCHAR(255),"\
# def convertTeamDataToTeamResponse(team) -> response_classes.TeamResponse:
#     print("convertTeamDataToTeamResponse: %s"%(team))
#     id = team["ID"]
#     baseTeamUrl = "/teams/%s"%(id)
#     name = team["Name"]
#     ageGroup = team["AgeGroup"]
#     email = team["Email"]
#     clubId = team["Club_ID"]
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

#     response =  response_classes.TeamResponse(id=id,email=email,name=name,ageGroup=ageGroup,clubId=clubId,live=live,self=self,nextMatch=nextMatch,teamPlayers=players,teamFixtures=fixtures,addFixtures=addFixtures,addPlayers=addPlayers)
#     print("Convert team %s"%(response))
#     return response.model_dump()