import sys
import id_generator
import match_day_data
from match_day_data import retrieveLastPlanned,retrieve_periods_by_match,retrieveNextPlanned,retrieveAllPlannedLineups,retrieveCurrentActual,retrieveStartingLineup,save_goals_for,save_assists_for,save_opposition_goal,retrieveNextPlannedByMinute
from player_data import retrieve_players_by_team_with_stats, retrieve_player
import api_helper
import matches_data
from matches_data import retrieve_match_by_id
from typing import Dict, List
import matches_state_machine
import player_data
import classes
from config import app_config
import traceback
import logging
from firebase_admin import credentials, firestore
import time
from cache_trigger import updateTeamCache, updateMatchCache, updateUserCache, updatePlayerCache
import datetime
import asyncio
logger = logging.getLogger(__name__)
import functools
import player_responses
from datetime import date,timezone
from pydantic import ValidationError
from matches_data import retrieve_match_by_id,retrieve_matches_by_team,save_team_fixture
import response_errors
import notifications
from fcatimer import fcatimer
import matches_backend
from secrets_util import initialise_firebase
import json
from etag_manager import getLatestObject,deleteEtag,setEtag,updateDocument, getObject,whereEqualwhere,whereEqual,whereContains

import exceptions
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


import response_classes

baseUrl = "/teams/%s/matches/%s"


@fcatimer
async def getMatchParent(team_id,match):
    try:
       
        print(f"MATCH STATUS {match.status}")
        if(match.status==matches_state_machine.MatchState.created):
            response = await getMatchCreated(team_id,match)
        elif(match.status==matches_state_machine.MatchState.plan or (match.status==matches_state_machine.MatchState.plan_confirmed and match.date!=date.today())):
            response = await getMatchPlanning(team_id,match)
        elif(match.status==matches_state_machine.MatchState.plan_confirmed and match.date==date.today()):
            response = await getMatchConfirmedPlanReadyToStart(team_id,match)
        elif(match.status==matches_state_machine.MatchState.started or match.status==matches_state_machine.MatchState.paused or match.status==matches_state_machine.MatchState.restarted or match.status==matches_state_machine.MatchState.starting_lineup_confirmed):
            response =  await getMatchStarted(team_id,match)
        elif(match.status==matches_state_machine.MatchState.ended or match.status==matches_state_machine.MatchState.rated):
            response = await getMatchEnded(team_id,match)
        else:
            response =  await getMatchCreated(team_id,match)
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
        traceback.print_exception(*sys.exc_info()) 
        print(e)
        response = api_helper.make_api_response(500,None,e)
        return response  

@fcatimer
async def getMatchCreatedResponse(team_id,match:classes.MatchInfo):
    playersList = await retrieve_players_by_team_with_stats(team_id)  
    url = f"/matches/{match.id}/captain"
    submit_captain = response_classes.Link(link=url,method="post")
    url = f"/teams/{team_id}/players"
    link = response_classes.Link(link=url,method="get",meta_data=team_id)
    
    url = response_classes.getMatchUrl(team_id,match.id)
    submit_first_subs = response_classes.Link(link=f'{url}/submit_plan',method="post")
    confirm_plan = response_classes.Link(link=f'{url}/{matches_state_machine.MatchState.plan_confirmed.value}',method="post")
    links = {"submit_plan":submit_first_subs,"confirm_plan":confirm_plan }
    links["submit_captain"]=submit_captain
    links["planned_lineup"]=link
    
    match_day_response = response_classes.PlannedMatchResponse(match=match,planned_lineups=playersList,links=createMatchLinks(url,links)).model_dump()
   

    return match_day_response

@fcatimer
async def getMatchCreated(team_id,match:classes.MatchInfo):
    match_day_responses = []
    return await getMatchCreatedResponse(team_id,match)    


async def getMatchConfirmedPlanReadyToStart(team_id,match:classes.MatchInfo):
    match_day_responses = []
    return await getMatch(team_id,match)





@fcatimer
async def getMatchPlanningResponse(team_id,match):
    selected_players = await retrieveAllPlannedLineups(match_id=match.id)
    last_minute = 0
    last_lineup = []
    lineup_summary = []

    for lineup in selected_players:
        minute = lineup["status"]
        for player in last_lineup:
            isNew = False
            if(player.selectionInfo.position):
                print(player)
                contains_value = any(obj.info.id == player.info.id for obj in lineup["players"])
                if contains_value:
                    # Check if the player already exists in lineup_summary
                    existing_player = next((p for p in lineup_summary if p.info.id == player.info.id), None)
                    if existing_player:
                        # If player exists, update their stats
                        existing_player.stats.minutes += (minute - last_minute)
                    else:
                        # If player does not exist, add them to lineup_summary
                        isNew = True
                        new_player = classes.Player(info=player.info, stats=player_responses.PlayerStats())
                        new_player.stats.minutes = (minute - last_minute)
                        
            else:
                print(player)
                contains_value = any(obj.info.id == player.info.id for obj in lineup["players"])
                if contains_value:
                    # Check if the player already exists in lineup_summary
                    existing_player = next((p for p in lineup_summary if p.info.id == player.info.id), None)
                    if existing_player:
                        # If player exists, update their stats
                        existing_player.stats.minutes += 0
                    else:
                        # If player does not exist, add them to lineup_summary
                        isNew = True
                        new_player = classes.Player(info=player.info, stats=player_responses.PlayerStats())
                        new_player.stats.minutes = 0
                        
            if(isNew):
                new_player.stats.total_minutes = (match.length - minute)+new_player.stats.minutes
                lineup_summary.append(new_player)
            else:
                existing_player.stats.total_minutes = (match.length - minute)+existing_player.stats.minutes

        last_minute = minute
        last_lineup = lineup["players"]
        print("LAST MINUTE")
        print(last_minute)
        print("LAST LINEUP")
        print(last_lineup)

    print("LINEUP SUMMARY")
    print(lineup_summary)

    captains = await retrieve_player(match.captain)
    captain = None
    url = f"/matches/{match.id}/captain"
    submit_captain = response_classes.Link(link=url,method="post")
    
    if(len(captains)>0):
        captain = captains[0]
    print(selected_players)
    url = response_classes.getMatchUrl(team_id,match.id)
    submit_first_subs = response_classes.Link(link=f'{url}/submit_plan',method="post")
    confirm_plan = response_classes.Link(link=f'{url}/{matches_state_machine.MatchState.plan_confirmed.value}',method="post")
    links = {"submit_plan":submit_first_subs,"confirm_plan":confirm_plan }
    links["submit_captain"]=submit_captain
    match_day_response = response_classes.ActualMatchResponse(match=match,captain=captain, planned_lineup_summary=lineup_summary, current_players=selected_players[0]['players'],planned_lineups=selected_players,links=createMatchLinks(url,links)).model_dump()
    
    return match_day_response
