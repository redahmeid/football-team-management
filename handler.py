
import create_database
import drop_database
import club_apis
import admins_apis
import team_apis
import player_apis
import matches_apis


def create_club(event, context):
    response = club_apis.create_club(event,context)
    return response

def create_club_admin(event, context):
    response = admins_apis.create_club_admin(event,context)
    return response
def create_team_admin(event, context):
    response = admins_apis.create_team_admin(event,context)
    return response

def create_team(event, context):
    response = team_apis.create_team(event,context)
    return response

def create_team_players(event, context):
    response = player_apis.create_players(event,context)
    return response
def create_team_player(event, context):
    response = player_apis.create_player(event,context)
    return response

def create_team_fixtures(event, context):
    response = matches_apis.create_fixtures(event,context)
    return response

def plan_day_match_day_squad(event, context):
    response = matches_apis.plan_match_squad(event,context)
    return response

def retrieve_planned_match_squad(event, context):
    response = matches_apis.show_planned_match_day_squad(event,context)
    return response
def list_players_by_team(event, context):
    response = player_apis.list_players_by_team(event,context)
    return response
def list_teams_by_club(event, context):
    response = team_apis.list_teams_by_club(event,context)
    return response

def list_matches_by_team(event,context):
    response = matches_apis.list_matches_by_team(event,context)
    return response
def retrieve_team_summary(event,context):
    response = team_apis.retrieve_team_summary(event,context)
    return response
def delete_player(event,context):
    response = player_apis.delete_player_from_team(event,context)
    return response
def retrieve_club_summary(event,context):
    response = club_apis.retrieve_club_summary(event,context)
    return response
def retrieve_next_match_by_team(event,context):
    response = matches_apis.next_match_by_team(event,context)
    return response

def create_db(event,context):
    # drop_database.drop_database()
    create_database.create_database()

def create_teams_table(event,context):
    # drop_database.drop_database()
    create_database.create_teams_table()

def create_admins_table(event,context):
    # drop_database.drop_database()
    create_database.create_admins_table()

def create_clubs_table(event,context):
    # drop_database.drop_database()
    create_database.create_clubs_table()

def create_players_table(event,context):
    # drop_database.drop_database()
    create_database.create_players_table()

def create_matches_table(event,context):
    # drop_database.drop_database()
    create_database.create_matches_table()

def create_match_planned_squad_table(event,context):
    # drop_database.drop_database()
    create_database.create_planned_match_day_squad_table()

def drop_db(event,context):
    # drop_database.drop_database()
    drop_database.drop_database()

