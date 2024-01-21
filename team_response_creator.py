import team_season_data
import response_classes
import logging
logger = logging.getLogger(__name__)
import functools
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
import functools
import time
import asyncio
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
@timeit
async def convertTeamSeasonDataToTeamResponse(team,order=0) -> response_classes.TeamResponse:
    logger.info(f"{order} TEAM {team}")
    id = team[f"{team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID}"]
    ageGroup = team[team_season_data.TABLE.TEAM_AGE_GROUP]
    season = team[team_season_data.TABLE.SEASON_NAME]
    season_id = team[f"{team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID}"]
    name = team["Name"]
    team_id = team[f"{team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.TEAM_ID}"]
    baseTeamUrl = f"/teams/{season_id}"
    self = response_classes.Link(link=baseTeamUrl,method="get")
    players = response_classes.Link(link="%s/players"%(baseTeamUrl),method="get")
    fixtures= response_classes.Link(link="%s/matches"%(baseTeamUrl),method="get")
    addPlayers = response_classes.Link(link="%s/players"%(baseTeamUrl),method="post")
    addFixtures = response_classes.Link(link="%s/matches"%(baseTeamUrl),method="post")
    nextMatch = response_classes.Link(link="%s/next_match"%(baseTeamUrl),method="get")

    response =  response_classes.TeamResponse(id=id,season=season, team_id=team_id,name=name, season_id=season_id,ageGroup=ageGroup,self=self,nextMatch=nextMatch,teamPlayers=players,teamFixtures=fixtures,addFixtures=addFixtures,addPlayers=addPlayers)
    logger.info(f"{order} Response {response}")
    return response
@timeit
async def convertTeamSeasonDataToTeamSeaonOnlyResponse(team,order=0) -> response_classes.TeamResponse:
    logger.info(f"{order} TEAM {team}")
    id = team[team_season_data.TABLE.ID]
    ageGroup = team[team_season_data.TABLE.TEAM_AGE_GROUP]
    season = team[team_season_data.TABLE.SEASON_NAME]
    season_id = team[team_season_data.TABLE.ID]
    
    team_id = team[team_season_data.TABLE.TEAM_ID]
    baseTeamUrl = f"/teams/{season_id}"
    self = response_classes.Link(link=baseTeamUrl,method="get")
    players = response_classes.Link(link="%s/players"%(baseTeamUrl),method="get")
    fixtures= response_classes.Link(link="%s/matches"%(baseTeamUrl),method="get")
    addPlayers = response_classes.Link(link="%s/players"%(baseTeamUrl),method="post")
    addFixtures = response_classes.Link(link="%s/matches"%(baseTeamUrl),method="post")
    nextMatch = response_classes.Link(link="%s/next_match"%(baseTeamUrl),method="get")

    response =  response_classes.TeamResponse(id=id,season=season, team_id=team_id, season_id=season_id,ageGroup=ageGroup,self=self,nextMatch=nextMatch,teamPlayers=players,teamFixtures=fixtures,addFixtures=addFixtures,addPlayers=addPlayers)
    logger.info(f"{order} Response {response}")
    return response