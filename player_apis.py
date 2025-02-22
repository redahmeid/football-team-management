import json
from secrets_util import lambda_handler, getEmailFromToken
import classes
from exceptions import AuthError
from config import app_config
from datetime import datetime,timezone
import api_helper
import id_generator
import response_errors
import response_classes
import team_data
import team_backend
from player_data import save_player,retrieve_players_by_team_with_stats,delete_player,retrieve_player,squad_size_by_team
from roles_data import retrieve_role_by_user_id_and_team_id
from users_data import retrieve_user_id_by_email
from etag_manager import deleteEtag
from roles import Role
from auth import check_permissions
from firebase_admin import credentials
from firebase_admin import messaging
import notifications
import player_backend
from etag_manager import getObject,updateDocument
from etag_manager import isEtaggged,deleteEtag,setEtag,whereEqual
import functools
import time
import asyncio
import hashlib
import json
from notifications import sendNotification
import firebase_admin
from firebase_admin import credentials, firestore
from fcatimer import fcatimer
from email_sender import send_email_with_template
import cache_trigger
from secrets_util import is_version_greater






@fcatimer    
async def create_players(event, context):
    await lambda_handler(event,context)
    body =json.loads(event["body"])
    headers = event["headers"]
    team_id = event["pathParameters"]["team_id"]
    version = headers.get("x-football-app","os.0.0.0")


    players = body["players"]
    created_players = []
    print("VERSION")
    print(version)
    i = 0

    
    for player in players:
        name = player["forename"]
        surname = player["surname"]
        emails = player['guardians']
        result = await player_backend.create_players_and_guardians(name,surname,team_id,emails)
        created_players.append(result)
  
        print(f"RESULT {result}")
        send_email = await getObject('send_email','feature_flags')
        enabled = True
        if(send_email):
            send_email_dict = send_email.get().to_dict()
            enabled = send_email_dict['enabled']
        if(enabled):
            for email in emails:
                await sendGuardianEmail(result['info']["id"],email)
        
       
    response = api_helper.make_api_response(200,created_players)
    return response


@fcatimer
async def sendGuardianEmail(player_id,email):
    fs_player = await getObject(player_id,'players_store')
    tokens={}
    if(fs_player):
        fs_player_dict = fs_player.get().to_dict()
        fs_team = await getObject(fs_player_dict['info']['team_id'],'teams_store')
        if(fs_team):
            fs_team_dict = fs_team.get().to_dict()
            

            template_data = {'player':fs_player_dict['info']['forename'],'team':fs_team_dict['name']}
            fs_user = await getObject(email,'users_store')
            if(fs_user):
                fs_user_dict = fs_user.get().to_dict()
                
                if(fs_user_dict.get('last_seen',None)):
                    await send_email_with_template(email,'d-d84865ab98a44c9aa6770e86364df6e5',template_data)
                else:
                    await send_email_with_template(email,'d-0904ad249669492fb6999ff0102742f1',template_data)
                message = f"You have been added as a guardian to {fs_player_dict['info']['forename']}"
                notification_id = id_generator.generate_random_number(10)
               
                fs_devices = await whereEqual('devices','email',email)
                metadata={"player_id":fs_player_dict["info"]["id"],'notification_id':notification_id}
                if(fs_devices):
                    
                    for fs_device in fs_devices:
                        fs_device_dict = fs_device.to_dict()
                        silent = False
                        if(fs_device_dict['version']):
                            silent = str((is_version_greater(fs_device_dict['version'],'android.3.0.34') or is_version_greater(fs_device_dict['version'],'ios.3.0.34')))
                        isNotifiable = fs_device_dict.get('notifications',True)

                        if(isNotifiable):
                            token=fs_device_dict["token"]
                            
                            if(not tokens[token]):
                                tokens[token] =True
                                await sendNotification(type="invitation",token=fs_device_dict["token"],message=message,silent=silent,subject="You've been added as a guardian",id=fs_player_dict["info"]["id"],metadata=metadata)
                notification = {
                                'message':message,
                                'metadata':metadata,
                                'email':email,
                                'type':'guardian_add',
                                'subject':f"You've been added to {fs_player_dict['info']['forename']}",
                                'sent':datetime.now(timezone.utc)
                            }
                await updateDocument('user_notifications',str(notification_id),notification)



@fcatimer
async def sendPlayerEmail(player_id,email):
    fs_player = await getObject(player_id,'players_store')
    tokens={}
    if(fs_player):
        fs_player_dict = fs_player.get().to_dict()
        fs_team = await getObject(fs_player_dict['info']['team_id'],'teams_store')
        if(fs_team):
            fs_team_dict = fs_team.get().to_dict()
            

            template_data = {'player':fs_player_dict['info']['forename'],'team':fs_team_dict['name']}
            fs_user = await getObject(email,'users_store')
            if(fs_user):
                fs_user_dict = fs_user.get().to_dict()
                
                if(fs_user_dict.get('last_seen',None)):
                    await send_email_with_template(email,'d-d84865ab98a44c9aa6770e86364df6e5',template_data)
                else:
                    await send_email_with_template(email,'d-0904ad249669492fb6999ff0102742f1',template_data)
                message = f"You have been given access to your details on TeamMate"
                notification_id = id_generator.generate_random_number(10)
               
                fs_devices = await whereEqual('devices','email',email)
                metadata={"player_id":fs_player_dict["info"]["id"],'notification_id':notification_id}
                if(fs_devices):
                    
                    for fs_device in fs_devices:
                        fs_device_dict = fs_device.to_dict()
                        silent = False
                        if(fs_device_dict['version']):
                            silent = str((is_version_greater(fs_device_dict['version'],'android.3.0.34') or is_version_greater(fs_device_dict['version'],'ios.3.0.34')))
                        isNotifiable = fs_device_dict.get('notifications',True)

                        if(isNotifiable):
                            token=fs_device_dict["token"]
                            
                            if(not tokens[token]):
                                tokens[token] =True
                                await sendNotification(type="invitation",token=fs_device_dict["token"],message=message,silent=silent,subject="You've been added as a guardian",id=fs_player_dict["info"]["id"],metadata=metadata)
                notification = {
                                'message':message,
                                'metadata':metadata,
                                'email':email,
                                'type':'guardian_add',
                                'subject':f"You've been added to {fs_player_dict['info']['forename']}",
                                'sent':datetime.now(timezone.utc)
                            }
                await updateDocument('user_notifications',str(notification_id),notification)

