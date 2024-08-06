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

from auth import check_permissions
from roles import Role

from team_backend import getTeamFromDB


import id_generator
from cache_trigger import updateUserCache
import json
import team_backend

from classes import User,Team,TeamUser, GroupTeam

from config import app_config
import exceptions
from users_data import retrieve_user_id_by_email,update_user
from team_data import save_team
from secrets_util import getEmailFromToken, lambda_handler
import api_helper

from auth import set_custom_claims
import notifications


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
        await notifications.sendNotificationUpdatesLink(getEmailFromToken(event,context),f"Welcome your new coaches",f"New coach added to {results['team_name']}",'team',data)
        response = api_helper.make_api_response(200,results['results'])
    else:
            response = api_helper.make_api_response(403,None,"You do not have permission to edit this match")
    return response




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
        await notifications.sendNotificationUpdatesLink(email,message,subject,'team',data)
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