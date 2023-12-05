
import asyncio
from roles import Role
from users_data import retrieve_user_id_by_email,save_user
from roles_data import save_role
from classes import TeamUser
import sys


async def addSingleUser(email,team_id):
    user_id = await retrieve_user_id_by_email(email)
    print(user_id)
    if(user_id):
        user = TeamUser(user_id=email,team_id=team_id,role=Role.coach)
        await save_role(user)
        return user
    else:
        user_id = await save_user("",email)
        user = TeamUser(user_id=email,team_id=team_id,role=Role.coach)
        await save_role(user)
        return user

async def main():
    print("main 1")
    if(sys.argv[1]=="addUser"):
        print("main")
        response = await addSingleUser(sys.argv[2],sys.argv[3])
        print(response)

if __name__ == "__main__":
    asyncio.run(main())
