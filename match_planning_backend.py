import sys
import match_day_data
from match_day_data import retrieveLastPlanned,retrieve_periods_by_match,retrieveNextPlanned,retrieveAllPlannedLineups,retrieveCurrentActual,retrieveStartingLineup,save_goals_for,save_assists_for,save_opposition_goal,retrieveNextPlannedByMinute
from player_data import retrieve_players_by_team, retrieve_player
import api_helper
import matches_data
from matches_data import retrieve_match_by_id
from typing import Dict, List
import matches_state_machine
import logging
import time
import datetime
import asyncio
logger = logging.getLogger(__name__)
import functools
import player_responses
from datetime import date, timedelta
from pydantic import ValidationError
from matches_data import retrieve_match_by_id,retrieve_matches_by_team,save_team_fixture
import response_errors
import team_data
import notifications
import multiprocessing
import boto3

import exceptions
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def timeit(func):
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
import response_classes

baseUrl = "/teams/%s/matches/%s"

async def getMatchParent(team_id,match_id):
    try:
        matchList = await retrieve_match_by_id(match_id)
        print(f"############################MATCH LIST##################################")
        print(matchList)
        match = matchList[0]
        
        print(f"MATCH STATUS {match.status}")
        if(match.status==matches_state_machine.MatchState.created):
            response = await getMatchCreated(team_id,match)
        elif(match.status==matches_state_machine.MatchState.plan or (match.status==matches_state_machine.MatchState.plan_confirmed and match.date!=date.today())):
            response = await getMatchPlanning(team_id,match)
        elif(match.status==matches_state_machine.MatchState.plan_confirmed and match.date==date.today()):
            response = await getMatchConfirmedPlanReadyToStart(team_id,match)
        elif(match.status==matches_state_machine.MatchState.started or match.status==matches_state_machine.MatchState.ended or match.status==matches_state_machine.MatchState.paused or match.status==matches_state_machine.MatchState.restarted or matches_state_machine.MatchState.starting_lineup_confirmed):
            response =  await getMatchStarted(team_id,match)
        logging.info(response)
        return response
       
    except exceptions.AuthError as e:
        print(e)
        response = api_helper.make_api_response(401,None,e)
        return response
    except ValidationError as e:
        print(e)
        response = api_helper.make_api_response(400,None,e)
        return response
    except Exception as e:
        print(e)
        response = api_helper.make_api_response(500,None,e)
        return response  

@timeit
async def getMatchCreatedResponse(team_id,match:response_classes.MatchInfo):
    playersList = await retrieve_players_by_team(team_id)  
    url = response_classes.getMatchUrl(team_id,match.id)
    submit_first_subs = response_classes.Link(link=f'{url}/players/submit_lineup',method="post")
    confirm_plan = response_classes.Link(link=f'{url}/{matches_state_machine.MatchState.plan.value}',method="post")

    links = {"submit_plan":submit_first_subs,"confirm_plan":confirm_plan }
    match_day_response = response_classes.PlannedMatchResponse(match=match,planned_lineups=playersList,links=createMatchLinks(url,links)).model_dump()
   

    return match_day_response

@timeit
async def getMatchCreated(team_id,match:response_classes.MatchInfo):
    match_day_responses = []
    match_day_responses.append(await getMatchCreatedResponse(team_id,match))
    response = api_helper.make_api_response(200,match_day_responses)
    logging.info(response)
    return response


async def getMatchConfirmedPlanReadyToStart(team_id,match:response_classes.MatchInfo):
    match_day_responses = []
    match_day_responses.append(await getMatch(team_id,match))

    response = api_helper.make_api_response(200,match_day_responses)
    
    return response

async def getMatchPlanningResponse(team_id,match):
    selected_players = await retrieveAllPlannedLineups(match_id=match.id)
    captains = await retrieve_player(match.captain)
    captain = None
    if(len(captains)>0):
        captain = captains[0]
    print(selected_players)
    url = response_classes.getMatchUrl(team_id,match.id)
    submit_first_subs = response_classes.Link(link=f'{url}/players/submit_lineup',method="post")
    confirm_plan = response_classes.Link(link=f'{url}/{matches_state_machine.MatchState.plan_confirmed.value}',method="post")
    links = {"submit_plan":submit_first_subs,"confirm_plan":confirm_plan }
    match_day_response = response_classes.PlannedMatchResponse(match=match,captain=captain, planned_lineups=selected_players,links=createMatchLinks(url,links)).model_dump()
    
    return match_day_response

