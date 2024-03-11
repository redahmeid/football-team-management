
import asyncio
from roles import Role
from users_data import retrieve_user_id_by_email,save_user
from roles_data import save_role
from classes import TeamUser
import sys
import team_season_data
from team_data import retrieve_users_by_team_id
from player_data import retrieve_players_by_team
import logging
import matches_data
import player_data
from cache_trigger import updateTeamCache, updateUserCache
from match_planning_backend import list_matches_by_team_backend
logger = logging.getLogger(__name__)
import json
import team_data
from timeit import timeit
from email_sender import send_email,send_email_with_template
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
from team_response_creator import convertTeamSeasonDataToTeamResponse,convertTeamSeasonDataToTeamSeaonOnlyResponse
from etag_manager import isEtaggged,deleteEtag,setEtag,getLatestObject


import asyncio
import response_classes

@timeit
async def addSingleUser(email,team_id):
    user_id = await retrieve_user_id_by_email(email)
    print(user_id)
    user = TeamUser(email=email,team_id=team_id,role=Role.coach)
    team = await team_data.retrieve_team_by_id(team_id)
    if(user_id):
        
        await save_role(user)
        template_data = {
            "team": team.name,
        }
        template_id = 'd-d953ef3608354d49bde38c7d7e3843fa'
        # await send_email_with_template(email,template_id,template_data)
    else:
        user_id = await save_user("",email,"")
        await save_role(user)
        template_data = {
            "team": team.name,
        }
        template_id = 'd-9ba5fab4e96a4a56819aeba57916356f'
        # await send_email_with_template(email,template_id,template_data)
        
    
    return user





@timeit
async def retrieveTeamResponse(team) -> response_classes.TeamResponse:
    
    emails,players,team_seasons,matches,wins,defeats,draws = await asyncio.gather(
        
        retrieve_users_by_team_id(team.id),
        retrieve_players_by_team(team.id),
        team_season_data.retrieve_seasons_by_team_id(team.team_id),
        list_matches_by_team_backend(team.id),
        matches_data.wins_by_team(team.id),
        matches_data.defeats_by_team(team.id),
        matches_data.draws_by_team(team.id),
        
    )
    
    logger.info(f"PLAYERS {players}")
    seasons = []
    logger.info(f"TEAM SEASONS {team_seasons}")
    print(f"WINS FROM TEAM RESPONSE {wins}")
    print(f"DEFEATS FROM TEAM RESPONSE {defeats}")
    print(f"DRAWS FROM TEAM RESPONSE {draws}")
    for team_season in team_seasons:
        logger.info(team_season)
        season = await convertTeamSeasonDataToTeamSeaonOnlyResponse(team_season,wins,defeats,draws)
        seasons.append(season)
    logger.info(f"SEASONS {seasons}")
    team.seasons = seasons
    team.wins = wins
    team.defeats = defeats
    team.draws = draws
    team.squad = players[0]["players"]
    team.coaches = emails
    team.fixtures = matches
    return team

@timeit
async def getTeamFromDB(team_id):
    cached_object = await getLatestObject(team_id,'teams')
    teams = []
    if(cached_object):
       etag = cached_object["etag"]
       team_response = json.loads(cached_object["object"])
       team_object = response_classes.TeamResponse(**team_response)
    else:
        team = await team_data.retrieve_team_by_id(team_id)
        team_object = await retrieveTeamResponse(team)
        team_response = team_object.model_dump()
        
        etag = await setEtag(team_id,'teams',team_response)
    
    print("RESPONSE FROM getTeamFromDB")
    print(team_object)
    
    # get the user
    
    return team_object


@timeit
async def deleteTeam(team_id):
    await team_season_data.delete_team_season(team_id)
    await deleteEtag(team_id,'teams')
    

async def main():
    print("main 1")
    if(sys.argv[1]=="addUser"):
        print("main")
        response = await addSingleUser(sys.argv[2],sys.argv[3])
        print(response)



if __name__ == "__main__":
    asyncio.run(main())