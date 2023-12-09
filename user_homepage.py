import exceptions

from secrets_util import getEmailFromToken, lambda_handler
import api_helper

from user_homepage_backend import setupHomepage
def custom_sort(item):
    return int(item["AgeGroup"][1:])

async def enter_screen(event, context):
    lambda_handler(event,context)
    teams_list = []
    try:
        
        email =  getEmailFromToken(event,context)
        teams_list = await setupHomepage(email)
        response = api_helper.make_api_response(200,teams_list)
        # get the user
        return response
    except exceptions.AuthError as e:
        response = api_helper.make_api_response(401,None,e)

