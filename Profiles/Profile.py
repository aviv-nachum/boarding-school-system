import json

class Profile:
    """
    Represents a profile for staff members and students.
    """
    def __init__(self, id, name, surname, password, role):
        """
        Initializes a Profile object.

        Args:
            id (str): The unique ID of the profile.
            name (str): The first name of the user.
            surname (str): The last name of the user.
            password (str): The password for the profile.
            role (str): The role of the user (e.g., "student" or "staff").
        """
        self.id = id
        self.name = name
        self.surname = surname
        self.password = password
        self.role = role

    def to_dict(self):
        """
        Converts the Profile object to a dictionary.

        Returns:
            dict: A dictionary representation of the Profile object.
        """
        return self.__dict__

    @staticmethod
    def from_dict(data):
        """
        Creates a Profile object from a dictionary.

        Args:
            data (dict): A dictionary containing profile data.

        Returns:
            Profile: A Profile object created from the dictionary.
        """
        return Profile(
            id=data['id'],
            name=data['name'],
            surname=data['surname']
        )

    @staticmethod
    def encode(profile):
        """
        Serializes a Profile object to JSON.

        Args:
            profile (Profile): The Profile object to serialize.

        Returns:
            bytes: The JSON-encoded representation of the Profile object.
        """
        return json.dumps(profile.to_dict()).encode('utf-8')

    @staticmethod
    def decode(data):
        """
        Deserializes JSON data into a Profile object.

        Args:
            data (bytes): The JSON-encoded data.

        Returns:
            Profile: A Profile object created from the JSON data.
        """
        return Profile.from_dict(json.loads(data.decode('utf-8')))
