import json
from Profiles.Profile import Profile

class Staff_Profile(Profile):
    """
    Represents a profile for students only.
    """
    def __init__(self, id, name, surname, client_student_id_dict, Request_ids = None):
        super().__init__(id,name,surname)
        client_student_id_dict = client_student_id_dict # For staff only
        Request_ids = Request_ids # For staff only
    
    def from_dict(data):
        """
        Create a Profile object from a dictionary.
        """
        return Staff_Profile(
            id=data['id'],
            name=data['name'],
            surname=data['surname'],
            client_student_id_dict=data.get('client_student_id_dict'),
            Request_ids=data.get('Request_ids')
        )