@fcatimer
async def sendNewGuardianAnEmail(event,context):
    await lambda_handler(event,context)
    player_id = event["pathParameters"]["player_id"]
    body =json.loads(event["body"])
    
    email = body["email"]
    await sendGuardianEmail(player_id,email)

@fcatimer
async def sendNewPlayerEmail(event,context):
    await lambda_handler(event,context)
    player_id = event["pathParameters"]["player_id"]
    body =json.loads(event["body"])
    
    email = body["email"]
    await sendPlayerEmail(player_id,email)

@fcatimer
async def addGuardiansToPlayer(event,context):
    await lambda_handler(event,context)
    acceptable_roles = [Role.admin.value,Role.coach.value]
    team_id = event["pathParameters"]["team_id"]
    player_id = event["pathParameters"]["player_id"]
    body =json.loads(event["body"])
    
    emails = body["emails"]

    if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
        results = []
        for email in emails:
           
            result = await player_backend.addGuardian(email,player_id,team_id)
            await cache_trigger.updateGuardiansPlayerCache(email)
            await cache_trigger.updateUserCache(email)
            results.append(result.model_dump())
        await cache_trigger.updateTeamCache(team_id)
        await cache_trigger.updatePlayerCache(team_id)
        
        data = {
            "link":f"/teams/{team_id}",
            "team_id":f"{team_id}",
            "action":"new_guardian",
            "silent":"False"
        }

        team = await team_data.retrieve_team_by_id(team_id)
        await notifications.sendNotificationUpdatesLink(getEmailFromToken(event,context),f"Guardian has been added to ",f"New coach added to {team.name}",'team',data)
        response = api_helper.make_api_response(200,results)
    else:
            response = api_helper.make_api_response(403,None,"You do not have permission to edit this match")
    return response

@fcatimer
async def list_players_by_team(event, context):
    await lambda_handler(event,context)
    acceptable_roles = [Role.admin.value,Role.coach.value,Role.parent.value]
    team_id = event["pathParameters"]["team_id"]
    if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
        players = []
        try:
            headers = event['headers']
            etag = headers.get('etag',None)
            if(etag):
                print("ETAG EXISTS")
                isEtag = await isEtaggged(team_id,'players',etag)
                if(isEtag):
                    response = api_helper.make_api_response_etag(304,result={},etag=etag)
                    return response 
                else:
                    return await player_backend.getPlayersByTeam(team_id)
            else:
                return await player_backend.getPlayersByTeam(team_id)
        except ValidationError as e:
            errors = response_errors.validationErrorsList(e)
            response = api_helper.make_api_response(400,None,errors)
        except ValueError as e:
            response = api_helper.make_api_response(400,None,None)
    else:
        response = api_helper.make_api_response(403,None,"You do not have permission to view the players")
        return response


@fcatimer
async def list_players_by_guardian(event, context):
    await lambda_handler(event,context)
    acceptable_roles = [Role.admin.value,Role.coach.value,Role.parent.value]
    
    
    players = []
    
    try:
        email = getEmailFromToken(event,context)
        headers = event['headers']
        etag = headers.get('etag',None)
        if(etag):
            print("ETAG EXISTS")
            isEtag = await isEtaggged(email,'guardian_players',etag)
            if(isEtag):
                response = api_helper.make_api_response_etag(304,result={},etag=etag)
                return response 
            else:
                players = await player_backend.getGuardianPlayersFromDB(email)
                response = api_helper.make_api_response_etag(200,players["result"],players["etag"])
                return response
        else:
            players = await player_backend.getGuardianPlayersFromDB(email)
            response = api_helper.make_api_response_etag(200,players["result"],players["etag"])
            return response
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        response = api_helper.make_api_response(400,None,errors)
    except ValueError as e:
        response = api_helper.make_api_response(400,None,None)
    except AuthError as e:
        response = api_helper.make_api_response(403,None,None)
   
    

def delete_player_from_team(event, context):
   
    
    player_id = event["pathParameters"]["player_id"]
    
    players = []
    

    try:
        delete_player(player_id)
        save_response = {"message":"Player %s has been deleted"%(player_id)}
        save_response["link"] = "/players/%s"%(player_id)
        players.append(save_response)
        actions = list()
            
        
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        response = api_helper.make_api_response(400,None,None,errors)
    except ValueError as e:
        response = api_helper.make_api_response(400,None,None,None)

    
    response = api_helper.make_api_response(200,players,actions)
    return response

# ID varchar(255),"\
        # "Name varchar(255) NOT NULL,"\
        # "Team_ID varchar(255) NOT NULL,"\
        # "Email varchar(255),"\
        # "live varchar(255),"\