async def getMatchPlanning(team_id,match):
    match_day_responses = []
    match_day_responses.append(await getMatchPlanningResponse(team_id,match))
    

    response = api_helper.make_api_response(200,match_day_responses)
    logging.info(response)
    return response


@timeit
async def getMatchGuest(match:response_classes.MatchInfo)-> response_classes.ActualMatchResponse:
    time_playing = await how_long_played(match.id)
    how_long_left = 0
    if(match.status==matches_state_machine.MatchState.ended.value):
        how_long_left = 0
    else:
        how_long_left = match.length-time_playing
    print(f"HOW LONG LEFT {how_long_left}")
    
    next_lineup,current_lineup,goals,opposition,last_planned,all_actual_lineups,starting_lineup = await asyncio.gather(
        
        retrieveNextPlanned(match,time_playing),
        retrieveCurrentActual(match,time_playing),
        match_day_data.retrieve_player_goals(match),
        match_day_data.retrieve_opposition_goals(match),
        retrieveLastPlanned(match,time_playing),
        match_day_data.retrieveAllActualLineups(match,time_playing),
        retrieveStartingLineup(match_id=match.id),
    )
    if(len(next_lineup)>0):
        next_minute = next_lineup[0].selectionInfo.minuteOn
        refresh_at = int((next_minute-time_playing)/2)
        if(len(last_planned)>0):
            last_minute = last_planned[0].selectionInfo.minuteOn
            next_close = next_minute - time_playing
            last_close = time_playing - last_minute

            if(next_close<last_close):
                planned_subs = await getSubs(next_lineup,current_lineup)
            else:
                planned_subs = await getSubs(last_planned,current_lineup)
        else:
            planned_subs = await getSubs(next_lineup,current_lineup)
    else:
        refresh_at = int(how_long_left)
        planned_subs=[]

    if(len(current_lineup)==0):
        current_lineup = starting_lineup
    
    subs = []
    i=1
    for list in all_actual_lineups:
        if(i<len(all_actual_lineups)):
            subs = subs + await getSubs(list,all_actual_lineups[i])
            i=i+1
    
    report = []

    report = report+subs
    print(f"Report = {report}")
    print(f"Subs = {subs}")
    report = report+goals
    print(f"Report = {report}")
    print(f"Goals = {goals}")
    report = report+opposition
    print(f"Report = {report}")
    print(f"Opposition = {opposition}")
    report.sort(key=lambda x:x.minute)
    
    print(f"NEXT LINEUP {next_lineup}")
    print(f"LAST LINEUP {last_planned}")
    print(f"CURRENT LINEUP {current_lineup}")
    print(f"GOALS {goals}")


    url = response_classes.getMatchUrl(match.team.id,match.id)
    
    start_match = response_classes.Link(link=f'{url}/start',method="post")
    submit_first_subs = response_classes.Link(link=f'{url}/players/submit_lineup/subs',method="post")
    submit_plan = response_classes.Link(link=f'{url}/players/submit_lineup',method="post")
    
    confirm_plan = response_classes.Link(link=f'{url}/{matches_state_machine.MatchState.plan_confirmed.value}',method="post")
    end_match = response_classes.Link(link=f'{url}/{matches_state_machine.MatchState.ended.value}',method="post")
    links = {"start_match":start_match,"submit_subs":submit_first_subs,"submit_plan":submit_plan,"confirm_plan":confirm_plan,"end_match":end_match }
    match_day_response = response_classes.ActualMatchResponse(match=match,planned_subs=planned_subs,last_planned=last_planned,started_at=0, how_long_left=how_long_left, current_players=current_lineup,next_players=next_lineup,links=createMatchLinks(url,links),scorers=goals,opposition=opposition,actual_subs=subs,refresh_at=refresh_at,report=report).model_dump()
    
    return match_day_response

