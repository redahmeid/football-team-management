from classes import Match, PlayerMatch
from config import app_config
import id_generator
from firebase_admin import auth
import db

# "CREATE TABLE Teams" \
#         "(ID varchar(255),"\
#         "Name varchar(255) NOT NULL,"\
#         "AgeGroup varchar(255) NOT NULL,"\
#         "Email varchar(255) NOT NULL,"\
#         "PRIMARY KEY (ID),"\
#         "FOREIGN KEY(Club_ID) references Clubs(ID))"

def save_team_fixture(match:Match):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "INSERT INTO Matches (ID,Opposition,HomeOrAway, Date,Length,Team_ID) VALUES (%s,%s,%s,%s,%s,%s)"

    # Data to be inserted
    id = id_generator.generate_random_number(5)
    data_to_insert = (id,match.opposition,match.homeOrAway,match.date,match.length,match.team_id)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
   
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return id

# "CREATE TABLE Teams" \
#         "(ID varchar(255),"\
#         "Name varchar(255) NOT NULL,"\
#         "AgeGroup varchar(255) NOT NULL,"\
#         "Email varchar(255) NOT NULL,"\
#         "PRIMARY KEY (ID),"\
#         "FOREIGN KEY(Club_ID) references Clubs(ID))"

def retrieve_fixture_team_size(match_id):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "select Team_Size, ID from Matches where ID=%s"

    # Data to be inserted
    id = id_generator.generate_random_number(5)
    data_to_insert = (match_id)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
    result = cursor.fetchone()
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return result["Team_Size"]

# "CREATE TABLE Matches_Planned_Squad" \
#         "(ID varchar(255),"\
#         "Match_ID varchar(255) NOT NULL,"\
#         "Player_ID varchar(255) NOT NULL,"\
#         "Start_Time_Minutes int,"\
#         "End_Time_Minutes int,"\
#         "Position varchar(255),"\
#         "PRIMARY KEY (ID),"\
#         "FOREIGN KEY(Match_ID) references Matches(ID))"\
#         "FOREIGN KEY(Player_ID) references Players(ID))"
def save_planned_match_squad(playerMatch:PlayerMatch):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "INSERT INTO Planned_Match_Day_Squad (ID,Match_ID,Player_ID, Start_Time_Minutes,End_Time_Minutes,Position) VALUES (%s,%s,%s,%s,%s,%s)"

    # Data to be inserted
    id = id_generator.generate_random_number(5)
    data_to_insert = (id,playerMatch.match_id,playerMatch.player_id,playerMatch.start_time_minutes,playerMatch.end_time_minutes,playerMatch.position)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
   
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return {"id":id}

def retrieve_planned_match_squad(matchId):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "SELECT * from Planned_Match_Day_Squad as plan  inner join Players on plan.Player_ID = Players.ID and plan.Match_ID=%s"
   

    # Execute the SQL query to insert data
    cursor.execute(insert_query, matchId)
    response = cursor.fetchall()
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return response

def retrieve_matches_by_team(team_id:str):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "select * from Matches as p inner join Teams as t on p.Team_ID = t.ID inner join Clubs as c on t.Club_ID = c.ID and p.TEAM_ID = %s order by p.Date asc" 

    # Execute the SQL query to insert data
    cursor.execute(insert_query,team_id)
    rows = cursor.fetchall()

     # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # club = Club(id=id,name=row)
    print(rows)
    return rows

def retrieve_match_by_id(id:str):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "select * from Matches where ID=%s" 

    # Execute the SQL query to insert data
    cursor.execute(insert_query,id)
    rows = cursor.fetchone()

     # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # club = Club(id=id,name=row)
    print(rows)
    return rows

def retrieve_next_match_by_team(team_id:str):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "select * from Matches as p where p.Team_ID = %s order by p.Date asc" 

    # Execute the SQL query to insert data
    cursor.execute(insert_query,team_id)
    rows = cursor.fetchone()

     # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # club = Club(id=id,name=row)
    print(rows)
    return rows
