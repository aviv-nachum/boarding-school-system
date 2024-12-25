import json

class Profile: # TODO: make profile the father class and have staff_profile and student_profile inherit from it
    """
    Represents a profile for staff members and students.
    """
    def __init__(self, id, name, surname):
        self.id = id
        self.name = name
        self.surname = surname


    def to_dict(self):
        """
        Convert the Profile object to a dictionary.
        """
        return self.__dict__

    @staticmethod
    def from_dict(data):
        """
        Create a Profile object from a dictionary.
        """
        return Profile(
            id=data['id'],
            name=data['name'],
            surname=data['surname']
        )

    @staticmethod
    def encode(profile):
        """
        Serialize a Profile object to JSON.
        """
        return json.dumps(profile.to_dict()).encode('utf-8')

    @staticmethod
    def decode(data):
        """
        Deserialize JSON data into a Profile object.
        """
        return Profile.from_dict(json.loads(data.decode('utf-8')))