@fcatimer
async def getMatchPlanning(team_id,match):
    match_day_responses = []
    return await getMatchPlanningResponse(team_id,match)
   


@fcatimer
async def getMatchGuest(match:classes.MatchInfo)-> response_classes.ActualMatchResponse:
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
        next_minute = next_lineup[0]['selectionInfo'].minuteOn
        refresh_at = int((next_minute-time_playing)/2)
        if(len(last_planned)>0):
            last_minute = last_planned[0]['selectionInfo'].minuteOn
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

@fcatimer
async def getSubs(next_lineup, current_lineup)->List[response_classes.PlayerMatchStat]:
    if not next_lineup or not current_lineup:
        return []

    plannedSubsOff = compare_and_create_subs(next_lineup,current_lineup)
    

    plannedSubsOn = compare_and_create_subs(current_lineup,next_lineup)
    
    plannedSubsOn.sort(key=lambda x: x.selectionInfo.position)
    plannedSubsOff.sort(key=lambda x: x.selectionInfo.position)
    # Ensure that lengths are the same, or handle cases where they're not
    min_length = min(len(plannedSubsOff), len(plannedSubsOn))

    subs = []
    for i in range(min_length):
        print(plannedSubsOff[i])
        print(plannedSubsOn[i])
        #to maintain backwards compatibility i am adding a primary player
        stat = response_classes.PlayerMatchStat(player=plannedSubsOff[i].info, player_off=plannedSubsOff[i],player_on=plannedSubsOn[i],time=round(plannedSubsOn[i].selectionInfo.minuteOn),minute=round(plannedSubsOn[i].selectionInfo.minuteOn),type="Sub")
        subs.append(stat)

    return subs

@fcatimer
def compare_and_create_subs(list1, list2):
    new_list = []
    # Create a mapping of id to position from list2 for easier comparison
    position_map = {item.info.id: item.selectionInfo.position for item in list2}

    # Iterate through list1 and compare
    for item in list1:
        player_id = item.info.id
        # Check if the position is blank in list1 and not blank in list2
        if item.selectionInfo.position == '' and position_map.get(player_id, '') != '':
            # Find the corresponding item in list2 and add it to new_list
            for item2 in list2:
                if item2.info.id == player_id:
                    new_list.append(item2)
                    break

    return new_list


@fcatimer
async def getPositionChanges(current_lineup,next_lineup):
    if not next_lineup or not current_lineup:
        return []
    current_positions = compare_lists_for_different_positions(current_lineup,next_lineup)
    next_positions = compare_lists_for_different_positions(next_lineup,current_lineup)
    min_length = min(len(current_positions), len(next_positions))
    subs = []

    current_positions.sort(key=lambda x: x.info.name)
    next_positions.sort(key=lambda x: x.info.name)
    for i in range(min_length):
       
        #to maintain backwards compatibility i am adding a primary player
        stat = response_classes.PlayerMatchStat(player=current_positions[i].info, player_off=current_positions[i],player_on=next_positions[i],time=round(next_positions[i].selectionInfo.minuteOn),minute=round(next_positions[i].selectionInfo.minuteOn),type="PositionChange")
        subs.append(stat)

    return subs

@fcatimer
def compare_lists_for_different_positions(list1, list2):
    new_list = []
    # Create a mapping of id to position from list2 for easier comparison
    position_map = {item.info.id: item.selectionInfo.position for item in list2}

    # Iterate through list1 and compare
    for item in list1:
        player_id = item.info.id
        list1_position = item.selectionInfo.position
        list2_position = position_map.get(player_id, None)

        # Check if the position is different in both lists and not blank
        if list1_position != list2_position and list1_position != '' and list2_position != '':
            # Add the item from list2 to new_list
            new_list.append(next((item2 for item2 in list2 if item2.info.id == player_id), None))

    return new_list


