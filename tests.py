import asyncio
import team_data
import team_season_data
from classes import Club, Team,UpdateTeam,TeamUser,Player
import roles
import roles_data
import team_data
import create_database
import config
import user_homepage_backend
import team_response_creator
import team_backend
import match_planning_backend
import response_classes
import api_helper
import users_data
import player_data
import player_responses
import player_backend
import matches_data

players = ['Musa','Charlie','Luke','Teddy','Ajeet','Aaron','Zora','Taylor']
if __name__ == "__main__":
    
    asyncio.run(create_database.drop_database())
    asyncio.run(create_database.create_database())
    asyncio.run(users_data.save_user('12345','r.hmeid+dev@gmail.com','Reda Hmeid'))
    team = Team(age_group='u12',name="MUFCJ Reds")
    id = asyncio.run(team_data.save_team(team))
    asyncio.run(team_season_data.retrieve_seasons_by_team_id(id))
    season_id = asyncio.run(team_season_data.save_team_season(id,"23/24",'u12'))
    asyncio.run(team_season_data.retrieve_seasons_by_team_id(id))
    teamUser = TeamUser(email='r.hmeid+dev@gmail.com',team_id=str(season_id),role=roles.Role.admin)
    role_id = asyncio.run(roles_data.save_role(teamUser))
    asyncio.run(team_data.retrieve_teams_by_user_id('r.hmeid+dev@gmail.com'))
    # user_teams = asyncio.run(user_homepage_backend.setupHomepage("r.hmeid+dev@gmail.com"))
    # results = []
    # result = None
    # for user_team in user_teams:
    #     team = asyncio.run(team_data.retrieve_team_by_id(user_team["id"]))
    #     team_response = asyncio.run(team_backend.retrieveTeamResponse(team))
    #     match = {"id":"","opposition":"Ascot","homeOrAway":"Home","date":"2023-12-08","length":60,"type":response_classes.MatchType.league.value}
    #     print("###############################TEST CREATE MATCH#############################################")
    #     result = asyncio.run(match_planning_backend.create_match_backend(match,team_response.id))
    #     print("###############################TEST CREATE MATCH RESULT#############################################")
    #     print(result)
    #     results.append(result.model_dump())
    # print(api_helper.make_api_response(200,results))
    # print(asyncio.run(team_data.retrieve_users_by_team_id(teamUser.team_id)))
    # for player in players:
    #     print(asyncio.run(player_backend.create_players(player,str(season_id))))
    # print("###############################TEST RETRIEVE PLAYERS BY TEAM#############################################")
    # print(asyncio.run(player_data.retrieve_players_by_team(season_id)))
    # print("###############################GET THE MATCH READY FOR PLANNING#############################################")
    # print(asyncio.run(match_planning_backend.getMatchParent(season_id,result.match.id)))

    # print("###############################GET THE MATCH CREATED FOR PLANNING#############################################")
    
    # print(asyncio.run(match_planning_backend.getMatchCreated(season_id,result.match)))

    # print("###############################GET THE MATCH PLANNING FOR PLANNING#############################################")
    
    # print(asyncio.run(match_planning_backend.getMatchPlanning(season_id,result.match)))

    # print("###############################GET THE MATCH PLANNING FOR CONFIRMED#############################################")
    
    # print(asyncio.run(match_planning_backend.getMatchConfirmedPlanReadyToStart(season_id,result.match)))
    
    # print("###############################GET THE MATCH PSTARTED#############################################")
    
    # print(asyncio.run(match_planning_backend.getMatchStarted(season_id,result.match)))
    asyncio.run(user_homepage_backend.setupHomepage("r.hmeid+dev@gmail.com"))