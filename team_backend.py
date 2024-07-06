
import asyncio
from roles import Role
from users_data import retrieve_user_id_by_email,save_user
from roles_data import save_role
import classes
import sys
import team_season_data
from team_data import retrieve_users_by_team_id
from player_data import retrieve_players_by_team_with_stats
import logging
import matches_data
import player_data
from cache_trigger import updateTeamCache, updateUserCache
from match_planning_backend import list_matches_by_team_backend
logger = logging.getLogger(__name__)
import json
import team_data
from fcatimer import fcatimer
from email_sender import send_email,send_email_with_template
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
from team_response_creator import convertTeamSeasonDataToTeamResponse,convertTeamSeasonDataToTeamSeaonOnlyResponse
from etag_manager import isEtaggged,deleteEtag,setEtag,getLatestObject,updateDocument,getObject,whereEqual,getAllObjects,whereContains


import asyncio

@fcatimer
async def addTeamToUser(emails,team_id):
    for email in emails:
            fs_user = await getObject(email,'users_store')
            
            if(fs_user):
                fs_user_dict = fs_user.get().to_dict()
                user = classes.User(**fs_user_dict)
                user.teams.append(team_id)
                user.admin.append(team_id)
                fs_user.update(user.model_dump())
            else:
                await updateDocument('users_store',email,classes.User(email=email,teams=[team_id],admin=[team_id]))
@fcatimer
async def addUserToTeam(emails,team_id,role):
    results = []
    for email in emails:
        fs_team = await getObject(team_id,'teams_store')
        if(fs_team):
            fs_team_dict = fs_team.get().to_dict()
            team = classes.Team(**fs_team_dict)
            team.coaches.append(classes.TeamUser(email=email,role=role))

            fs_team.update(team.model_dump())
        user = classes.TeamUser(email=email,role=Role.coach)
        
        results.append(user.model_dump())
    return {'team_name':fs_team_dict['name'],'results':results}


# @fcatimer
# async def addSingleUser(email,team_id):
#     user_id = await retrieve_user_id_by_email(email)
#     print(user_id)
#     user = TeamUser(email=email,team_id=team_id,role=Role.coach)
#     team = await team_data.retrieve_team_by_id(team_id)
#     if(user_id):
        
#         await save_role(user)
#         template_data = {
#             "team": team.name,
#         }
#         template_id = 'd-d953ef3608354d49bde38c7d7e3843fa'
#         # await send_email_with_template(email,template_id,template_data)
#     else:
#         user_id = await save_user("",email,"")
#         await save_role(user)
#         template_data = {
#             "team": team.name,
#         }
#         template_id = 'd-9ba5fab4e96a4a56819aeba57916356f'
#         # await send_email_with_template(email,template_id,template_data)
        
    
#     return user

# @fcatimer
# async def save_to_store(team_seasons,team, wins, defeats, draws, emails,matches, players):
#     seasons = []
#     for team_season in team_seasons:
#         logger.info(team_season)
#         season = await convertTeamSeasonDataToTeamSeaonOnlyResponse(team_season,wins,defeats,draws)
#         seasons.append(season)
#     logger.info(f"SEASONS {seasons}")
#     team.seasons = seasons
#     team.wins = wins
#     team.defeats = defeats
#     team.draws = draws

#     [await updateDocument('players_store',player["info"]["id"],player) for player in players[0]["players"]]
    

#     player_ids = [player["info"]["id"] for player in players[0]["players"]]
#     team.squad = player_ids
#     coaches = [obj for obj in emails if (obj.role == "coach" or obj.role == "admin")]
#     team.coaches = coaches
#     guardians = [obj for obj in emails if (obj.role == "parent")]
#     team.guardians = guardians
#     match_ids = [match["match"]["id"] for match in matches]
#     team.fixtures = match_ids
#     await updateDocument('teams_store',team.id,team)

# @fcatimer
# async def retrieve_team_to_store(team) -> Team:
    
#     emails,players,team_seasons,matches,wins,defeats,draws = await asyncio.gather(
        
#         retrieve_users_by_team_id(team.id),
#         retrieve_players_by_team_with_stats(team.id),
#         team_season_data.retrieve_seasons_by_team_id(team.team_id),
#         list_matches_by_team_backend(team.id),
#         matches_data.wins_by_team(team.id),
#         matches_data.defeats_by_team(team.id),
#         matches_data.draws_by_team(team.id),
        
#     )
#     store_team = team
#     save_to_store(team_seasons,store_team,wins,defeats,draws,emails,matches,players)
#     logger.info(f"PLAYERS {players}")
#     seasons = []
#     logger.info(f"TEAM SEASONS {team_seasons}")
#     print(f"WINS FROM TEAM RESPONSE {wins}")
#     print(f"DEFEATS FROM TEAM RESPONSE {defeats}")
#     print(f"DRAWS FROM TEAM RESPONSE {draws}")
#     for team_season in team_seasons:
#         logger.info(team_season)
#         season = await convertTeamSeasonDataToTeamSeaonOnlyResponse(team_season,wins,defeats,draws)
#         seasons.append(season)
#     logger.info(f"SEASONS {seasons}")
#     team.seasons = seasons
#     team.wins = wins
#     team.defeats = defeats
#     team.draws = draws
#     team.squad = players[0]["players"]
#     team.coaches = emails
#     team.fixtures = matches
    
#     return team




@fcatimer
async def getTeamFromDB(team_id):
    fs_team = await getObject(team_id,'teams_store')
    if(fs_team):
        fs_team_dict = fs_team.get().to_dict()
        
        team = classes.Team(**fs_team_dict)
        fs_coaches = await whereContains('users_store','admin',team_id)
        print(f'FS_COACHES {fs_coaches}')
        coaches = []
        for fs_coach in fs_coaches:
            fs_team_coach = fs_coach.to_dict()
            coach = classes.User(**fs_team_coach)
            coaches.append(coach)
        team.coaches = coaches
        
        
        fs_matches = await whereEqual('matches_store','team_id',team_id)
        print(f'FS_MATCHES {fs_matches}')
        fixtures = []
        for fs_match in fs_matches:
            fs_match_dict = fs_match.to_dict()
            match = classes.MatchInfo(**fs_match_dict)
            fixtures.append(match)
        team.fixtures = fixtures
       
    
    
    print(f"RESPONSE FROM getTeamFromDB {team}")
    
    return team


@fcatimer
async def deleteTeam(team_id):
    await team_season_data.delete_team_season(team_id)
    await deleteEtag(team_id,'teams')
    

# async def main():
#     print("main 1")
#     if(sys.argv[1]=="addUser"):
#         print("main")
#         response = await addSingleUser(sys.argv[2],sys.argv[3])
#         print(response)



# if __name__ == "__main__":
#     asyncio.run(main())