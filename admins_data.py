from classes import ClubAdministrator, TeamAdministrator
from config import app_config
import id_generator
import db

# # "(ID varchar(255),"\
#         "Name varchar(255) NOT NULL,"\
#         "Email varchar(255) NOT NULL,"\
#         "Phone varchar(255),"\
#         "Club_ID varchar(255),"\
#         "Team_ID varchar(255),"\
#         "PRIMARY KEY (ID),"\
#         "FOREIGN KEY(Club_ID) references Clubs(ID))"

def save_club_admin(admin:ClubAdministrator):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "INSERT INTO Admins (ID,Name,Email, Club_ID,Role) VALUES (%s,%s,%s,%s,%s)"

    # Data to be inserted
    id = "CLUB-%s%s" %(admin.club_id,id_generator.generate_random_number(5))
    data_to_insert = (id,admin.name,admin.email,admin.club_id,admin.role)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
    row_count = cursor.rowcount
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return (row_count,id)


def save_team_admin(admin:TeamAdministrator):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "INSERT INTO Admins (ID,Name,Email, Team_ID,,Role) VALUES (%s,%s,%s,%s,%s)"

    # Data to be inserted
    id = id_generator.generate_random_number(5)
    data_to_insert = (id,admin.name,admin.email,admin.team_id,admin.role)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
    row_count = cursor.rowcount
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return (row_count,id)

