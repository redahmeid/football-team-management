
import create_database
import drop_database
import club_apis
import team_apis
import player_apis
import matches_apis
import users_apis
import match_detail_screen
import asyncio
import user_homepage
import create_team_screen
import auth
import api_helper

def check_online(event,context):
    return api_helper.make_api_response(200,{})
def create_team(event, context):
    response = asyncio.run(team_apis.create_team(event,context))
    return response

def add_users_to_team(event,context):
    response = asyncio.run(team_apis.addUserToTeam(event,context))
    return response

def create_team_players(event, context):
    response = asyncio.run(player_apis.create_players(event,context))
    return response

def set_tokens(event,context):
    response = asyncio.run(auth.set_custom_claims(event,context))
    return response
def create_team_fixtures(event, context):
    response = asyncio.run(matches_apis.create_fixtures(event,context))
    return response

def list_players_by_team(event, context):
    response = asyncio.run(player_apis.list_players_by_team(event,context))
    return response

def getMatch(event,context):
    response = asyncio.run(match_detail_screen.getMatch(event,context))
    print(response)
    return response
def getMatchAsGuest(event,context):
    response = asyncio.run(match_detail_screen.getMatchAsGuest(event,context))
    print(response)
    return response

def update_match_status(event,context):
    response = asyncio.run(match_detail_screen.update_match_status(event,context))
    return response
def submit_lineup(event,context):
    response = asyncio.run(match_detail_screen.submit_lineup(event,context))
    return response
def submit_subs(event,context):
    response = asyncio.run(match_detail_screen.submit_substitutions(event,context))
    return response
def list_matches_by_team(event,context):
    response = asyncio.run(matches_apis.list_matches_by_team(event,context))
    return response
def retrieve_team_summary(event,context):
    response = asyncio.run(team_apis.retrieve_team_summary(event,context))
    return response
def delete_player(event,context):
    response = player_apis.delete_player_from_team(event,context)
    return response
def retrieve_club_summary(event,context):
    response = club_apis.retrieve_club_summary(event,context)
    return response
def retrieve_next_match_by_team(event,context):
    response = asyncio.run(matches_apis.next_match_by_team(event,context))
    return response
def create_user(event,context):
    response = asyncio.run(users_apis.new_user(event,context))
    return response
def submit_team(event,context):
    response = asyncio.run(create_team_screen.submit_team(event,context))
    return response
def getUser(event,context):
    response = asyncio.run(user_homepage.enter_screen(event,context))
    return response

