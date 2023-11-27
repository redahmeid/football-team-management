import sys
import match_day_data
from match_day_data import retrieve_periods_by_match,retrieveNextPlanned,retrieveAllPlannedLineups,retrieveCurrentActual,retrieveStartingLineup,save_goals_for,save_assists_for,save_opposition_goal,retrieveNextPlannedByMinute
from player_data import retrieve_players_by_team
import api_helper
import matches_data
from matches_data import retrieve_match_by_id
from typing import Dict
import matches_state_machine
import logging
import time
import datetime
import asyncio
logger = logging.getLogger(__name__)
import functools
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
import match_responses

baseUrl = "/teams/%s/matches/%s"


@timeit
async def getMatchCreated(team_id,match:match_responses.MatchInfo):
    playersList = await retrieve_players_by_team(team_id)  
    url = match_responses.getMatchUrl(team_id,match.id)
    submit_first_subs = match_responses.Link(link=f'{url}/players/submit_lineup',method="post")
    confirm_plan = match_responses.Link(link=f'{url}/{matches_state_machine.MatchState.plan.value}',method="post")

    links = {"submit_lineup":submit_first_subs,"confirm_plan":confirm_plan }
    match_day_response = match_responses.MatchResponse(match=match,squad=playersList,links=createMatchLinks(url,links)).model_dump()
    match_day_responses = [match_day_response]

    response = api_helper.make_api_response(200,match_day_responses)
    logging.info(response)
    return response


async def getMatchConfirmedPlanReadyToStart(team_id,match:match_responses.MatchInfo):
    selected_players = await retrieveStartingLineup(match_id=match.id)
    next_players = await retrieveNextPlannedByMinute(match,minutes=0)
    
    url = match_responses.getMatchUrl(team_id,match.id)
    submit_first_subs = match_responses.Link(link=f'{url}/players/submit_lineup',method="post")
    end_match = match_responses.Link(link=f'{url}/{matches_state_machine.MatchState.ended.value}',method="post")
    links = {"submit_lineup":submit_first_subs,"end_match":end_match }
    match_day_response = match_responses.ActualMatchResponse(match=match,current_players=selected_players,next_players= next_players,how_long_left=match.length, links=createMatchLinks(url,links)).model_dump()
    match_day_responses = []
    match_day_responses.append(match_day_response)

    response = api_helper.make_api_response(200,match_day_responses)
    logging.info(response)
    return response

async def getMatchPlanning(team_id,match):
    selected_players = await retrieveAllPlannedLineups(match_id=match.id)
    
    url = match_responses.getMatchUrl(team_id,match.id)
    submit_first_subs = match_responses.Link(link=f'{url}/players/submit_lineup',method="post")
    confirm_plan = match_responses.Link(link=f'{url}/{matches_state_machine.MatchState.plan_confirmed.value}',method="post")
    links = {"submit_lineup":submit_first_subs,"confirm_plan":confirm_plan }
    match_day_response = match_responses.PlannedMatchResponse(match=match,planned_lineups=selected_players,links=createMatchLinks(url,links)).model_dump()
    match_day_responses = []
    match_day_responses.append(match_day_response)

    response = api_helper.make_api_response(200,match_day_responses)
    logging.info(response)
    return response


@timeit
async def getMatchGuest(match):
    
    periods = await retrieve_periods_by_match(match.id)
    time_playing = 0
    last_period = {}
    started_at = 0
    ended = False
    for period in periods:
        if(period.status=="ended"):
            time_playing = time_playing + (period.time - last_period.time)
            ended = True
        if(period.status == "paused"):
            time_playing = time_playing + (period.time - last_period.time)
            print(f"TIME PLAYING PAUSE {time_playing}")
            last_period = period
        if(period.status=="started" or period.status=="restarted"):
            print(f"TIME PLAYING STARTED {time_playing}")
            if(period.status=="started"):
                started_at = period.time
            last_period = period
    
    time_playing = ((datetime.datetime.utcnow().timestamp()-time_playing-started_at)/60)

    if(ended):
        how_long_left = 0
    else:
        how_long_left = match.length-time_playing

    current_lineup, goals,assists,opposition = await asyncio.gather(
        retrieveCurrentActual(match,time_playing),
        match_day_data.retrieve_player_goals(match),
        match_day_data.retrieve_player_assists(match),
        match_day_data.retrieve_opposition_goals(match)
    ) 
    print(f"HOW LONG LEFT {how_long_left}")
    print(f"TIME PLAYING {time_playing}")
    
    logging.info(f"GOALS {goals}")
    logging.info(f"ASSISTS {assists}")
    
    match_day_response = match_responses.ActualMatchResponse(match=match,current_players=current_lineup, how_long_left=how_long_left,started_at=started_at , next_players=None,links=None,goals=goals,opposition=opposition,assisters=assists).model_dump()
    match_day_responses = []
    match_day_responses.append(match_day_response)

    response = api_helper.make_api_response(200,match_day_responses)
    print(response)
    return response

