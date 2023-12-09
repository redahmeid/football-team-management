
import asyncio

from team_data import retrieve_teams_by_user_id

from team_backend import retrieveTeamResponse

def custom_sort(item):
    return int(item["AgeGroup"][1:])

async def setupHomepage(email):
    teams_list = []
    teams = await retrieve_teams_by_user_id(email)
    teams.sort(key=custom_sort)
    for team in teams:
        
        team_response = await retrieveTeamResponse(team)
        teams_list.append(team_response.model_dump())
    return teams_list

if __name__ == "__main__":
    asyncio.run(setupHomepage("r.hmeid+dev@gmail.com"))