from time import sleep
from server import Server
from Clients.Student import Student
from Clients.Staff import Staff
from Profiles.Staff_Profile import Staff_Profile
from Profiles.Student_Profile import Student_Profile
from threading import Thread
from db_manager import get_user, get_user_by_id

interval = 3

# Initialize and start the server
server = Server()
server.start()
sleep(1)

user_id = None  # To track the currently logged-in user
user = None  # To track whether the user is a Student or Staff

def register_student():
    """Register a new student."""
    global user
    print("\n--- Register as Student ---")
    id = input("Enter your ID: ").strip()
    name = input("Enter your name: ").strip()
    surname = input("Enter your surname: ").strip()
    grade = input("Enter your grade: ").strip()
    class_number = int(input("Enter your class number: ").strip())
    head_teacher_id = int(input("Enter your head teacher ID: ").strip())
    head_madric_id = int(input("Enter your head madrich ID: ").strip())
    password = input("Enter your password: ").strip()

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

    user = Student(name, password, profile)
    user.start()  # Ensure connection to the server

    sleep(1)

    user.register(profile)
    print("Student registered successfully.")
    student_menu()

def login_student():
    global user
    print("\n--- Log in as Student ---")
    name = input("Enter your name: ").strip()
    password = input("Enter your password: ").strip()
    user_data = get_user(name)
    if user_data and user_data.role == "student":
        user = Student(name, password, user_data.profile)
        user.start()
        sleep(1)
        user.login(user_data.profile.id)
        student_menu()
    else:
        print("Invalid Student ID or user is not a student.")

def register_staff():
    global user
    print("\n--- Register as Staff ---")
    staff_id = input("Enter your ID: ").strip()
    name = input("Enter your name: ").strip()
    surname = input("Enter your surname: ").strip()
    password = input("Enter your password: ").strip()
    #client_student_id_dict = input("Enter the client student ID dictionary: ").strip()
    #Request_ids = input("Enter the request IDs: ").strip()

    profile = Staff_Profile(
        id=staff_id,
        name=name,
        surname=surname,
        password=password,
        role="staff"
    )

    user = Staff(name, password, profile)
    user.start()
    sleep(1)
    user.register(profile)
    print("Staff registered successfully.")
    staff_menu()

def login_staff():
    global user
    print("\n--- Log in as Staff ---")
    name = input("Enter your name: ").strip()
    password = input("Enter your password: ").strip()
    user_data = get_user(name)
    if user_data and user_data.role == "staff":
        user = Staff(name, password, user_data.profile)
        user.start()
        sleep(1)
        user.login(user_data.profile.id)
        staff_menu()
    else:
        print("Invalid Staff ID or user is not a staff member.")

def student_menu():
    while True:
        print("\n--- Student Menu ---")
        print("1. Submit Request")
        print("2. Logout")
        choice = input("Choose an option: ").strip()

        if choice == '1':
            submit_request()
        elif choice == '2':
            user.logout()
            main_menu()
        else:
            print("Invalid choice. Please try again.")

def submit_request():
    content = input("Enter your request content: ").strip()
    approver_id = input("Enter the approver ID: ").strip()
    user.submit_request(content, approver_id)
    student_menu()

def staff_menu():
    """Display the staff menu."""
    global user_id, user
    while True:
        print("\n--- Staff Menu ---")
        print("1. Log out")
        print("2. View exit requests")
        print("3. View approved exit requests")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            user.logout()
            user_id = None
            main_menu()
        elif choice == "2":
            user.view_requests()
            request_id = int(input("Enter the request ID to approve: ").strip())
            user.approve_request(request_id=request_id)
        elif choice == "3":
            user.view_approved_requests()
        else:
            print("Invalid option. Please try again.")

def main_menu():
    while True:
        print("\n--- Main Menu ---")
        print("1. Log in as Student")
        print("2. Log in as Staff")
        print("3. Register as Student")
        print("4. Register as Staff")
        print("5. Exit")
        choice = input("Choose an option: ").strip()

        if choice == '1':
            login_student()
        elif choice == '2':
            login_staff()
        elif choice == '3':
            register_student()
        elif choice == '4':
            register_staff()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
