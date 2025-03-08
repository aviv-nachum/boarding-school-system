import json
from Profiles.Profile import Profile

class Staff_Profile(Profile):
    """
    Represents a profile for students only.
    """
    def __init__(self, id, name, surname, password, role, students_list = [], pending_requests = []):
        super().__init__(id,name,surname, password, role)
        self.students_list = students_list # For staff only
        self.pending_requests = pending_requests # For staff only
    
    def to_dict(self):
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
        Create a Profile object from a dictionary.
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