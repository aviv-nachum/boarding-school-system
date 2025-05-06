from Profiles.Profile import Profile

class Student_Profile(Profile):
    """
    Represents a profile for students only.
    """
    def __init__(self, id, name, surname, password, role, grade, class_number, head_teacher_id, head_madric_id):
        """
        Initializes a Student_Profile object.

        Args:
            id (str): The unique ID of the student.
            name (str): The first name of the student.
            surname (str): The last name of the student.
            password (str): The password for the student's profile.
            role (str): The role of the user (should be "student").
            grade (str): The grade of the student.
            class_number (str): The class number of the student.
            head_teacher_id (str): The ID of the student's head teacher.
            head_madric_id (str): The ID of the student's head matric.
        """
        super().__init__(id, name, surname, password, role)
        self.grade = grade  # For students only
        self.class_number = class_number  # For students only
        self.head_teacher_id = head_teacher_id  # For students only
        self.head_madric_id = head_madric_id  # For students only

    def to_dict(self):
        """
        Converts the Student_Profile object to a dictionary.

        Returns:
            dict: A dictionary representation of the Student_Profile object.
        """
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "password": self.password,
            "role": self.role,
            "grade": self.grade,
            "class_number": self.class_number,
            "head_teacher_id": self.head_teacher_id,
            "head_madric_id": self.head_madric_id
        }

    def from_dict(data):
        """
        Creates a Student_Profile object from a dictionary.

        Args:
            data (dict): A dictionary containing student profile data.

        Returns:
            Student_Profile: A Student_Profile object created from the dictionary.
        """
        return Student_Profile(
            id=data['id'],
            name=data['name'],
            surname=data['surname'],
            password=data['password'],
            role=data['role'],
            grade=data.get('grade'),
            class_number=data.get('class_number'),
            head_teacher_id=data.get('head_teacher_id'),
            head_madric_id=data.get('head_madric_id')
        )