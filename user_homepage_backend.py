
import asyncio

from team_data import retrieve_teams_by_user_id

from team_backend import retrieveTeamResponse
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
def custom_sort(item):
    return int(item.ageGroup[1:])

async def setupHomepage(email):
    logger.info("START")
    teams_list = []
    teams = await retrieve_teams_by_user_id(email)
    
    if(isinstance(teams,list)):
        teams.sort(key=custom_sort)
        for team in teams:
            
            team_response = await retrieveTeamResponse(team)
            teams_list.append(team_response.model_dump())
    
    logger.info(teams_list)
    logger.info("END")
    return teams_list

if __name__ == "__main__":
    asyncio.run(setupHomepage("r.hmeid+dev@gmail.com"))