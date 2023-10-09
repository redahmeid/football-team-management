
import create_database
import drop_database
import club_apis


def create_club(event, context):
    response = club_apis.create_club(event,context)
    return response

def create_db(event,context):
    drop_database.drop_database()
    create_database.create_database()

