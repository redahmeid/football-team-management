from classes import Club, Team
from config import app_config
import id_generator
import db

# "CREATE TABLE Teams" \
#         "(ID varchar(255),"\
#         "Name varchar(255) NOT NULL,"\
#         "AgeGroup varchar(255) NOT NULL,"\
#         "Email varchar(255) NOT NULL,"\
#         "PRIMARY KEY (ID),"\
#         "FOREIGN KEY(Club_ID) references Clubs(ID))"

def save_team(team:Team):
    print("IN SAVE TEAM ")
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "INSERT INTO Teams (ID,Name,AgeGroup, live) VALUES (%s,%s,%s,%s)"

    # Data to be inserted
    id = id_generator.generate_random_number(5)
    data_to_insert = (id,team.name,team.age_group,True)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
    row_count = cursor.rowcount
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("IN SAVE TEAM %s"%id)
    return id

def retrieve_teams_by_club(club_id:str):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "select * from Teams where Club_ID = %s" %(club_id)

    # Execute the SQL query to insert data
    cursor.execute(insert_query)
    row = cursor.fetchall()
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # club = Club(id=id,name=row)
    print(row)
    return row

def retrieve_teams_by_user_id(user_id:str):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "select * from Roles as r inner join Teams as t on r.Team_ID = t.ID and r.Email = %s" 

    # Execute the SQL query to insert data
    cursor.execute(insert_query,user_id)
   
    row = cursor.fetchall()
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # club = Club(id=id,name=row)
    print(row)
    return row

def does_userid_match_team(user_id:str,team_id:str):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = f"select * from Roles where Team_ID={team_id} and Email = '{user_id}'" 

    # Execute the SQL query to insert data
    cursor.execute(insert_query)
   
    row = cursor.rowcount
    print("###################ROWS %s################"%row)
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # club = Club(id=id,name=row)
    if(row>0):
        return True
    else:
        return False

def retrieve_team_by_id(team_id:str):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "select * from Teams where id=%s" 

    # Execute the SQL query to insert data
    cursor.execute(insert_query,team_id)
    row = cursor.fetchone()
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # club = Club(id=id,name=row)
    print(row)
    return row



if __name__ == "__main__":
    retrieve_teams_by_club("53805")
    # retrieve_player("29308")