async def getSubs(current_lineup, next_lineup):
    if not current_lineup or not next_lineup:
        return []

    plannedSubsOn = [player for player in current_lineup if player not in next_lineup and player.selectionInfo.position]
    

    plannedSubsOff = [player for player in next_lineup if player not in current_lineup and player.selectionInfo.position]

    plannedSubsOn.sort(key=lambda x: x.selectionInfo.position)
    plannedSubsOff.sort(key=lambda x: x.selectionInfo.position)
    # Ensure that lengths are the same, or handle cases where they're not
    min_length = min(len(plannedSubsOff), len(plannedSubsOn))

    subs = []
    for i in range(min_length):
        print(plannedSubsOff[i])
        print(plannedSubsOn[i])
        #to maintain backwards compatibility i am adding a primary player
        stat = response_classes.PlayerMatchStat(player=plannedSubsOff[i].info, player_off=plannedSubsOff[i],player_on=plannedSubsOn[i],time=int(plannedSubsOn[i].selectionInfo.minuteOn),minute=int(plannedSubsOn[i].selectionInfo.minuteOn),type="Sub")
        subs.append(stat)

    return subs

@timeit
async def getMatch(team_id,match:response_classes.MatchInfo):

    time_playing = await how_long_played(match.id)
    how_long_left = 0
    if(match.status==matches_state_machine.MatchState.ended.value):
        how_long_left = 0
    else:
        how_long_left = match.length-time_playing
    print(f"HOW LONG LEFT {how_long_left}")
    
    next_lineup,current_lineup,goals,opposition,last_planned,all_actual_lineups,starting_lineup,captain = await asyncio.gather(
        
        retrieveNextPlanned(match,time_playing),
        retrieveCurrentActual(match,time_playing),
        match_day_data.retrieve_player_goals(match),
        match_day_data.retrieve_opposition_goals(match),
        retrieveLastPlanned(match,time_playing),
        match_day_data.retrieveAllActualLineups(match,time_playing),
        retrieveStartingLineup(match_id=match.id),
        retrieve_player(match.captain)
    )
    if(len(next_lineup)>0):
        next_minute = next_lineup[0].selectionInfo.minuteOn
        refresh_at = int((next_minute-time_playing)/2)
        if(len(last_planned)>0):
            last_minute = last_planned[0].selectionInfo.minuteOn
            next_close = next_minute - time_playing
            last_close = time_playing - last_minute

            if(next_close<last_close):
                planned_subs = await getSubs(next_lineup,current_lineup)
            else:
                planned_subs = await getSubs(last_planned,current_lineup)
        else:
            planned_subs = await getSubs(next_lineup,current_lineup)
    else:
        refresh_at = int(how_long_left)
        planned_subs=[]

    if(len(current_lineup)==0):
        current_lineup = starting_lineup
    
    subs = []
    i=1
    for list in all_actual_lineups:
        if(i<len(all_actual_lineups)):
            subs = subs + await getSubs(list,all_actual_lineups[i])
            i=i+1
    
    report = []

    report = report+subs
    print(f"Report = {report}")
    print(f"Subs = {subs}")
    report = report+goals
    print(f"Report = {report}")
    print(f"Goals = {goals}")
    report = report+opposition
    print(f"Report = {report}")
    print(f"Opposition = {opposition}")
    report.sort(key=lambda x:x.minute)
    
    print(f"NEXT LINEUP {next_lineup}")
    print(f"LAST LINEUP {last_planned}")
    print(f"CURRENT LINEUP {current_lineup}")
    print(f"GOALS {goals}")


    url = response_classes.getMatchUrl(team_id,match.id)
    
    start_match = response_classes.Link(link=f'{url}/start',method="post")
    submit_first_subs = response_classes.Link(link=f'{url}/players/submit_lineup/subs',method="post")
    submit_plan = response_classes.Link(link=f'{url}/players/submit_lineup',method="post")
    captain_player = None
    if(len(captain)>0):
        captain_player = captain[0]
    confirm_plan = response_classes.Link(link=f'{url}/{matches_state_machine.MatchState.plan_confirmed.value}',method="post")
    end_match = response_classes.Link(link=f'{url}/{matches_state_machine.MatchState.ended.value}',method="post")
    links = {"start_match":start_match,"submit_subs":submit_first_subs,"submit_plan":submit_plan,"confirm_plan":confirm_plan,"end_match":end_match }
    match_day_response = response_classes.ActualMatchResponse(match=match,planned_subs=planned_subs,last_planned=last_planned,started_at=0, how_long_left=how_long_left, current_players=current_lineup,next_players=next_lineup,links=createMatchLinks(url,links),scorers=goals,opposition=opposition,actual_subs=subs,refresh_at=refresh_at,report=report,captain=captain_player).model_dump()
    
    return match_day_response

