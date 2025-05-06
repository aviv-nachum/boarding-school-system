"""
GUI class for handling user interaction in the boarding school system.
Provides menus for students and staff.
"""

from time import sleep
from Clients.Student import Student
from Clients.Staff import Staff
from Profiles.Staff_Profile import Staff_Profile
from Profiles.Student_Profile import Student_Profile
from db_manager import get_user

class GUI:
    """
    Handles the user interface for the boarding school system.
    """
    def __init__(self):
        self.user = None  # Tracks the currently logged-in user

    def register_student(self):
        """Register a new student."""
        print("\n--- Register as Student ---")
        id = input("Enter your ID: ").strip()
        name = input("Enter your name: ").strip()
        surname = input("Enter your surname: ").strip()
        grade = input("Enter your grade: ").strip()
        class_number = int(input("Enter your class number: ").strip())
        head_teacher_id = int(input("Enter your head teacher ID: ").strip())
        head_madric_id = int(input("Enter your head madrich ID: ").strip())
        password = input("Enter your password: ").strip()

        # Create a student profile
        profile = Student_Profile(
            id=id,
            name=name,
            surname=surname,
            grade=grade,
            class_number=class_number,
            head_teacher_id=head_teacher_id,
            head_madric_id=head_madric_id,
            password=password,
            role="student"
        )

        # Initialize the student and register them
        self.user = Student(name, password, profile)
        self.user.start()
        sleep(1)
        self.user.register(profile)
        print("Student registered successfully.")
        self.main_menu()

    def login_student(self):
        """Log in as a student."""
        print("\n--- Log in as Student ---")
        name = input("Enter your name: ").strip()
        password = input("Enter your password: ").strip()

        # Retrieve user data from the database
        user_data = get_user(name)
        if user_data and user_data.role == "student" and user_data.password == password:
            self.user = Student(name, password, user_data.profile)
            self.user.start()  # Ensure the handshake is completed
            sleep(1)
            self.user.login(user_data.profile.id)
            self.student_menu()
        else:
            print("Invalid username or password.")
            self.main_menu()

    def register_staff(self):
        """Register a new staff member."""
        print("\n--- Register as Staff ---")
        staff_id = input("Enter your ID: ").strip()
        name = input("Enter your name: ").strip()
        surname = input("Enter your surname: ").strip()
        password = input("Enter your password: ").strip()

        # Create a staff profile
        profile = Staff_Profile(
            id=staff_id,
            name=name,
            surname=surname,
            password=password,
            role="staff"
        )

        # Initialize the staff member and register them
        self.user = Staff(name, password, profile)
        self.user.start()
        sleep(1)
        self.user.register(profile)
        print("Staff registered successfully.")
        self.main_menu()

    def login_staff(self):
        """Log in as a staff member."""
        print("\n--- Log in as Staff ---")
        name = input("Enter your name: ").strip()
        password = input("Enter your password: ").strip()

        # Retrieve user data from the database
        user_data = get_user(name)
        if user_data and user_data.role == "staff" and user_data.password == password:
            self.user = Staff(name, password, user_data.profile)
            self.user.start()
            sleep(1)
            self.user.login(user_data.profile.id)
            self.staff_menu()
        else:
            print("Invalid username or password.")
            self.main_menu()

    def student_menu(self):
        """Display the student menu."""
        while True:
            print("\n--- Student Menu ---")
            print("1. Submit Request")
            print("2. Logout")
            choice = input("Choose an option: ").strip()

            if choice == '1':
                self.submit_request()
            elif choice == '2':
                self.user.logout()
                self.main_menu()
            else:
                print("Invalid choice. Please try again.")

    def submit_request(self):
        """Submit a new exit request."""
        content = input("Enter your request content: ").strip()
        approver_id = input("Enter the approver ID: ").strip()

        # Submit the request through the student object
        self.user.submit_request(content, approver_id)
        print("Request submitted successfully.")
        self.student_menu()

    def staff_menu(self):
        """Display the staff menu."""
        while True:
            print("\n--- Staff Menu ---")
            print("1. Log out")
            print("2. View exit requests")
            print("3. View approved exit requests")
            choice = input("Choose an option: ").strip()

            if choice == "1":
                self.user.logout()
                self.main_menu()
            elif choice == "2":
                self.user.view_requests()
                request_id = input("Enter the request ID to approve (or press Enter to skip): ").strip()
                if request_id:
                    self.user.approve_request(request_id=int(request_id))
            elif choice == "3":
                self.user.view_approved_requests()
            else:
                print("Invalid option. Please try again.")

    def main_menu(self):
        """Display the main menu."""
        while True:
            print("\n--- Main Menu ---")
            print("1. Log in as Student")
            print("2. Log in as Staff")
            print("3. Register as Student")
            print("4. Register as Staff")
            print("5. Exit")
            choice = input("Choose an option: ").strip()

            if choice == '1':
                self.login_student()
            elif choice == '2':
                self.login_staff()
            elif choice == '3':
                self.register_student()
            elif choice == '4':
                self.register_staff()
            elif choice == '5':
                print("Exiting the system. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")