import json
from Profiles.Profile import Profile

class Student_Profile(Profile):
    """
    Represents a profile for students only.
    """
    def __init__(self, id, name, surname, grade, class_number, head_teacher_id, head_madric_id):
        super().__init__(id,name,surname)
        self.grade = grade  # For students only
        self.class_number = class_number  # For students only
        self.head_teacher_id = head_teacher_id  # For students only
        self.head_madric_id = head_madric_id  # For students only
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "grade": self.grade,
            "class_number": self.class_number,
            "head_teacher_id": self.head_teacher_id,
            "head_madric_id": self.head_madric_id
        }
    
    def from_dict(data):
        """
        Create a Profile object from a dictionary.
        """
        return Student_Profile(
            id=data['id'],
            name=data['name'],
            surname=data['surname'],
            grade=data.get('grade'),
            class_number=data.get('class_number'),
            head_teacher_id=data.get('head_teacher_id'),
            head_madric_id=data.get('head_madric_id')
        )