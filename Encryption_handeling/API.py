"""
Defines the API class for interacting with the database and managing user operations.
"""

from db_manager import get_user, store_in_DB, remove_from_DB, get_user_by_id, get_approved_requests_by_approver
from Clients.User import User

class API:
    """
    Provides methods for user management and database interactions.
    """
    def __init__(self):
        """
        Initializes the API object.
        """
        pass

    def sign_up(self, username, password, role, profile):
        """
        Handles user signup by storing the user in the database.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.
            role (str): The role of the user (e.g., "student", "staff").
            profile (Profile): The profile object associated with the user.
        """
        user = User(username=username, password=password, role=role, profile=profile)
        store_in_DB(user)

    def get_user(self, username):
        """
        Retrieves a user from the database by username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User: The user object if found, otherwise None.
        """
        return get_user(username)
    
    def get_user_by_id(self, id):
        """
        Retrieves a user from the database by ID.

        Args:
            id (str): The ID of the user to retrieve.

        Returns:
            User: The user object if found, otherwise None.
        """
        return get_user_by_id(id)

    def delete_user(self, username):
        """
        Deletes a user from the database by username.

        Args:
            username (str): The username of the user to delete.
        """
        remove_from_DB(username)

    def check_password(self, user, password):
        """
        Checks if the provided password matches the user's password.

        Args:
            user (User): The user object.
            password (str): The password to check.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return user.check_password(password)

    def check_name(self, user):
        """
        Returns the username of the user.

        Args:
            user (User): The user object.

        Returns:
            str: The username of the user.
        """
        return user.username

    def get_approved_requests(self, approver_id):
        """
        Fetch all approved exit requests for a specific approver.

        Args:
            approver_id (str): The ID of the approver.

        Returns:
            list: A list of approved requests for the approver.
        """
        return get_approved_requests_by_approver(approver_id)