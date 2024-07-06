import json
from pydantic import TypeAdapter, ValidationError
from fcatimer import fcatimer
from etag_manager import getObject,updateDocument, whereEqual
from config import app_config
import id_generator
from datetime import datetime,timezone
from dateutil.parser import parse
import classes
import api_helper
import response_errors
from users_data import save_user,retrieve_user_id_by_email,update_user
from matches_data import retrieve_next_match_by_team
from auth import getToken
from secrets_util import lambda_handler
from notifications import save_token,sendNotificationUpdatesLink,sendNotification
import asyncio
from email_sender import send_email,send_email_with_template

async def new_user(event, context):
    await lambda_handler(event,context)
    try:
        body =json.loads(event["body"])
        print(body)
        email = getToken(event)["email"]
        await saveDeviceToken(event)
        fs_user = await getObject(email,'users_store')
        if(fs_user):
            fs_user.update({'name':body['name']})
            template_id="d-f25c6f27e6d14af58f8a3457ecfebee2"
            await send_email_with_template(email,template_id,{})
        else:
            await updateDocument('users_store',email,{'email':email,'name':body['name']})
        
        response = api_helper.make_api_response(200,{"id":id})
    except ValidationError as e:
        errors = response_errors.validationErrorsList(e)
        response = api_helper.make_api_response(400,None,errors)
    except ValueError as e:
        response = api_helper.make_api_response(400,None,e)

    print(response)
    return response
def sort_by_date(item):
    return item["date"]

@fcatimer
async def sendInvites(event,context):
    await lambda_handler(event,context)
    match_id = event["pathParameters"]["match_id"]
    
    fs_match = await getObject(match_id,"matches_store")
    if(fs_match):
        fs_match_dict = fs_match.get().to_dict()
        opposition = fs_match_dict['opposition']
        date = fs_match_dict['date']

        print
        format_string = "%Y-%m-%d"  # Year-Month-Day format

        try:
            formatted_date = parse(date)
            date_string = formatted_date.strftime("%B %d, %Y")
            print(date_string)
            print(formatted_date)  # Output: July 02, 2024 (formatted differently)
        except ValueError:
            print("Invalid date format!")
        
        fs_invites = fs_match_dict['invites']   
        players = []
        if(fs_invites):
            for fs_player in fs_invites:
                fs_invited = fs_player['inviteResponse']
                fs_history = fs_player.get('inviteHistory',[])
                print(f"INVITE HISTORY {fs_history}")
                if(fs_invited=='invited'):
                    
                    send_invite = True
                    if len(fs_history)>0:
                        fs_history_sorted = sorted(fs_history, key=sort_by_date, reverse=True)
                        print(f"INVITE HISTORY SORTED {fs_history_sorted}")
                        fs_history_response = fs_history_sorted[0]
                        fs_history_response_answer = fs_history_response.get('response',"")
                        if fs_history_response_answer==fs_invited:
                            send_invite = False
                    if send_invite: 
                        fs_guardians = fs_player['guardians']
                        for fs_guardian in fs_guardians:
                            notification_id = id_generator.generate_random_number(10)
                            print(f"GUARDIAN {fs_guardian}")
                            fs_devices = await whereEqual('devices','email',fs_guardian)
                            print(f"DEVICES {fs_devices}")
                            message=f"{fs_player['info']['forename']} has been invited to play against {opposition} on {date_string}"
                            if(fs_devices):
                                
                                for fs_device in fs_devices:
                                    fs_device_dict = fs_device.to_dict()
                                    metadata={"player_id":fs_player["info"]["id"],"match_id":match_id,"team_id":fs_match_dict["team_id"],"email":fs_guardian,'notification_id':notification_id}
                                    await sendNotification(type="invitation",token=fs_device_dict["token"],message=message,silent=False,subject="New invitation",id=match_id,metadata=metadata)
                            notification = {
                                'message':message,
                                'metadata':metadata,
                                'email':fs_guardian,
                                'type':'invitation',
                                'subject':f"{fs_match_dict['opposition']} invite",
                                'sent':datetime.now(timezone.utc)
                            }
                            await updateDocument('user_notifications',str(notification_id),notification)
                fs_history.append({'response':fs_invited,'date':datetime.now(timezone.utc)})
                print(f"INVITE HISTORY 2{fs_history}")
                fs_player['inviteHistory'] = fs_history
                print(f"INVITE PLAYER {fs_player}")
                players.append(fs_player)
                print(f"INVITE PLAYERs {players}")
            fs_invites.update({'players':players})

@fcatimer
async def sendResponse(event,context):
    await lambda_handler(event,context)
    player_id = event["pathParameters"]["player_id"]
    match_id = event["pathParameters"]["match_id"]
    
    fs_match = await getObject(match_id,'matches_store')
     
    emails = []
    if(fs_match):
        fs_match_dict = fs_match.get().to_dict()
        date = fs_match_dict['date']

        print
        format_string = "%Y-%m-%d"  # Year-Month-Day format

        try:
            formatted_date = parse(date)
            date_string = formatted_date.strftime("%B %d, %Y")
            print(date_string)
            print(formatted_date)  # Output: July 02, 2024 (formatted differently)
        except ValueError:
            print("Invalid date format!")
        fs_invites = fs_match_dict['invites'] 
        team_id = fs_match_dict['team_id']
        fs_team = await getObject(team_id,'teams_store')
        if(fs_team):
            fs_team_dict = fs_team.get().to_dict()
            fs_admins = fs_team_dict['admins']
            for fs_admin in fs_admins:
                emails.append(fs_admin['email'])
            fs_coaches = fs_team_dict['coaches']
            for fs_coach in fs_coaches:
                emails.append(fs_coach['email'])

        if(fs_invites):
        
            
            for player_dict in fs_invites:
                
                if player_dict['info']['id'] == player_id:
                    response = player_dict['inviteResponse']
                    message = ''
                    if response=='accepted':
                        message = f"{player_dict['info']['forename']} {player_dict['info']['surname']} can make the game against {fs_match_dict['opposition']} on {date_string}"
                    elif response=='decline':
                        message = f"{player_dict['info']['forename']} {player_dict['info']['surname']} can't make the game against {fs_match_dict['opposition']} on {date_string}"
                    for email in emails:
                        notification_id = id_generator.generate_random_number(10)
                        fs_devices = await whereEqual('devices','email',email)
                        print(f"DEVICES {fs_devices}")
                        if(fs_devices):
                            for fs_device in fs_devices:
                                fs_device_dict = fs_device.to_dict()
                                metadata={"player_id":player_id,"match_id":match_id,"team_id":team_id,"email":email,'notification_id':notification_id}
                                await sendNotification(type="response",token=fs_device_dict["token"],message=message,silent=False,subject="Match response",id=match_id,metadata=metadata)
                        notification = {
                            'message':message,
                            'metadata':metadata,
                            'email':email,
                            'type':'response',
                            'subject':f"{fs_match_dict['opposition']} response",
                            'sent':datetime.now(timezone.utc)
                        }
                        await updateDocument('user_notifications',str(notification_id),notification)
        

async def saveDeviceToken(event):
    headers = event["headers"]
    device_token = event["headers"]['x-device-token']
    device_id = event["headers"]['x-device-id']
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