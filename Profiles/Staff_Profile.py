import json
from Profiles.Profile import Profile

class Staff_Profile(Profile):
    """
    Represents a profile for students only.
    """
    def __init__(self, id, name, surname, password, role, client_student_id_dict, Request_ids = None):
        super().__init__(id,name,surname, password, role)
        client_student_id_dict = client_student_id_dict # For staff only
        Request_ids = Request_ids # For staff only
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "password": self.password,
            "role": self.role,
            "client_student_id_dict": self.client_student_id_dict,
            "Request_ids": self.Request_ids
        }
    
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