@timeit
async def getMatchStarted(team_id,match):
    match_day_responses = []
    match_day_responses.append(await getMatch(team_id,match))

    response = api_helper.make_api_response(200,match_day_responses)
    
    return response


async def how_long_played(match_id):
    periods = await retrieve_periods_by_match(match_id)
    time_playing = 0
    last_period = {}
    isStarted = False
    started_at = 0
    ended = False
    for period in periods:
        if(period.status=="ended"):
            ended = True
        if(period.status == "paused"):
            print(f"TIME PLAYING PAUSE {time_playing}")
            last_period = period
        if(period.status=="started"):
            isStarted = True
            started_at = period.time
            last_period = period
        if(period.status=="restarted"):
            time_playing = time_playing + (period.time - last_period.time)
            last_period = period
    
    if(isStarted):
        if(len(periods)>0 and last_period.status=="paused"):
            current_pause = datetime.datetime.utcnow().timestamp()-last_period.time
            time_playing = time_playing+current_pause
            
        print("################### TIME PLAYING 1#######################")
        print(time_playing)
        how_long_ago_started = (datetime.datetime.utcnow().timestamp()-started_at)
        print("HOW LONG AGO STARTED")
        print(how_long_ago_started)
        time_playing = (datetime.datetime.utcnow().timestamp()-time_playing-started_at)
        print("################### TIME PLAYING 2#######################")
        print(time_playing/60)
        return time_playing/60
    else:
        return 0
 
async def getStakeholders(match_id):
    matches = await matches_data.retrieve_match_by_id(match_id)

    match = matches[0]
    print(f"MATCH {match}")
    team_id = match.team.id
    print(f"TEAM ID {team_id}")
    admins = await team_data.retrieve_users_by_team_id(team_id)
    return admins

async def sendMessagesOnMatchUpdates(token,message,title,match_id,team_id):
    await notifications.send_push_notification(token, title, message,"view_match",f"/matches/{match_id}")
    logger.debug(f"Message sent to device {token}")

async def setGoalsFor(team_id,match_id, goal_scorer,assister,type):
    time_playing = await how_long_played(match_id)
    
    print(assister)
    if(assister):
        await save_assists_for(match_id,assister["info"]["id"],time_playing)
    await save_goals_for(match_id,goal_scorer["info"]["id"],time_playing,type,assister["info"]["id"])
    await matches_data.increment_goals_scored(match_id=match_id,goals=1)
    scored_by = f"Assisted by {assister['info']['name']} - {type}"
    users = await getStakeholders(match_id)
    for user in users:
        tokens = await notifications.getDeviceToken(user.email)
        for token in tokens:
            new_token = token["Token"]
            asyncio.create_task(sendMessagesOnMatchUpdates(new_token, scored_by, f"{int(time_playing)}' {goal_scorer['info']['name']} scores",match_id,team_id))
    tokens = await notifications.getDeviceTokenByMatchOnly(match_id)

    for token in tokens:
        new_token = token["Token"]
        asyncio.create_task(sendMessagesOnMatchUpdates(new_token, scored_by, f"{int(time_playing)}' {goal_scorer['info']['name']} scores",match_id,team_id))

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
            asyncio.create_task(sendMessagesOnMatchUpdates(new_token, message, "Status updated",match_id,match.team.id))
    tokens = await notifications.getDeviceTokenByMatchOnly(match_id)

    for token in tokens:
        new_token = token["Token"]
        asyncio.create_task(sendMessagesOnMatchUpdates(new_token, "" ,message,match_id,match.team.id))


