
import asyncio
from roles import Role
from users_data import retrieve_user_id_by_email,save_user
from roles_data import save_role
from classes import TeamUser,Team
import sys
import team_season_data
from team_data import retrieve_teams_by_user_id,retrieve_users_by_team_id
from player_data import retrieve_players_by_team
from match_planning_backend import list_matches_by_team_backend

from team_response_creator import convertTeamSeasonDataToTeamResponse

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

async def retrieveTeamResponse(team:Team):
    team_response = convertTeamSeasonDataToTeamResponse(team)
    emails = await retrieve_users_by_team_id(team_response.id)
    players = await retrieve_players_by_team(team_response.id)
    team_seasons = await team_season_data.retrieve_seasons_by_team_id(team_response.id)
    seasons = []
    for team_season in team_seasons:
        seasons.append(convertTeamSeasonDataToTeamResponse(team_season))
    team_response.seasons = seasons
    team_response.squad = players[0]["players"]
    team_response.coaches = emails
    matches = await list_matches_by_team_backend(team_response.id)
    team_response.fixtures = matches
    return team_response

async def main():
    print("main 1")
    if(sys.argv[1]=="addUser"):
        print("main")
        response = await addSingleUser(sys.argv[2],sys.argv[3])
        print(response)



if __name__ == "__main__":
    asyncio.run(main())
