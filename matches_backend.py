import json
import pydantic
import sys
from config import app_config
import team_data
import notifications
from matches_data import retrieve_match_by_id
import boto3
import response_classes
import matches_data
import matches_state_machine
import match_planning_backend

import asyncio
import json
import match_day_data
from etag_manager import setEtag,isEtaggged,getLatestObject,deleteEtag,setEtagList
from timeit import timeit

@timeit
async def getMatchCurrentLineups(match_id):
    
    actual_lineups = await getLatestObject(match_id,"actual_lineups")
   
    if(actual_lineups):
        lineups = json.loads(actual_lineups)
        current_lineup = lineups[len(lineups)-1]
    else:
        planned_lineups = await getLatestObject(match_id,"planned_lineups")   
        
        if(planned_lineups):
            lineups = json.loads(planned_lineups["object"])
            current_lineup = lineups[0]
        else:
            current_lineup = {}
    
    current_lineup = [current_lineup]
    etag =  await setEtag(match_id,"current_lineup",current_lineup)
    
   

    return {"etag":etag,"object":current_lineup}
   

@timeit
async def getPlannedLineup(match_id):
    matchList = await retrieve_match_by_id(match_id)
    print(f"############################MATCH LIST##################################")
    print(matchList)
    match = matchList[0]

    if(match.status==matches_state_machine.MatchState.created):
        url = f"/teams/{match.team.id}/players"
        link = response_classes.Link(link=url,method="get")
        return {"planned_lineup":link}
    

async def getStakeholders(match_id):
    matches = await matches_data.retrieve_match_by_id(match_id)

    match = matches[0]
    print(f"MATCH {match}")
    team_id = match.team.id
    print(f"TEAM ID {team_id}")
    admins = await team_data.retrieve_users_by_team_id(team_id)
    return admins

@timeit
async def updateStatus(match_id,status):
    matches = await matches_data.update_match_status(match_id,status)
    match = matches[0]
            
    if(status==matches_state_machine.MatchState.plan_confirmed):
        message = f"{match.team.name} vs {match.opposition} match day plans confirmed"
    if(status==matches_state_machine.MatchState.started):
        message = f"{match.team.name} vs {match.opposition} has started"
    if(status==matches_state_machine.MatchState.paused):
        message = f"{match.team.name} vs {match.opposition} has paused"
    if(status==matches_state_machine.MatchState.ended):
        message = f"{match.team.name} vs {match.opposition} has ended"
    for user in await getStakeholders(match_id):
        tokens = await notifications.getDeviceToken(user.email)

        for token in tokens:
            new_token = token["Token"]
            asyncio.create_task(sendMessagesOnMatchUpdates(new_token, "", message,match_id))
    tokens = await notifications.getDeviceTokenByMatchOnly(match_id)

    for token in tokens:
        new_token = token["Token"]
        asyncio.create_task(sendMessagesOnMatchUpdates(new_token, "" ,message,match_id))

@timeit
async def sendMessagesOnMatchUpdates(token,message,title,match_id):
    data = {
        "link":f"/matches/{match_id}"
    }
    await notifications.send_push_notification(token, title, message,data)



    



@timeit
async def getMatchFromDB(match_id) :
    
    matches = []
    match_response = await getLatestObject(match_id,"matches")
    if(match_response):
        object = json.loads(match_response["object"])

    else:
        match = await matches_data.retrieve_match_by_id(match_id)
        object = await match_planning_backend.getMatchParent(match[0].team.id,match[0])

    actual_match = response_classes.ActualMatchResponse(**object)
    print(actual_match)
    etag = await setEtag(match_id,'matches',actual_match.model_dump())
    return {"etag":etag,"result":actual_match.model_dump()}

@timeit
async def getMatchFromDBRefresh(match_id,refresh) :
    
    matches = []
    match_response = await getLatestObject(match_id,"matches")
    if(match_response):
        object = json.loads(match_response["object"])

    else:
        match = await matches_data.retrieve_match_by_id(match_id)
        object = await match_planning_backend.getMatchParent(match[0].team.id,match[0])

    actual_match = response_classes.ActualMatchResponse(**object)
    print(actual_match)
    if(refresh is not None):
        refreshes = refresh.split(',')
        if("time_played" in refreshes):
            time_played = await match_planning_backend.how_long_played(match_id)
            actual_match.how_long_left=actual_match.match.length - time_played
        if("changes_due" in refreshes):
            changes_due = await match_planning_backend.getChangesDue(actual_match.match)
            actual_match.planned_subs=changes_due["planned_subs"]
            actual_match.planned_position_changes=changes_due["planned_position_changes"]
            actual_match.refresh_at=changes_due["refresh_at"]
    
    etag = await setEtag(match_id,'matches',actual_match.model_dump())
    return {"etag":etag,"result":actual_match.model_dump()}



@timeit
async def getPlannedLineupsFromDB(match_id):
    object = await match_day_data.retrieveAllPlannedLineups(match_id)
    etag = await setEtagList(match_id,'planned_lineups',object)
    print(object)
    print(json.dumps(object, default=lambda o: o.dict()))
    
    return {"etag":etag,"result":json.dumps(object, default=lambda o: o.dict())}


async def main():
    if(sys.argv[1]=="getPlanned"):
        
        await getPlannedLineupsFromDB(sys.argv[2] )
    

if __name__ == "__main__":
    asyncio.run(main())



