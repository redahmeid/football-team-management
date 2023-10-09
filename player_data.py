from classes import Club, Team,Player
from config import app_config
import id_generator
import db

# # "CREATE TABLE Players" \
#         "(ID varchar(255),"\
#         "Name varchar(255) NOT NULL,"\
#         "Team_ID varchar(255) NOT NULL,"\
#         "Email varchar(255),"\
#         "PRIMARY KEY (ID),"\
#         "FOREIGN KEY(Team_ID) references Teams(ID))"

def save_player(player:Player):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "INSERT INTO Players (ID,Name,Team_ID) VALUES (%s,%s,%s)"

    # Data to be inserted
    id = "TEAM-%s-%s" %(player.team_id,id_generator.generate_random_number(5))
    data_to_insert = (id,player.name,player.team_id)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
    row_count = cursor.rowcount
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return {"id":id,"name":player.name}

def retrieve_club(id:str):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "select * from Clubs where ID = %s" %(id)

    # Execute the SQL query to insert data
    cursor.execute(insert_query)
    row = cursor.fetchone()
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # club = Club(id=id,name=row)
    print(row)
    return row