async def getChangesDue(match):
    time_playing = await how_long_played(match.id)
    all_planned,all_actual_lineups = await asyncio.gather(
            retrieveAllPlannedLineups(match.id),
            match_day_data.retrieveAllActualLineups(match,time_playing),
        )
    next_lineup = []
    current_lineup = []
    last_planned = []
    starting_lineup = []
    next_lineup_obj = {}
    last_lineup_obj = {}
    current_lineup_obj = {}
        # Next Planned
    next_lineups = [item for item in all_planned if item["status"]  > time_playing]
    if(len(next_lineups)>0):
        next_lineup_obj = next_lineups[0] #{status: players:}
    print(f"Next LINEUP {next_lineup_obj}")
    # Current Actual
    if(len(all_actual_lineups)>0):
        current_lineup_obj = all_actual_lineups[0]
    print(f"Current LINEUP {current_lineup}")
    # Last Planned
    previous_planned_lineups = [item for item in all_planned if item["status"] < time_playing]
    if(len(previous_planned_lineups)>0):
        last_lineup_obj = previous_planned_lineups[len(previous_planned_lineups)-1]
    print(f"Last LINEUP {last_lineup_obj}")
    # Starting Lineup
    if(len(all_planned)>0):
        starting_lineup = all_planned[0]["players"]
    else:
        starting_lineup = []
    print(f"Starting LINEUP {last_planned}")
    
    if(next_lineup_obj and len(next_lineup_obj["players"])>0):
        next_lineup = next_lineup_obj["players"]
    print(f"Next LINEUP JUST PLAYERS {next_lineup}")
    if(last_lineup_obj and len(last_lineup_obj["players"])>0):
        last_planned = last_lineup_obj["players"]
        print(f"Last LINEUP JUST PLAYERS {last_planned}")
    if(current_lineup_obj and len(current_lineup_obj["players"])>0):
        current_lineup = current_lineup_obj["players"]
    print(f"CURRENT LINEUP JUST PLAYERS {current_lineup}")
    
    if(len(next_lineup)>0):
        next_minute = next_lineup[0].selectionInfo.minuteOn
        refresh_at = int((next_minute-time_playing)/2)
        if(len(last_planned)>0):
            last_minute = last_planned[0].selectionInfo.minuteOn
            

            planned_subs = await getSubs(next_lineup,current_lineup)
            planned_position_changes = await getPositionChanges(next_lineup,current_lineup)
            
        else:
            planned_subs = await getSubs(next_lineup,current_lineup)
            planned_position_changes = await getPositionChanges(next_lineup,current_lineup)
    else:
        refresh_at = int(match.length-time_playing)
        planned_subs=[]
        planned_position_changes = []
    
    return {"planned_subs":planned_subs,"planned_position_changes":planned_position_changes,"refresh_at":refresh_at}



@fcatimer
async def getMatchEnded(team_id,match:classes.MatchInfo):
    try:
        goals,opposition,all_actual_lineups,players = await asyncio.gather(
            match_day_data.retrieve_player_goals(match),
            match_day_data.retrieve_opposition_goals(match),
            match_day_data.retrieveAllActualLineups(match,0),
            player_data.retrieve_players_by_team_no_stats(team_id)
        )
        lineup = []
        subs = []
        positionChanges = []
        i=1
        if(len(all_actual_lineups)==0):
            lineup = players
        else:
            lineup = all_actual_lineups
        for list in all_actual_lineups:
                if(i<len(all_actual_lineups)):
                    subs = subs + await getSubs(list["players"],all_actual_lineups[i]["players"])
                    positionChanges = positionChanges + await getPositionChanges(list["players"],all_actual_lineups[i]["players"])
                    i=i+1
            
        report = []

        report = report+subs
        
        report = report+goals
        
        report = report+opposition
        report = report+positionChanges
        
        report.sort(key=lambda x:x.minute)
        
        url = response_classes.getMatchUrl(team_id,match.id)
        match_day_response = response_classes.ActualMatchResponse(match=match,started_at=0, actual_lineups=lineup, links=createMatchLinks(url,{}),scorers=goals,opposition=opposition,report=report,actual_position_changes=positionChanges).model_dump()
            
        return match_day_response
    except Exception as e:
        traceback.print_exception(*sys.exc_info()) 