async def subs_due(match_id):
    matches = retrieve_match_by_id(match_id)
    match = matches[0]
    
    for user in await getStakeholders(match_id):
        tokens = await notifications.getDeviceToken(user)
        for token in tokens:
            new_token = token["Token"]
            asyncio.create_task(sendMessagesOnMatchUpdates(new_token,"", f"Subs due for {match.name} vs {match.opposition}",match_id,match.team.id))

    tokens = await notifications.getDeviceTokenByMatchOnly(match_id)

    for token in tokens:
        new_token = token["Token"]
        asyncio.create_task(sendMessagesOnMatchUpdates(new_token,"", f"Subs due for {match.name} vs {match.opposition}",match_id,match.team.id))




async def setGoalsAgainst(match_id,team_id, opposition):
    time_playing = await how_long_played(match_id)
    await save_opposition_goal(match_id,time_playing)
    await matches_data.increment_goals_conceded(match_id=match_id,goals=1)
    scored_by = f"{int(time_playing)}' Goal scored by {opposition}"
    users = await getStakeholders(match_id)
    for user in users:
        tokens = await notifications.getDeviceToken(user.email)
        for token in tokens:
            new_token = token["Token"]
            asyncio.create_task(sendMessagesOnMatchUpdates(new_token, scored_by, scored_by,match_id,team_id))
    tokens = await notifications.getDeviceTokenByMatchOnly(match_id)

    for token in tokens:
        new_token = token["Token"]
        asyncio.create_task(sendMessagesOnMatchUpdates(new_token, scored_by, scored_by,match_id,team_id))

async def updateMatchPeriod(match_id,status):
    periods = await retrieve_periods_by_match(match_id)
    if(len(periods)>0):
        if(periods[-1].status!=status):
            await match_day_data.update_period(match_id,status)
    else:
        await match_day_data.update_period(match_id,status)
    await sendStatusUpdate(match_id,status)


async def sendStatusUpdate(match_id,status):
    matches = await retrieve_match_by_id(match_id)
    match = matches[0]
    if(status==matches_state_machine.MatchState.plan_confirmed.value):
        message = f"{match.team.name} vs {match.opposition} match day plans confirmed"
    elif(status==matches_state_machine.MatchState.started.value):
        message = f"{match.team.name} vs {match.opposition} has started"
    elif(status==matches_state_machine.MatchState.paused.value):
        message = f"{match.team.name} vs {match.opposition} has paused"
    elif(status==matches_state_machine.MatchState.restarted.value):
        message = f"{match.team.name} vs {match.opposition} has restarted"
    elif(status==matches_state_machine.MatchState.restarted.value):
        message = f"{match.team.name} vs {match.opposition} has restarted"
    elif(status==matches_state_machine.MatchState.substitutions.value):
        message = f"{match.team.name} vs {match.opposition} - substitutions"
    else:
        message = f"{match.team.name} vs {match.opposition} status update"
    for user in await getStakeholders(match_id):
        tokens = await notifications.getDeviceToken(user.email)

        for token in tokens:
            new_token = token["Token"]
            asyncio.create_task(sendMessagesOnMatchUpdates(new_token, "" ,message,match_id,match.team.id))
    
    tokens = await notifications.getDeviceTokenByMatchOnly(match_id)

    for token in tokens:
        new_token = token["Token"]
        asyncio.create_task(sendMessagesOnMatchUpdates(new_token, "" ,message,match_id,match.team.id))

async def submit_planned_lineup(match_id,players:List[player_responses.PlayerResponse],minute,team_id):
   
    committed = await match_day_data.save_planned_lineup(match_id=match_id,minute=minute,players=players)
    # if(committed):
    #     for user in await getStakeholders(match_id):
    #         tokens = await notifications.getDeviceToken(user.email)

    #         for token in tokens:
    #             new_token = token["Token"]
    #             asyncio.create_task(sendMessagesOnMatchUpdates(new_token, "", "Match plan updated",match_id,team_id))
    
           
      
async def start_match(match_id):
    await updateMatchPeriod(match_id,matches_state_machine.MatchState.started.value)
    await matches_data.update_match_status(match_id=match_id,status=matches_state_machine.MatchState(matches_state_machine.MatchState.started.value))

