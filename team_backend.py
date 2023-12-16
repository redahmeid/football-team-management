
import asyncio
from roles import Role
from users_data import retrieve_user_id_by_email,save_user
from roles_data import save_role
from classes import TeamUser,Team
import sys
import team_season_data
from team_data import retrieve_teams_by_user_id,retrieve_users_by_team_id
from player_data import retrieve_players_by_team
import logging
from match_planning_backend import list_matches_by_team_backend
logger = logging.getLogger(__name__)
import functools
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
from team_response_creator import convertTeamSeasonDataToTeamResponse,convertTeamSeasonDataToTeamSeaonOnlyResponse

async def addSingleUser(email,team_id):
    user_id = await retrieve_user_id_by_email(email)
    print(user_id)
    if(user_id):
        user = TeamUser(email=email,team_id=team_id,role=Role.coach)
        await save_role(user)
        return user
    else:
        user_id = await save_user("",email,"")
        user = TeamUser(email=email,team_id=team_id,role=Role.coach)
        await save_role(user)

        return user

async def retrieveTeamResponse(team):
    
    emails = await retrieve_users_by_team_id(team.id)
    players = await retrieve_players_by_team(team.id)
    logger.info(f"PLAYERS {players}")
    team_seasons = await team_season_data.retrieve_seasons_by_team_id(team.team_id)
    seasons = []
    logger.info(f"TEAM SEASONS {team_seasons}")
    for team_season in team_seasons:
        logger.info(team_season)
        season = await convertTeamSeasonDataToTeamSeaonOnlyResponse(team_season,2)
        seasons.append(season)
    logger.info(f"SEASONS {seasons}")
    team.seasons = seasons
    team.squad = players[0]["players"]
    team.coaches = emails
    matches = await list_matches_by_team_backend(team.id)
    team.fixtures = matches
    return team

async def main():
    print("main 1")
    if(sys.argv[1]=="addUser"):
        print("main")
        response = await addSingleUser(sys.argv[2],sys.argv[3])
        print(response)



if __name__ == "__main__":
    asyncio.run(main())