@fcatimer
async def getMatch(team_id,match:classes.MatchInfo):
    try:
        time_playing = await how_long_played(match.id)
        how_long_left = 0
        if(match.status==matches_state_machine.MatchState.ended.value):
            how_long_left = 0
        else:
            how_long_left = match.length-time_playing
        print(f"HOW LONG LEFT {how_long_left}")
        
        all_planned,goals,opposition,all_actual_lineups = await asyncio.gather(
            
            retrieveAllPlannedLineups(match.id),
            match_day_data.retrieve_player_goals(match),
            match_day_data.retrieve_opposition_goals(match),
            match_day_data.retrieveAllActualLineups(match,time_playing),
            
        )
        next_lineup = []
        current_lineup = []
        last_planned = []
        starting_lineup = []
        next_lineup_obj = {}
        last_lineup_obj = {}
        current_lineup_obj = {}
            # Next Planned
        next_lineups = [item for item in all_planned if item["status"]  > time_playing]
        if(len(next_lineups)>0):
            next_lineup_obj = next_lineups[0] #{status: players:}
        print(f"Next LINEUP {next_lineup_obj}")
        # Current Actual
        if(len(all_actual_lineups)>0):
            current_lineup_obj = all_actual_lineups[0]
        print(f"Current LINEUP {current_lineup}")
        # Last Planned
        previous_planned_lineups = [item for item in all_planned if item["status"] < time_playing]
        if(len(previous_planned_lineups)>0):
            last_lineup_obj = previous_planned_lineups[len(previous_planned_lineups)-1]
        print(f"Last LINEUP {last_lineup_obj}")
        # Starting Lineup
        if(len(all_planned)>0):
            starting_lineup = all_planned[0]["players"]
        else:
            starting_lineup = []
        print(f"Starting LINEUP {last_planned}")
        
        if(next_lineup_obj and len(next_lineup_obj["players"])>0):
            next_lineup = next_lineup_obj["players"]
        print(f"Next LINEUP JUST PLAYERS {next_lineup}")
        if(last_lineup_obj and len(last_lineup_obj["players"])>0):
            last_planned = last_lineup_obj["players"]
            print(f"Last LINEUP JUST PLAYERS {last_planned}")
        if(current_lineup_obj and len(current_lineup_obj["players"])>0):
            current_lineup = current_lineup_obj["players"]
        print(f"CURRENT LINEUP JUST PLAYERS {current_lineup}")
        
        if(len(next_lineup)>0):
            next_minute = next_lineup[0].selectionInfo.minuteOn
            refresh_at = int((next_minute-time_playing)/2)
            if(len(last_planned)>0):
                last_minute = last_planned[0].selectionInfo.minuteOn
                next_close = next_minute - time_playing
                last_close = time_playing - last_minute

                if(next_close<last_close):
                    planned_subs = await getSubs(next_lineup,current_lineup)
                    planned_position_changes = await getPositionChanges(next_lineup,current_lineup)
                else:
                    planned_subs = await getSubs(last_planned,current_lineup)
                    planned_position_changes = await getPositionChanges(next_lineup,current_lineup)
            else:
                planned_subs = await getSubs(next_lineup,current_lineup)
                planned_position_changes = await getPositionChanges(next_lineup,current_lineup)
        else:
            refresh_at = int(how_long_left)
            planned_subs=[]
            planned_position_changes = []

        if(len(current_lineup)==0):
            current_lineup = starting_lineup
        

        subs = []
        positionChanges = []
        i=1
        for list in all_actual_lineups:
            if(i<len(all_actual_lineups)):
                subs = subs + await getSubs(list["players"],all_actual_lineups[i]["players"])
                positionChanges = positionChanges + await getPositionChanges(list["players"],all_actual_lineups[i]["players"])
                i=i+1
        
        report = []

        report = report+subs
        print(f"Report = {report}")
        print(f"Subs = {subs}")
        report = report+goals
        print(f"Report = {report}")
        print(f"Goals = {goals}")
        report = report+opposition
        report = report+positionChanges
        print(f"Report = {report}")
        print(f"Opposition = {opposition}")
        report.sort(key=lambda x:x.minute)
        
        print(f"NEXT LINEUP {next_lineup}")
        print(f"LAST LINEUP {last_planned}")
        print(f"CURRENT LINEUP {current_lineup}")
        print(f"GOALS {goals}")
        print(f"PLANNED POSITIONS CHANGES {match.id} {planned_position_changes} on minute {time_playing}")
        print(f"PLANNED SUBS {match.id} {planned_subs} on minute {time_playing}")


        url = response_classes.getMatchUrl(team_id,match.id)
        
        start_match = response_classes.Link(link=f'{url}/start',method="post")
        submit_first_subs = response_classes.Link(link=f'{url}/players/submit_lineup/subs',method="post")
        submit_plan = response_classes.Link(link=f'{url}/submit_plan',method="post")
        captain_player = None
        
        confirm_plan = response_classes.Link(link=f'{url}/{matches_state_machine.MatchState.plan_confirmed.value}',method="post")
        end_match = response_classes.Link(link=f'{url}/{matches_state_machine.MatchState.ended.value}',method="post")
        links = {"start_match":start_match,"submit_subs":submit_first_subs,"submit_plan":submit_plan,"confirm_plan":confirm_plan,"end_match":end_match }
        match_day_response = response_classes.ActualMatchResponse(match=match,planned_lineups=all_planned,planned_subs=planned_subs,last_planned=last_planned,started_at=0, how_long_left=how_long_left, current_players=current_lineup,next_players=next_lineup,actual_lineups=all_actual_lineups, links=createMatchLinks(url,links),scorers=goals,opposition=opposition,actual_subs=subs,refresh_at=refresh_at,report=report,captain=captain_player,actual_position_changes=positionChanges,planned_position_changes=planned_position_changes).model_dump()
        
        return match_day_response
    except Exception as e:
        traceback.print_exception(*sys.exc_info()) 

@fcatimer
async def getMatchStarted(team_id,match):
    match_day_responses = []
    return await getMatch(team_id,match)



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
            current_pause = datetime.datetime.now(datetime.timezone.utc).timestamp()-last_period.time
            time_playing = time_playing+current_pause
            
        print("################### TIME PLAYING 1#######################")
        print(time_playing)
        how_long_ago_started = (datetime.datetime.now(datetime.timezone.utc).timestamp()-started_at)
        print("HOW LONG AGO STARTED")
        print(how_long_ago_started)
        time_playing = (datetime.datetime.now(datetime.timezone.utc).timestamp()-time_playing-started_at)
        print("################### TIME PLAYING 2#######################")
        print(time_playing/60)
        return time_playing/60
    else:
        return 0
 

@fcatimer
async def removeGoalsFor(id,match_id,team_id):
    
    await match_day_data.delete_goal_scorer(id)
    await matches_data.increment_goals_scored(match_id=match_id,goals=-1)
    
    message = f"Score correction"

    await updateMatchCache(match_id)
    await updateTeamCache(team_id)
    data = {
        "link":f"/matches/{match_id}",
        "match_id":match_id,
        "action":"goals_for"
    }
    await notifications.sendNotificationUpdatesLink(match_id,message,message,'match',data)



