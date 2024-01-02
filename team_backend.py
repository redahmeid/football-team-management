
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
import team_data
from email_sender import send_email,send_email_with_template
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
from team_response_creator import convertTeamSeasonDataToTeamResponse,convertTeamSeasonDataToTeamSeaonOnlyResponse

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
        await send_email_with_template(email,template_id,template_data)
    else:
        user_id = await save_user("",email,"")
        await save_role(user)
        template_data = {
            "team": team.name,
        }
        template_id = 'd-9ba5fab4e96a4a56819aeba57916356f'
        await send_email_with_template(email,template_id,template_data)
        
    
    return user

async def retrieveTeamResponse(team):
    
    emails,players,team_seasons,matches = await asyncio.gather(
        
        retrieve_users_by_team_id(team.id),
        retrieve_players_by_team(team.id),
        team_season_data.retrieve_seasons_by_team_id(team.team_id),
        list_matches_by_team_backend(team.id),
    )
    
    logger.info(f"PLAYERS {players}")
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
