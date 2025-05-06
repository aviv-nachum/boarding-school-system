import json
from Profiles.Profile import Profile

class Staff_Profile(Profile):
    """
    Represents a profile for staff members only.
    """
    def __init__(self, id, name, surname, password, role, students_list=[], pending_requests=[]):
        """
        Initializes a Staff_Profile object.

        Args:
            id (str): The unique ID of the staff member.
            name (str): The first name of the staff member.
            surname (str): The last name of the staff member.
            password (str): The password for the staff's profile.
            role (str): The role of the user (should be "staff").
            students_list (list): A list of students assigned to the staff member.
            pending_requests (list): A list of pending requests for the staff member.
        """
        super().__init__(id, name, surname, password, role)
        self.students_list = students_list  # For staff only
        self.pending_requests = pending_requests  # For staff only

    def to_dict(self):
        """
        Converts the Staff_Profile object to a dictionary.

        Returns:
            dict: A dictionary representation of the Staff_Profile object.
        """
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "password": self.password,
            "role": self.role,
            "students_list": self.students_list,
            "pending_requests": self.pending_requests
        }

    def from_dict(data):
        """
        Creates a Staff_Profile object from a dictionary.

        Args:
            data (dict): A dictionary containing staff profile data.

        Returns:
            Staff_Profile: A Staff_Profile object created from the dictionary.
        """
        return Staff_Profile(
            id=data['id'],
            name=data['name'],
            surname=data['surname'],
            password=data['password'],
            role=data['role'],
            students_list=data.get('students_list'),
            pending_requests=data.get('pending_requests')
        )