async def submit_actual_lineup(match_id,players:List[player_responses.PlayerResponse]):
    await match_day_data.save_actual_lineup(match_id=match_id,players=players,time_playing=0)
    await matches_data.update_match_status(match_id=match_id,status=matches_state_machine.MatchState(matches_state_machine.MatchState.starting_lineup_confirmed.value))

async def submit_subs(match,players:List[player_responses.PlayerResponse]):
    time_playing = await how_long_played(match.id)
    
    print("************** SUBS ON HERE ***************")
    current_players = await match_day_data.retrieveCurrentActual(match=match,how_log_ago=time_playing)
    print(current_players)
    print(players)
    difference = set(players).difference(current_players)
    print("************** SUBS ON***************")
    print(difference)
    await match_day_data.save_subs(match_id=match.id,players=difference,time_playing=time_playing)
    await match_day_data.save_actual_lineup(match_id=match.id,players=players,time_playing=time_playing)
    await updateMatchPeriod(match.id,matches_state_machine.MatchState.substitutions.value)

def createMatchLinks(url, links:Dict[str,response_classes.Link]):
    self = response_classes.Link(link=url,method="get")
    print(links)
    links["self"] = self
    print(links)
    return links

async def create_match_backend(match,team_id) -> response_classes.MatchResponse:
    type = match.get("type",None)
    if(type):
        type = response_classes.MatchType(type)

    matchInfo = response_classes.MatchInfo(id="",opposition=match["opposition"],homeOrAway=match["homeOrAway"],date=match["date"],length=match["length"],status=matches_state_machine.MatchState.created,type=type)
        
    result = await retrieve_match_by_id(await save_team_fixture(matchInfo,team_id))
    print("########################################RESULT FROM RETRIEVE MATCH BY ID ")
    print(result)
    self_url = response_classes.getMatchUrl(team_id,result[0].id)
    self = response_classes.Link(link=self_url,method="get")
    links = {"self":self}
    match_response = response_classes.MatchResponse(match=result[0],links=links)
    message = f"{match_response.match.team.name} vs {match_response.match.opposition} created"
    subject = f"New match for {match_response.match.team.name}"
    
    for user in await getStakeholders(match_response.match.id):
        tokens = await notifications.getDeviceToken(user.email)
        for token in tokens:
            new_token = token["Token"]
            asyncio.create_task(sendMessagesOnMatchUpdates(new_token, message, subject,match_response.match.id,team_id))
    return match_response

async def list_matches_by_team_backend(team_id):
    matches = []
    for match in await retrieve_matches_by_team(team_id):
        try:
            if(match.status==matches_state_machine.MatchState.created):
                matches.append(await getMatchCreatedResponse(team_id,match))
            elif(match.status==matches_state_machine.MatchState.plan or (match.status==matches_state_machine.MatchState.plan_confirmed and match.date!=date.today())):
                matches.append(await getMatchPlanningResponse(team_id,match))
            else:
                matches.append(await getMatch(team_id,match))
            
        except ValidationError as e:
            print(e)
            errors = response_errors.validationErrorsList(e)
            print(errors)
            response = api_helper.make_api_response(400,None,errors)
            return response
        except ValueError as e:
            print(e)
            response = api_helper.make_api_response(400,None)
            return response
   
    return matches

async def main():
    if(sys.argv[1]=="getMatchParent"):
        
        await getMatchParent(sys.argv[2],sys.argv[3] )
    if(sys.argv[1]=="getMatchCreated"):
        matchList = await retrieve_match_by_id(sys.argv[3])
        print(matchList)
        match = matchList[0]
        await getMatchCreated(sys.argv[2],match )
    if(sys.argv[1]=="getMatchStarted"):
        matchList = await retrieve_match_by_id(sys.argv[3])
        print(matchList)
        match = matchList[0]
        await getMatchStarted(sys.argv[2],match)
    if(sys.argv[1]=="getMatchConfirmedPlan"):
        matchList = await retrieve_match_by_id(sys.argv[3])
        match = matchList[0]
        await getMatchConfirmedPlanReadyToStart(sys.argv[2],match)
    if(sys.argv[1]=="getMatchGuest"):
        matchList = await retrieve_match_by_id(sys.argv[3])
        print(matchList)
        match = matchList[0]
        await getMatchGuest(sys.argv[2],match)

if __name__ == "__main__":
    asyncio.run(main())

