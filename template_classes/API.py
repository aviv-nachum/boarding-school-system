from db_manager import get_user, store_in_DB, remove_from_DB
from Clients.User import User

class API:
    def __init__(self):
        pass

    def sign_up(self, username, password):
        user = User(username=username, password=password, role="guest", profile=None)
        store_in_DB(user)

    def get_user(self, username):
        return get_user(username)

    def delete_user(self, user):
        remove_from_DB(user.username)

    def check_password(self, user, password):
        return user.check_password(password)

    def check_name(self, user):
        return user.username