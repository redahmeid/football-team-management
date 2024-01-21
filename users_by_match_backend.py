
import team_data
import matches_data


async def getStakeholders(match_id):
    matches = await matches_data.retrieve_match_by_id(match_id)

    match = matches[0]
    print(f"MATCH {match}")
    team_id = match.team.id
    print(f"TEAM ID {team_id}")
    admins = await team_data.retrieve_users_by_team_id(team_id)
    return admins