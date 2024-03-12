import json
from pydantic import TypeAdapter, ValidationError
from exceptions import AuthError

import response_classes
import api_helper
import response_errors
from team_data import save_team,retrieve_team_by_id
from secrets_util import getEmailFromToken, lambda_handler
from auth import set_custom_claims
from player_data import retrieve_players_by_team
from auth import check_permissions
from roles import Role
import team_season_data
from team_backend import retrieveTeamResponse,getTeamFromDB
import team_season_data
from team_backend import addSingleUser
import id_generator
from cache_trigger import updateUserCache
from etag_manager import isEtaggged,deleteEtag,setEtag
import json
import team_backend
import functools
import time
import asyncio
from classes import User,Team,TeamUser
import response_classes
from config import app_config
import exceptions
from users_data import retrieve_user_id_by_email
from team_data import save_team,retrieve_team_by_id
from secrets_util import getEmailFromToken, lambda_handler
import api_helper
from roles_data import save_role
import roles
from auth import set_custom_claims
import team_season_data
import notifications
import cache_trigger

import user_homepage_backend
from timeit import timeit

async def addUserToTeam(event,context):
    lambda_handler(event,context)
    acceptable_roles = [Role.admin.value,Role.coach.value]
    team_id = event["pathParameters"]["team_id"]
    body =json.loads(event["body"])
    emails = body["emails"]
    if(await check_permissions(event=event,team_id=team_id,acceptable_roles=acceptable_roles)):
        results = []
        for email in emails:
            result = await addSingleUser(email,team_id)
            results.append(result.model_dump())
        team = await team_backend.getTeamFromDB(team_id)
        await cache_trigger.updateTeamCache(team_id)
        data = {
            "link":f"/teams/{team_id}",
            "team_id":f"{team_id}",
            "action":"new_users",
            "silent":"False"
        }
        await notifications.sendNotificationUpdatesLink(getEmailFromToken(event,context),f"Welcome your new coaches",f"New coach added to {team.name}",'team',data)
        response = api_helper.make_api_response(200,results)
    else:
            response = api_helper.make_api_response(403,None,"You do not have permission to edit this match")
    return response




@timeit
async def submit_team(event, context):
    lambda_handler(event,context)
    body =json.loads(event["body"])
    teams = []
    try:
        email = getEmailFromToken(event,context)
       
        
        team = Team(age_group=body["age_group"],name=body["name"])
        id = id_generator.generate_random_number(7)
        team_id = id_generator.generate_random_number(7)
        # data, count = supabase.table('teams').insert({"id": id, "name": body["name"],"age_group":body["age_group"],"season":body["season"],"team_id":team_id}).execute()
        save_response = await save_team(team,team_id)
        
        
        team_season_id = await team_season_data.save_team_season(team_id,body["season"],body["age_group"])
        teamUser = TeamUser(email=email,team_id=str(team_season_id),role=roles.Role.admin)
        role_id = await save_role(teamUser)
        await set_custom_claims(event=event,context=context)
        # get the user
        save_response = await retrieve_team_by_id(team_season_id)
        teams.append(save_response.model_dump())
        await cache_trigger.updateUserCache(email)
        message = f"{team.name} has been created"
        subject = 'New team added'
        data = {
            "link":f"/teams/{save_response.id}",
            "team_id":f"{save_response.id}",
            "action":"new_team",
            "silent":"True"
        }
        await notifications.sendNotificationUpdatesLink(email,message,subject,'team',data)
        
        response = api_helper.make_api_response(200,teams)
    except exceptions.AuthError as e:
        print(e)
        response = api_helper.make_api_response(401,None,e)
    except Exception as e:
        print(e)
        response = api_helper.make_api_response(400,None,e)
    return response

@timeit
async def retrieve_team_summary(event, context):
    lambda_handler(event,context)
    
    team_id = event["pathParameters"]["team_id"]
    headers = event['headers']
    etag = headers.get('etag',None)
    print(f"USER HEADERS {headers}")
    
    teams = []

    try:
        if(etag):
            print("ETAG EXISTS")
            isEtag = await isEtaggged(team_id,'teams',etag)
            if(isEtag):
                return api_helper.make_api_response_etag(304,result={},etag=etag)
                
                
            else:
                response = await getTeamFromDB(team_id)
                
        else:
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
        
@timeit
async def delete_team(event, context):
    lambda_handler(event,context)
    
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




@timeit
def convertTeamDataToTeamResponse(team) -> response_classes.TeamResponse:
    print("convertTeamDataToTeamResponse: %s"%(team))
    id = team["ts.ID"]
    baseTeamUrl = "/teams/%s"%(id)
    name = team["Name"]
    ageGroup = team["Age_Group"]
    live = team["live"]
    print("Convert team live %s"%(live))
    if(live == None):
        live = True
    self = response_classes.Link(link=baseTeamUrl,method="get")
    players = response_classes.Link(link="%s/players"%(baseTeamUrl),method="get")
    fixtures= response_classes.Link(link="%s/matches"%(baseTeamUrl),method="get")
    addPlayers = response_classes.Link(link="%s/players"%(baseTeamUrl),method="post")
    addFixtures = response_classes.Link(link="%s/matches"%(baseTeamUrl),method="post")
    nextMatch = response_classes.Link(link="%s/next_match"%(baseTeamUrl),method="get")

    response =  response_classes.TeamResponse(id=id,name=name,ageGroup=ageGroup,live=live,self=self,nextMatch=nextMatch,teamPlayers=players,teamFixtures=fixtures,addFixtures=addFixtures,addPlayers=addPlayers)
    print("Convert team %s"%(response))
    return response