@fcatimer
async def addGoalScorers(team_id,match_id, goal_scorer,assister,type,assist_type,time_playing):
    
    scored_by =""
    print(assister)
    if(assister is not None):
        await save_goals_for(match_id,goal_scorer["id"],time_playing,type,assister["id"],assist_type)
        scored_by = f"Assisted by {assister['name']} - {type}"
    else:   
        await save_goals_for(match_id,goal_scorer["id"],time_playing,type,"","")
    

    db = firestore.client()
    if(len(goal_scorer["id"])>0):
        doc_ref = db.collection(f"{app_config.db_prefix}_player_stats").document(goal_scorer["id"])
        goalsField = f"matches.{match_id}.goals"

        data = {
            goalsField: firestore.Increment(1)
        }
        doc_ref.set(
        data, merge=True
        )
    


    message = f"{round(time_playing)}' {goal_scorer['name']} scores"
    await updateMatchCache(match_id)
    await updateTeamCache(team_id)
    data = {
        "link":f"/matches/{match_id}",
        "match_id":match_id,
        "action":"goals_for"
    }
    await notifications.sendNotificationUpdatesLink(match_id,scored_by,message,'match',data)


@fcatimer
async def setGoalsFor(team_id,match_id, goal_scorer,assister,type,assist_type):
    time_playing = await how_long_played(match_id)
    scored_by =""
    print(assister)
    fs_match = await getObject(match_id,'matches_store')
    if(assister is not None):
        await save_goals_for(match_id,goal_scorer["info"]["id"],time_playing,type,assister["info"]["id"],assist_type)
        scored_by = f"Assisted by {assister['info']['name']} - {type}"
        if(fs_match):
            fs_match_dict = fs_match.get().to_dict()
            scorers = fs_match_dict.get('scorers',[])
            scorers.append({"scorer":goal_scorer['info']['id'],"assister":assister['info']['id'],"goal_type":type,"assist_type":assist_type,"minute":time_playing})
    else:   
        await save_goals_for(match_id,goal_scorer["info"]["id"],time_playing,type,"","")
        if(fs_match):
            fs_match_dict = fs_match.get().to_dict()
            fs_match_dict = fs_match.get().to_dict()
            scorers = fs_match_dict.get('scorers',[])
            scorers.append({"scorer":goal_scorer['info']['id'],"goal_type":type,"minute":time_playing})
    await matches_data.increment_goals_scored(match_id=match_id,goals=1)
    
    
    if(fs_match):
        
        fs_match.update({"scorers":scorers})

    fs_player = await getObject(goal_scorer,'player_stats')
    if fs_player:
        fs_player_dict = fs_player.get().to_dict()
        current_list = fs_player_dict.get('actual_matches', {})
        fs_match = current_list.get(match_id,{match_id:{}})
        fs_subs = fs_match.get("goals",[])
        fs_subs.append({"goal_type":type,"minute":time_playing})
        fs_match["goals"] = fs_subs
        current_list[match_id] = fs_match
        fs_player.update(current_list)
    
    fs_assister = await getObject(assister,'player_stats')
    if fs_assister:
        fs_assister_dict = fs_assister.get().to_dict()
        current_list = fs_assister_dict.get('actual_matches', {})
        fs_match = current_list.get(match_id,{match_id:{}})
        fs_subs = fs_match.get("assists",[])
        fs_subs.append({"assist_type":assist_type,"minute":time_playing})
        fs_match["assists"] = fs_subs
        current_list[match_id] = fs_match
        fs_assister.update(current_list)
    


    message = f"{round(time_playing)}' {goal_scorer['info']['name']} scores"
    await updateMatchCache(match_id)
    await updateTeamCache(team_id)
    await updatePlayerCache(team_id)
    data = {
        "link":f"/matches/{match_id}",
        "match_id":match_id,
        "action":"goals_for"
    }
    await notifications.sendNotificationUpdatesLink(match_id,scored_by,message,'match',data)

@fcatimer
async def sendGoalScoredNotification(team_id,match_id, goal_scorer,assister,type,assist_type):

    print("deprecated")
    # fs_team = await getObject(team_id,'teams_store')
    # team_name = ""
    
    # if(fs_team):
    #     fs_team_dict = fs_team.get().to_dict()
    #     team_name = fs_team_dict['name']

    # fs_match = await getObject(match_id,'matches_store')
    # opposition = ""
    # goals_for = 0
    # goals_against = 0
    # if(fs_match):
    #     fs_match_dict = fs_match.get().to_dict()
    #     opposition = fs_match_dict['opposition']
    #     goals_for = fs_match_dict.get('goals',0)
    #     goals_against = fs_match_dict.get('conceded',0)
    # assisted_by = ""
    # if(assister is not None):
    #     assisted_by = f", assisted by {assister['forename']} with a {assist_type.lower()}"
    # title = f"Gooooaaaal {team_name} ({goals_for}) - {goals_against} {opposition}"
    # message = f"{type.lower()} goal scored by {goal_scorer['forename']}{assisted_by}"
    
    # fs_team_users = await whereContains('users_store','teams',team_id)
    
    # if(fs_team_users):
    #     for fs_team_user in fs_team_users:
    #         notification_id = id_generator.generate_random_number(10)
    #         metadata={"match_id":match_id,"team_id":fs_match_dict["team_id"],"email":fs_team_user.to_dict()['email'],'notification_id':notification_id}
    #         notification = {
    #             'message':message,
    #             'metadata':metadata,
    #             'email':fs_team_user.to_dict()['email'],
    #             'type':'match',
    #             'subject':title,
    #             'sent':datetime.datetime.now(timezone.utc)
    #         }
            
    #         fs_devices = await whereEqual('devices','email',fs_team_user.to_dict()['email'])
    #         print(f"DEVICES {fs_devices}")
    #         for fs_device in fs_devices:
    #             fs_device_dict = fs_device.to_dict()
    #             token = fs_device_dict['token']
    #             print(f"TOKEN {token}")
    #             await notifications.sendNotification(match_id,message,title,'match',False,token,metadata)
            
    #         await updateDocument('user_notifications',str(notification_id),notification)

