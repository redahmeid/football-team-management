from classes import Club, Team, User, TeamUser
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

def save_role(user:TeamUser):
    print("IN SAVE ROLE")
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "INSERT INTO Roles (ID,User_ID,Team_ID,Role,live) VALUES (%s,%s,%s,%s,%s)"

    # Data to be inserted
    id = id_generator.generate_random_number(5)
    data_to_insert = (id,user.user_id,user.team_id,user.role.value,True)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
    row_count = cursor.rowcount
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return id

def retrieve_role_by_user_id_and_team_id(user_id,team_id):
    print("IN RETRIEVE ROLE")
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "select * from Roles where User_ID=%s and Team_ID=%s"

    data_to_insert = (user_id,team_id)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
    data = cursor.fetchall()
    print(data)
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return data

