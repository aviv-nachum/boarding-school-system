import json

class Profile:
    """
    Represents a profile for staff members and students.
    """
    def __init__(self, id, name, surname, role, grade=None, class_number=None, head_teacher_id=None, head_madric_id=None):
        self.id = id
        self.name = name
        self.surname = surname
        self.role = role
        self.grade = grade  # For students only
        self.class_number = class_number  # For students only
        self.head_teacher_id = head_teacher_id  # For students only
        self.head_madric_id = head_madric_id  # For students only

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
            surname=data['surname'],
            role=data['role'],
            grade=data.get('grade'),
            class_number=data.get('class_number'),
            head_teacher_id=data.get('head_teacher_id'),
            head_madric_id=data.get('head_madric_id')
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