@fcatimer
async def sendGoalConcededNotification(team_id,match_id):
    print('deprecated')
    # fs_team = await getObject(team_id,'teams_store')
    # team_name = ""
    
    # if(fs_team):
    #     fs_team_dict = fs_team.get().to_dict()
    #     team_name = fs_team_dict['name']

    # fs_match = await getObject(match_id,'matches_store')
    # opposition = ""
    # goals_for = 0
    # goals_against = 0
    # if(fs_match):
    #     fs_match_dict = fs_match.get().to_dict()
    #     opposition = fs_match_dict['opposition']
    #     goals_for = fs_match_dict.get('goals',0)
    #     goals_against = fs_match_dict.get('conceded',0)
    
    # title = f"Goal conceded - {team_name} {goals_for} - ({goals_against}) {opposition}"
    # message = f"Scored by {opposition}"
    # data = {
    #         "link":f"/matches/{match_id}",
    #         "match_id":match_id,
    #         "team_id":team_id,
    #         "action":"goal_conceded",
    #         "silent":False
    #     }
    # fs_team_users = await whereContains('users_store','teams',team_id)
    
    # if(fs_team_users):
    #     for fs_team_user in fs_team_users:
    #         fs_devices = await whereEqual('devices','email',fs_team_user.to_dict()['email'])
    #         print(f"DEVICES {fs_devices}")
    #         for fs_device in fs_devices:
    #             fs_device_dict = fs_device.to_dict()
    #             token = fs_device_dict['token']
    #             print(f"TOKEN {token}")
    #             await notifications.sendNotification(match_id,message,title,'match_update',False,token,data)

@fcatimer
async def calculateTimePlayed(match:classes.MatchInfo):
    print(f"TIME NOW IN SECONDS = {datetime.datetime.now(datetime.timezone.utc).timestamp}")
    print(f"LAST START TIME = {match.time_last_started.timestamp}")
    minutes_played = ((datetime.datetime.now(datetime.timezone.utc) - match.time_last_started))
    
    return minutes_played.total_seconds()+match.seconds_played_when_paused


            
@fcatimer
async def updateStatus(match_id,status:matches_state_machine.MatchState):
    print(f"UPDATE STATUS {status.value}")
    # matches = await matches_data.update_match_status(match_id,status.value)
    fs_match = await getObject(match_id,'matches_store')
    fs_match_dict = fs_match.get().to_dict()
    match = classes.MatchInfo(**fs_match_dict)
    print(f"FS MATCH DICT {fs_match_dict}")
    match.status = status
    
    state = {'status':status.value,'time':datetime.datetime.now(datetime.timezone.utc)}
    match.status_history.append(state)
    fs_match.update(match.model_dump())
    
    fs_team = await getObject(match.team_id,'teams_store')
    team = classes.Team(**fs_team.get().to_dict())
    type="match"
    silent='False'
    action = "status_updated"
    if(status==matches_state_machine.MatchState.plan_confirmed):
        message = f"{team.name} vs {match.opposition} match day plans confirmed"
        type="admins"
    elif(status==matches_state_machine.MatchState.started):
        fs_match.update({'time_started':datetime.datetime.now(datetime.timezone.utc)})
        fs_match.update({'time_last_started':datetime.datetime.now(datetime.timezone.utc)})
        message = f"{team.name} vs {match.opposition} has started"
    elif(status==matches_state_machine.MatchState.restarted):
        fs_match.update({'time_last_started':datetime.datetime.now(datetime.timezone.utc)})
        message = f"{team.name} vs {match.opposition} has restarted"
    elif(status==matches_state_machine.MatchState.paused):
        fs_match.update({'seconds_played_when_paused':await calculateTimePlayed(match)})
        message = f"{team.name} vs {match.opposition} has paused"
    elif(status==matches_state_machine.MatchState.ended):
        fs_lineups = await whereEqual('lineups_store','match_id',match_id)

        fs_match.update({'time_ended':datetime.datetime.now(datetime.timezone.utc)})
        message = f"{team.name} vs {match.opposition} has ended"
    elif(status==matches_state_machine.MatchState.created):
        await delete_lineups(match_id,0)
        message = f"{team.name} vs {match.opposition} start_again"
        action = "start_again"
        silent='True'
    elif(status==matches_state_machine.MatchState.plan):
        message = f"{team.name} vs {match.opposition} in plan"
        action = "plan"
        silent='True'
    elif(status==matches_state_machine.MatchState.rated):
        message = f"{team.name} vs {match.opposition} has been rated"
        action = "rated"
    elif(status==matches_state_machine.MatchState.cancelled):
        message = f"{team.name} vs {match.opposition} has been cancelled"
        action = "cancelled"
    
    data = {
        "link":f"/matches/{match_id}",
        "match_id":match_id,
        "action":action,
        "status":status,
        "silent":silent
    }
    
    await updateMatchCache(match_id)
    await updateTeamCache(team.id)
    await notifications.sendNotificationUpdatesLink(match_id,message,message,type,data)
    
    return ""



async def subs_due(match_id):
    matches = retrieve_match_by_id(match_id)
    match = matches[0]
    
    message = f"Subs due for {match.name} vs {match.opposition}"

    await notifications.sendNotificationUpdates(match_id,message,"")




