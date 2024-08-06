
try:
  import unzip_requirements
except ImportError:
  pass

import team_apis
import player_apis
import matches_apis
import users_apis
import match_detail_screen
import asyncio
import user_homepage
import auth
import api_helper
import email_sender
import accounts
import caching_data
import notifications

def contact_us(event,context):
    response = asyncio.run(email_sender.contact_us(event,context))
    return response

def send_new_guardian_email(event,context):
    response = asyncio.run(player_apis.sendNewGuardianAnEmail(event,context))
    return response


def schedule_invitations(event,context):
    response = asyncio.run(users_apis.backgroundSendInvites(event,context))
    return response

def notify_match_update(event,context):
    response = asyncio.run(users_apis.notify_match_update(event,context))
    return response

def send_cancellation(event,context):
    response = asyncio.run(users_apis.send_cancellation_message(event,context))
    return response

def send_reminder(event,context):
    response = asyncio.run(users_apis.sendReminder(event,context))
    return response

def find_and_schedule_invitations(event,context):
    response = asyncio.run(users_apis.findAndSendInvites(event,context))
    return response


def send_invites(event,context):
    response = asyncio.run(users_apis.sendInvites(event,context))
    return response
def send_invite_response(event,context):
    response = asyncio.run(users_apis.sendInviteResponse(event,context))
    return response
def check_online(event,context):
    return api_helper.make_api_response(200,{})
def create_team(event, context):
    response = asyncio.run(team_apis.submit_team(event,context))
    return response
def subs_due(event, context):
    response = asyncio.run(match_detail_screen.subs_due(event,context))
    return response

def add_users_to_team(event,context):
    response = asyncio.run(team_apis.addUserToTeam(event,context))
    return response

def add_guardians_to_player(event,context):
    response = asyncio.run(player_apis.addGuardiansToPlayer(event,context))
    return response

def create_team_players(event, context):
    response = asyncio.run(player_apis.create_players(event,context))
    return response

def set_device_token(event,context):
    response = asyncio.run(auth.saveDeviceToken(event,context))
    return response
def turn_off_notifications(event,context):
    response = asyncio.run(auth.turnOffNotifications(event,context))
    return response
def turn_on_notifications(event,context):
    response = asyncio.run(auth.turnOffNotifications(event,context))
    return response
def set_device_token_by_match(event,context):
    response = asyncio.run(auth.saveDeviceTokenByMatch(event,context))
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

def update_invites(event, context):
    response = asyncio.run(match_detail_screen.update_invites(event,context))
    return response

def list_players_by_user(event, context):
    response = asyncio.run(player_apis.list_players_by_guardian(event,context))
    return response

def update_matches_from_cache(event,context):
    response = asyncio.run(matches_apis.updateFromCache(event,context))
    return response

def add_goal_scorers(event,context):
    response = asyncio.run(match_detail_screen.add_goal_scorers(event,context))
    return response

def get_match_planned_lineups(event,context):
    response = asyncio.run(matches_apis.retrieve_match_planned_lineups(event,context))
    return response

def get_match_actual_lineups(event,context):
    response = asyncio.run(matches_apis.retrieve_match_actual_lineups(event,context))
    return response

def retrieve_score(event,context):
    response = asyncio.run(match_detail_screen.retrieveScore(event,context))
    return response

def time_played(event,context):
    response = asyncio.run(matches_apis.time_played(event,context))
    return response

def get_match_current_lineup(event,context):
    response = asyncio.run(matches_apis.retrieve_match_current_lineup(event,context))
    return response

def getMatch(event,context):
    response = asyncio.run(matches_apis.retrieve_match_by_id(event,context))
    print(response)
    return response
def getMatchAsGuest(event,context):
    response = asyncio.run(match_detail_screen.getMatchAsGuest(event,context))
    print(response)
    return response
def set_captain(event,context):
    response = asyncio.run(match_detail_screen.set_captain(event,context))
    print(response)
    return response
def delete_user(event,context):
    response = asyncio.run(accounts.delete_account(event,context))
    print(response)
    return response

def cacher(event,context):
    asyncio.run(caching_data.handler(event,context))
def edit_match(event,context):
    response = asyncio.run(matches_apis.edit_match(event,context))
    return response
def sendNotification(event,context):
    asyncio.run(notifications.backgroundSendMatchUpdateNotification(event,context))   

def update_match_status(event,context):
    response = asyncio.run(match_detail_screen.update_match_status(event,context))
    return response
def submit_lineup(event,context):
    response = asyncio.run(match_detail_screen.submit_lineup(event,context))
    return response
def start_match(event,context):
    response = asyncio.run(match_detail_screen.start_match(event,context))
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
def delete_team(event,context):
    response = asyncio.run(team_apis.delete_team(event,context))
    return response
def delete_player(event,context):
    response = player_apis.delete_player_from_team(event,context)
    return response

def retrieve_next_match_by_team(event,context):
    response = asyncio.run(matches_apis.next_match_by_team(event,context))
    return response
def create_user(event,context):
    response = asyncio.run(users_apis.new_user(event,context))
    return response
def submit_team(event,context):
    response = asyncio.run(team_apis.submit_team(event,context))
    return response
def getUser(event,context):
    response = asyncio.run(user_homepage.enter_screen(event,context))
    return response
def getUserV2(event,context):
    response = asyncio.run(user_homepage.enter_screenV2(event,context))
    return response