@timeit
async def getMatchStarted(team_id,match):
    periods = await retrieve_periods_by_match(match.id)
    time_playing = 0
    last_period = {}
    started_at = 0
    ended = False
    for period in periods:
        if(period.status=="ended"):
            time_playing = time_playing + (period.time - last_period.time)
            ended = True
        if(period.status == "paused"):
            time_playing = time_playing + (period.time - last_period.time)
            print(f"TIME PLAYING PAUSE {time_playing}")
            last_period = period
        if(period.status=="started" or period.status=="restarted"):
            print(f"TIME PLAYING STARTED {time_playing}")
            if(period.status=="started"):
                started_at = period.time
            last_period = period
    
    time_playing = (datetime.datetime.utcnow().timestamp()-time_playing-started_at)/60

    if(ended):
        how_long_left = 0
    else:
        how_long_left = match.length-time_playing
    print(f"HOW LONG LEFT {how_long_left}")
    print(f"TIME PLAYING {time_playing}")
    next_lineup,current_lineup,goals,assists,opposition = await asyncio.gather(
        
        retrieveNextPlanned(match,time_playing),
        retrieveCurrentActual(match,time_playing),
        match_day_data.retrieve_player_goals(match),
        match_day_data.retrieve_player_assists(match),
        match_day_data.retrieve_opposition_goals(match)
    ) 
    logging.info(f"NEXT LINEUP {next_lineup}")
    logging.info(f"CURRENT LINEUP {current_lineup}")
    logging.info(f"GOALS {goals}")
    logging.info(f"ASSISTS {assists}")

   

    url = match_responses.getMatchUrl(team_id,match.id)
    submit_first_subs = match_responses.Link(link=f'{url}/players/submit_lineup/subs',method="post")
    confirm_plan = match_responses.Link(link=f'{url}/{matches_state_machine.MatchState.plan_confirmed.value}',method="post")
    end_match = match_responses.Link(link=f'{url}/{matches_state_machine.MatchState.ended.value}',method="post")
    links = {"submit_lineup":submit_first_subs,"confirm_plan":confirm_plan,"end_match":end_match }
    match_day_response = match_responses.ActualMatchResponse(match=match,started_at=started_at, how_long_left=how_long_left, current_players=current_lineup,next_players=next_lineup,links=createMatchLinks(url,links),goals=goals,opposition=opposition,assisters=assists).model_dump()
    match_day_responses = []
    match_day_responses.append(match_day_response)

    response = api_helper.make_api_response(200,match_day_responses)
    
    return response

async def setGoalsFor(match_id, goal_scorer,assister):
    periods = await retrieve_periods_by_match(match_id)
    time_playing = 0
    last_period = {}
    started_at = 0
    ended = False
    for period in periods:
        if(period.status=="ended"):
            time_playing = time_playing + (period.time - last_period.time)
            ended = True
        if(period.status == "paused"):
            time_playing = time_playing + (period.time - last_period.time)
            print(f"TIME PLAYING PAUSE {time_playing}")
            last_period = period
        if(period.status=="started" or period.status=="restarted"):
            print(f"TIME PLAYING STARTED {time_playing}")
            if(period.status=="started"):
                started_at = period.time
            last_period = period
    
    time_playing = int((datetime.datetime.utcnow().timestamp()-time_playing-started_at)/60)

    await save_assists_for(match_id,assister,time_playing)
    await save_goals_for(match_id,goal_scorer,time_playing)
    await matches_data.increment_goals_scored(match_id=match_id,goals=1)

async def setGoalsAgainst(match_id):
    periods = await retrieve_periods_by_match(match_id)
    time_playing = 0
    last_period = {}
    started_at = 0
    ended = False
    for period in periods:
        if(period.status=="ended"):
            time_playing = time_playing + (period.time - last_period.time)
            ended = True
        if(period.status == "paused"):
            time_playing = time_playing + (period.time - last_period.time)
            print(f"TIME PLAYING PAUSE {time_playing}")
            last_period = period
        if(period.status=="started" or period.status=="restarted"):
            print(f"TIME PLAYING STARTED {time_playing}")
            if(period.status=="started"):
                started_at = period.time
            last_period = period
    
    time_playing = int((datetime.datetime.utcnow().timestamp()-time_playing-started_at)/60)
    await save_opposition_goal(match_id,time_playing)
    await matches_data.increment_goals_conceded(match_id=match_id,goals=1)
     

async def updateMatchPeriod(match_id,status):
    await match_day_data.update_period(match_id,status)

def createMatchLinks(url, links:Dict[str,match_responses.Link]):
    self = match_responses.Link(link=url,method="get")
    print(links)
    links["self"] = self
    print(links)
    return links

async def main():
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
        print(matchList)
        match = matchList[0]
        await getMatchConfirmedPlanReadyToStart(sys.argv[2],match)
    if(sys.argv[1]=="getMatchGuest"):
        matchList = await retrieve_match_by_id(sys.argv[3])
        print(matchList)
        match = matchList[0]
        await getMatchGuest(sys.argv[2],match)

if __name__ == "__main__":
    asyncio.run(main())