async def setGoalsAgainst(match_id,team_id, opposition):
    time_playing = await how_long_played(match_id)
    await save_opposition_goal(match_id,time_playing)
    await matches_data.increment_goals_conceded(match_id=match_id,goals=1)
    scored_by = f"{int(time_playing)}' Goal scored by {opposition}"
    fs_match = await getObject(match_id,'matches_store')
    fs_match_dict = fs_match.get().to_dict()
    print(f"FS MATCH DICT {fs_match_dict}")
    conceded_history = fs_match_dict.get('conceded_history',[])
    conceded_history.append({"minute":time_playing})
    conceded = fs_match_dict.get('conceded',0)
    conceded = conceded+1
    status = {'conceded':conceded,'conceded_history':conceded_history}
    
    fs_match.update(status)
    print(f"UPDATED SUCCESSFULLY FS MATCH DICT {fs_match_dict}")
    await updateMatchCache(match_id)
    await updateTeamCache(team_id)
    data = {
        "link":f"/matches/{match_id}",
        "match_id":match_id,
        "action":"goals_against"
    }
    await notifications.sendNotificationUpdatesLink(match_id,scored_by,scored_by,'match',data)
 
@fcatimer
async def updateMatchPeriod(match_id,status):
    periods = await retrieve_periods_by_match(match_id)
    if(len(periods)>0):
        if(periods[len(periods)-1].status!=status):
            await match_day_data.update_period(match_id,status)
    else:
        await match_day_data.update_period(match_id,status)
    await updateMatchCache(match_id)
    
    await sendStatusUpdate(match_id,status)

@fcatimer
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
    elif(status==matches_state_machine.MatchState.ended.value):
        message = f"{match.team.name} vs {match.opposition} has ended"
    elif(status==matches_state_machine.MatchState.substitutions.value):
        message = f"{match.team.name} vs {match.opposition} - lineup changes made"
    else:
        message = f"{match.team.name} vs {match.opposition} status update"
   
    data = {
        "link":f"/matches/{match_id}",
        "match_id":match_id,
        "action":"status_updated",
        "status":status
    }
    await notifications.sendNotificationUpdatesLink(match_id,message,message,'match',data)

def remove_lineups_greater_than_minute(data_list, field_name, minute):
  """Removes objects from a list where a specified field meets a condition.

  Args:
      data_list: The list to filter.
      field_name: The name of the field to check for the condition.
      condition: A function that takes an object from the list and returns True
                 if the object should be removed, False otherwise.

  Returns:
      A new list containing only objects that don't meet the condition.
  """

  return [item for item in data_list if not item[field_name]>=minute]

@fcatimer
async def delete_lineups(match_id,minute):
    db = firestore.client()
    docs = await whereEqual('lineups_store','match_id',match_id)
    batch = db.batch()
    for doc in docs:
        fs_lineup_dict = doc.to_dict()
        print(fs_lineup_dict['minute'])
        if fs_lineup_dict['type']=='planned' and int(fs_lineup_dict['minute'])>=int(minute):
            print("deleted")
            batch.update(doc.reference, {'deleted':True})
    batch.commit()
@fcatimer
async def submit_planned_lineup(match_id,players:List[classes.Player],minute):
   
  
    id = id_generator.generate_random_number(7)
    await delete_lineups(match_id,minute)
    fs_match = await getObject(match_id,'matches_store')
    if(fs_match):
        fs_match_dict = fs_match.get().to_dict()
        match = classes.MatchInfo(**fs_match_dict)
        if(match.planned_lineups is None):
            match.planned_lineups = []
        i = 0
        for lineup in match.planned_lineups:
            i = i+1
            if(lineup.minute>=float(minute)):
                match.planned_lineups.pop(i)
        match.planned_lineups.append(classes.Lineup(id=str(id),players=players,match_id=match_id,minute=minute,type='planned'))
        fs_match.update(match.model_dump())
    # await updateDocument('lineups_store',str(id),classes.Lineup(id=str(id),players=players,match_id=match_id,minute=minute,type='planned'))
    

@fcatimer
async def submit_match_lineup(match_id,players:List[classes.Player],minute):
   
  
    id = id_generator.generate_random_number(7)
    await delete_lineups(match_id,minute)
    fs_match = await getObject(match_id,'matches_store')
    if(fs_match):
        fs_match_dict = fs_match.get().to_dict()
        match = classes.MatchInfo(**fs_match_dict)
        for lineup in match.actual_lineups:
            if(lineup.minute>=float(minute)):
                lineup.deleted=True
        match.actual_lineups.append(classes.Lineup(id=str(id),players=players,match_id=match_id,minute=minute,type='actual'))
        fs_match.update(match.model_dump())
    
    
           
      
async def start_match(match_id):
    # await updateMatchPeriod(match_id,matches_state_machine.MatchState.started.value)
    await updateStatus(match_id,matches_state_machine.MatchState.started)

async def sort_by_minute(lineup):
    return lineup['minute']

# @fcatimer
# async def submit_match_lineup(match_id,players:List[classes.Player],minute):
#     id = id_generator.generate_random_number(7)
#     player_ids = [{"id":player.info.id,"position":player.selectionInfo.position} for player in players]
#     # await delete_lineups(match_id,minute)
#     await updateDocument('lineups_store',str(id),classes.Lineup(id=str(id),players=players,match_id=match_id,minute=minute,type='actual'))
#     fs_match = await getObject(match_id,'matches_store')
#     print(fs_match)
#     empty_list = []
#     fs_match_dict = fs_match.get().to_dict()
#     fs_lineups = fs_match_dict.get('actual_lineups',[])
  
