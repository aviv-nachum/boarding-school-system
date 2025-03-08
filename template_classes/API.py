from db_manager import get_user, store_in_DB, remove_from_DB, get_user_by_id
from Clients.User import User

class API:
    def __init__(self):
        pass

    def sign_up(self, username, password, role, profile):
        #print(f"Signing up user: {username}, role: {role}")
        user = User(username=username, password=password, role=role, profile=profile)
        store_in_DB(user)

    def get_user(self, username):
        #print(f"Getting user: {username}")
        return get_user(username)
    
    def get_user_by_id(self, id):
        return get_user_by_id(id)

    def delete_user(self, username):
        print(f"Deleting user: {username}")
        remove_from_DB(username)

    def check_password(self, user, password):
        return user.check_password(password)

    def check_name(self, user):
        return user.username