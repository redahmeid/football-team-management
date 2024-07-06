import json
import pydantic
import classes
import datetime
from match_day_data import save_goals_for
import sys
import traceback
from config import app_config
import id_generator
import team_data
import notifications
from matches_data import retrieve_match_by_id
import boto3
import response_classes
import matches_data
import matches_state_machine
import match_planning_backend
from etag_manager import getObject, updateDocument
import asyncio
import json
import match_day_data
from etag_manager import setEtag,isEtaggged,getLatestObject,deleteEtag,setEtagList,getAllObjects,updateDocument
from fcatimer import fcatimer

@fcatimer
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
   

@fcatimer
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

async def updateInvites(match_id, players):
    await updateDocument('invites',str(match_id),{"players":players})
    

@fcatimer
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

@fcatimer
async def sendMessagesOnMatchUpdates(token,message,title,match_id):
    data = {
        "link":f"/matches/{match_id}"
    }
    await notifications.send_push_notification(token, title, message,data)


async def create_match_backend(match,team_id) -> response_classes.PlannedMatchResponse:
    type = match.get("type",None)
    if(type):
        type = response_classes.MatchType(type)
    id = id_generator.generate_random_number(7)
    matchInfo = classes.MatchInfo(id=str(id),length=match["length"],opposition=match["opposition"],homeOrAway=match["homeOrAway"],location=match["location"],placeId=match["placeId"],date=match["date"],time=match["time"],status=matches_state_machine.MatchState.created,status_history=[{'status':matches_state_machine.MatchState.created,'time':datetime.datetime.now(datetime.timezone.utc)}],type=type,team_id=team_id)
    
    await updateDocument('matches_store',str(id),matchInfo.dict())
    fs_team = await getObject(team_id,'teams_store')
    print(fs_team)
    empty_list = []
    fs_team_dict = fs_team.get().to_dict()
    fs_fixtures = fs_team_dict.get('fixtures',[])
      # Set an empty list as the default
    fs_fixtures.append(id)
    fs_team.update({'fixtures':fs_fixtures})

    message = f"{fs_team_dict['name']} vs {matchInfo.opposition} scheduled"
    subject = f"New match for {fs_team_dict['name']}"
    data = {
        "link":f'/matches/{id}',
        "match_id":id,
        "action":"new_match",
        "silent": 'False'
    }
    await notifications.sendNotificationUpdatesLink(id,message,subject,'match',data)
    return matchInfo



@fcatimer
async def getMatchFromDB(match_id) :
    
    
    match = await matches_data.retrieve_match_by_id(match_id)

    return match.model_dump()

# @fcatimer
# async def getMatchFromDBRefresh(match_id,refresh) :
    
#     matches = []
#     match_response = await getLatestObject(match_id,"matches")
#     if(match_response):
#         object = json.loads(match_response["object"])

#     else:
#         match = await matches_data.retrieve_match_by_id(match_id)
#         object = await match_planning_backend.getMatchParent(match[0].team.id,match[0])

#     actual_match = response_classes.ActualMatchResponse(**object)
#     print(actual_match)
#     if(refresh is not None):
#         refreshes = refresh.split(',')
#         if("time_played" in refreshes):
#             time_played = await match_planning_backend.how_long_played(match_id)
#             actual_match.how_long_left=actual_match.match.length - time_played
#         if("changes_due" in refreshes):
#             changes_due = await match_planning_backend.getChangesDue(actual_match.match)
#             actual_match.planned_subs=changes_due["planned_subs"]
#             actual_match.planned_position_changes=changes_due["planned_position_changes"]
#             actual_match.refresh_at=changes_due["refresh_at"]
#     await updateDocument('matches_store',actual_match.match.id,actual_match.match)
#     etag = await setEtag(match_id,'matches',actual_match.model_dump())
#     return {"etag":etag,"result":actual_match.model_dump()}


@fcatimer
async def updateScore(match_id,goals_for,goals_against):
    try:
        await matches_data.updateScore(match_id,goals_for,goals_against)
        
        
    except:
        traceback.print_exception(*sys.exc_info()) 

@fcatimer
async def addPlayerRatings(match_id,players):
    try:
        await matches_data.create_player_ratings(match_id,players)
        
    except:
        traceback.print_exception(*sys.exc_info()) 


# @fcatimer
# async def updateDBFromCache():
#     objs = await getAllObjects('matches')
#     for obj in objs:
#         response = json.loads(obj["object"])
#         actual_match = response_classes.ActualMatchResponse(**response)
#         if(actual_match.match.status=='created'):
#             await matches_data.save_team_fixture(actual_match.match,actual_match.match.team.id)

@fcatimer
async def getPlannedLineupsFromDB(match_id):
    object = await match_day_data.retrieveAllPlannedLineups(match_id)
    etag = await setEtagList(match_id,'planned_lineups',object)
    print(object)
    print(json.dumps(object, default=lambda o: o.dict()))
    

    
    
    return {"etag":etag,"result":json.dumps(object, default=lambda o: o.dict())}


@fcatimer
async def addAGoalScorer(team_id,match_id, goal_scorer,assister,type,assist_type,minutes):
    
    scored_by =""
    print(assister)
    fs_match = await getObject(match_id,'matches_store')
    if(assister is not None):
        
        scored_by = f"Assisted by {assister['info']['name']} - {type}"
        if(fs_match):
            fs_match_dict = fs_match.get().to_dict()
            scorers = fs_match_dict.get('scorers',[])
            scorers.append({"scorer":goal_scorer['info']['id'],"assister":assister['info']['id'],"goal_type":type,"assist_type":assist_type,"minute":minutes})
    else:   
        
        if(fs_match):
            fs_match_dict = fs_match.get().to_dict()
            fs_match_dict = fs_match.get().to_dict()
            scorers = fs_match_dict.get('scorers',[])
            scorers.append({"scorer":goal_scorer['info']['id'],"goal_type":type,"minute":minutes})
   
    
    
    if(fs_match):
        fs_match.update({"scorers":scorers})

    fs_player = await getObject(goal_scorer,'player_stats')
    if fs_player:
        fs_player_dict = fs_player.get().to_dict()
        current_list = fs_player_dict.get('actual_matches', {})
        fs_match = current_list.get(match_id,{match_id:{}})
        fs_subs = fs_match.get("goals",[])
        fs_subs.append({"goal_type":type,"minute":minutes})
        fs_match["goals"] = fs_subs
        current_list[match_id] = fs_match
        fs_player.update(current_list)
    
    fs_assister = await getObject(assister,'player_stats')
    if fs_assister:
        fs_assister_dict = fs_assister.get().to_dict()
        current_list = fs_assister_dict.get('actual_matches', {})
        fs_match = current_list.get(match_id,{match_id:{}})
        fs_subs = fs_match.get("assists",[])
        fs_subs.append({"assist_type":assist_type,"minute":minutes})
        fs_match["assists"] = fs_subs
        current_list[match_id] = fs_match
        fs_assister.update(current_list)
    


    message = f"{round(minutes)}' {goal_scorer['info']['name']} scores"
    # await updateMatchCache(match_id)
    # await updateTeamCache(team_id)
    # await updatePlayerCache(team_id)
    data = {
        "link":f"/matches/{match_id}",
        "match_id":match_id,
        "action":"goals_for"
    }
    await notifications.sendNotificationUpdatesLink(match_id,scored_by,message,'match',data)
    

# if __name__ == "__main__":
#     asyncio.run(updateDBFromCache())