#     fs_lineups = remove_lineups_greater_than_minute(fs_lineups,"minute",minute)
#       # Set an empty list as the default
#     fs_lineups.append({"minute":minute,"id":id})
#     fs_match.update({'actual_lineups':fs_lineups})
#     for player in players:
#         if(len(player.selectionInfo.position)>0):
#             fs_player = await getObject('player_stats',player.info.id)
#             if fs_player:
#                 fs_player_dict = fs_player.get().to_dict()
#                 current_list = fs_player_dict.get('actual_matches', {})
#                 fs_match = current_list.get(match_id,{match_id:{}})
               
                
#                 fs_subs = fs_match.get("lineup",[])
#                 fs_subs.append({"position":player.selectionInfo.position,"minute":minute})
#                 fs_match["lineup"] = fs_subs
#                 current_list[match_id] = fs_match
#                 fs_player.update(current_list)
#             else:
#                 await updateDocument('player_stats',str(player.info.id),{'actual_matches': {match_id:{"lineup":[{"position":player.selectionInfo.position}]}}})

    
@fcatimer
async def submit_starting_lineup(match_id,players:List[classes.Player]):
    # await match_day_data.save_actual_lineup(match_id=match_id,players=players,time_playing=0)
    await submit_match_lineup(match_id,players,0)
    await updateStatus(match_id=match_id,status=matches_state_machine.MatchState.starting_lineup_confirmed)
    # await matches_data.update_match_status(match_id=match_id,status=matches_state_machine.MatchState.starting_lineup_confirmed.value)

async def submit_subs(match,players:List[classes.Player]):
    time_playing = await how_long_played(match.id)
    
    print("************** SUBS ON HERE ***************")
    all_actual = await match_day_data.retrieveAllActualLineups(match=match,how_log_ago=time_playing)
    current_players = all_actual[0]
    print(current_players)
    print(players)
    difference = set(players).difference(current_players["players"])

    subs = await getSubs(players,current_players["players"])
    for sub in subs:
        fs_match = await getObject(match.id,'matches_store')
        if(fs_match):
            fs_match_dict = fs_match.get().to_dict()
            fs_subs = fs_match_dict.get('subs',[])
            fs_sub = {'on':sub.player_on.info.id,'off':sub.player_off.info.id,'minute':time_playing}
            fs_subs.append(fs_sub)
            fs_match.update({'subs':fs_subs})

    print("************** SUBS ON***************")
    print(difference)
    await submit_match_lineup(match.id,players,time_playing)
    for player in difference:
        sub_type = "on" if (len(player.selectionInfo.position)>0) else "off"
        fs_player = await getObject(player.info.id,'player_stats')
        if fs_player:
            fs_player_dict = fs_player.get().to_dict()
            current_list = fs_player_dict.get('actual_matches', {})
            fs_match = current_list.get(match.id,{match.id:{}})
            fs_subs = fs_match.get("subs",[])
            fs_subs.append({"type":sub_type,"minute":time_playing,"position":player.selectionInfo.position})
            fs_match["subs"] = fs_subs
            current_list[match.id] = fs_match
            fs_player.update(current_list)
        else:
            await updateDocument('player_stats',str(player.info.id),{'actual_matches':{match.id:{"subs":[{"type":sub_type,"minute":time_playing}]}}})
    await match_day_data.save_subs(match_id=match.id,players=difference,time_playing=time_playing)
    await match_day_data.save_actual_lineup(match_id=match.id,players=players,time_playing=time_playing)
    await updateMatchPeriod(match.id,matches_state_machine.MatchState.substitutions.value)

def createMatchLinks(url, links:Dict[str,response_classes.Link]):
    self = response_classes.Link(link=url,method="get")
    print(links)
    links["self"] = self
    print(links)
    return links







async def create_match_backend(match,team_id) -> response_classes.PlannedMatchResponse:
    type = match.get("type",None)
    if(type):
        type = response_classes.MatchType(type)
    id = id_generator.generate_random_number(7)
    matchInfo = classes.MatchInfo(id=str(id),opposition=match["opposition"],homeOrAway=match["homeOrAway"],location=match["location"],placeId=match["placeId"],date=match["date"],length=match["length"],status=matches_state_machine.MatchState.created,type=type,team_id=team_id)
    
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
async def setUpMatchFromDB(match):
    
    result = await matches_backend.getMatchFromDB(match.id)
    return result["result"]

@fcatimer
async def setUpMatch(match):
    
    result = await matches_backend.getMatchFromDB(match["match"]["id"])
    return result["result"]




@fcatimer
async def list_matches_by_team_backend(team_id):

    team = await getLatestObject(team_id,"teams")
    print(f"TEAM FROM LIST MATCHES \n {team}")
    match_list = []
    if(team):
        team_mapping = json.loads(team['object'])
        response = response_classes.TeamResponse(**team_mapping)
        print(f"TEAM IN FIRESTORE {team}")
        matches = response.fixtures
        print(f"MATCHES IN FIRESTORE {matches}")
        # Loop in chunks of 10
        for i in range(0, len(matches), 20):
            chunk_matches = matches[i:i+20]  # Get a slice of 10 matches

            coroutines = [setUpMatch(match) for match in chunk_matches]
            processed_matches = await asyncio.gather(*coroutines)  # Run coroutines concurrently

    # Assuming setUpMatch returns processed match data
            match_list.extend(processed_matches)
    else:
        matches = await retrieve_matches_by_team(team_id)
        for i in range(0, len(matches), 20):
            chunk_matches = matches[i:i+20]  # Get a slice of 10 matches

            coroutines = [setUpMatchFromDB(match) for match in chunk_matches]
            # Assuming setUpMatch is asynchronous
            processed_matches = await asyncio.gather(*coroutines)  # Run
            match_list.extend(processed_matches)
    
    
    
    matches = []
    for match in match_list:
        try:
            match["team_id"] = team_id
            matches.append(match)
            
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