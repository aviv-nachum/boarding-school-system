from time import sleep
from server import Server
from Clients.Student import Student
from Clients.Staff import Staff
from Profiles.Staff_Profile import Staff_Profile
from Profiles.Student_Profile import Student_Profile
from threading import Thread

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

    user = Student(id, "password")  # Assuming password is set to "password" for simplicity
    user.start()  # Ensure connection to the server

    sleep(1)

    profile = Student_Profile(
        id=id,
        name=name,
        surname=surname,
        grade=grade,
        class_number=class_number,
        head_teacher_id=head_teacher_id,
        head_madric_id=head_madric_id
    )

    user.register(profile)
    print("Student registered successfully.")

def login_student():
    global user
    print("\n--- Log in as Student ---")
    student_id = input("Enter your Student ID: ").strip()
    user = Student(student_id, "password")  # Assuming password is set to "password" for simplicity
    user.start()
    sleep(1)
    user.login(student_id)
    student_menu()

def register_staff():
    global user
    print("\n--- Register as Staff ---")
    staff_id = input("Enter your ID: ").strip()
    name = input("Enter your name: ").strip()
    surname = input("Enter your surname: ").strip()
    position = input("Enter your position: ").strip()

    profile = Staff_Profile(
        id=staff_id,
        name=name,
        surname=surname,
        position=position
    )

    user = Staff(staff_id, "password")  # Assuming password is set to "password" for simplicity
    user.start()
    sleep(1)
    user.register(profile)
    print("Staff registered successfully.")

def login_staff():
    global user
    print("\n--- Log in as Staff ---")
    staff_id = input("Enter your Staff ID: ").strip()
    user = Staff(staff_id, "password")  # Assuming password is set to "password" for simplicity
    user.start()
    sleep(1)
    user.login(staff_id)
    staff_menu()

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
            break
        else:
            print("Invalid choice. Please try again.")

def submit_request():
    content = input("Enter your request content: ").strip()
    approver_id = input("Enter the approver ID: ").strip()
    user.submit_request(content, approver_id)

def staff_menu():
    """Display the staff menu."""
    global user_id, user
    while True:
        print("\n--- Staff Menu ---")
        print("1. Log out")
        print("2. View exit requests")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            user.logout()
            user_id = None
            break
        elif choice == "2":
            user.view_requests()
            request_id = int(input("Enter the request ID to approve: ").strip())
            user.approve_request(request_id=request_id)
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
    server_thread = Thread(target=server.run)
    server_thread.start()
    main_menu()
