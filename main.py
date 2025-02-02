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

    # Create and start the client
    user = Student()
    user.start()  # Ensure connection to the server

    sleep(1)

    profile = Student_Profile(
        id=id,
        name=name,
        surname=surname,
        grade=grade,
        class_number=class_number,
        head_teacher_id=head_teacher_id,
        head_madric_id=head_madric_id,
    )

    user.register(profile)
    print("Student registered successfully.")

    user.login(id)
    if user.session_id:
        student_menu()


def register_staff():
    """Register a new staff member."""
    global user
    print("\n--- Register as Staff ---")
    id = input("Enter your ID: ").strip()
    name = input("Enter your name: ").strip()
    surname = input("Enter your surname: ").strip()

    # Create and start the client
    user = Staff()
    user.start()  # Ensure connection to the server

    sleep(1)

    profile = Staff_Profile(
        id=id,
        name=name,
        surname=surname,
        client_student_id_dict={},  # Start with no assigned students
    )

    user.register(profile)
    print("Staff registered successfully.")

    user.login(id)
    if user.session_id:
        staff_menu()


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


def login_student():
    global user
    print("\n--- Log in as Student ---")
    student_id = input("Enter your Student ID: ").strip()
    user = Student()
    user.start()
    sleep(1)
    user.login(student_id)
    if user.session_id:
        student_menu()

def login_staff():
    global user
    print("\n--- Log in as Staff ---")
    staff_id = input("Enter your Staff ID: ").strip()
    user = Staff()
    user.start()
    sleep(1)
    user.login(staff_id)
    if user.session_id:
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


if __name__ == "__main__":
    main_menu()

sleep(interval)

# Create and start student clients
student1 = Student()
student2 = Student()
student1.start()
student2.start()

sleep(interval)  # Allow clients to connect

# Student profiles with unique IDs
student1_profile = Student_Profile(
    id=101,
    name="Alice",
    surname="Chohen",
    grade="12",
    class_number=3,
    head_teacher_id=201,
    head_madric_id=301
)

student2_profile = Student_Profile(
    id=102,
    name="Aviad",
    surname="Gabay",
    grade="12",
    class_number=3,
    head_teacher_id=201,
    head_madric_id=301
)

# Students register and log in
student1.register(student1_profile)  
student2.register(student2_profile)

sleep(interval)  # Allow registration to process

student1.login(student1_profile.to_dict()["id"])
student2.login(student2_profile.to_dict()["id"])

sleep(interval)  # Allow login to process

# Create and start staff client
staff = Staff()
staff.start()

sleep(interval)  # Allow staff client to connect

# Staff profile with unique ID
staff_profile = Staff_Profile(
    id = 201,  # Ensure unique ID
    name = "Mr.",
    surname =  "Anderson",
    client_student_id_dict = {  # Students assigned to this staff member
        101: student1_profile,
        102: student2_profile
    }
).to_dict()

# Staff register and log in
staff.register(staff_profile)

sleep(interval)  # Allow registration to process

staff.login(staff_profile["id"])
sleep(interval)  # Allow login to process

# Student interval submits an exit request to their head teacher
student1.submit_request(
    content="Requesting permission to leave school early for a doctor’s appointment.",
    approver_id=student1_profile.to_dict()["head_teacher_id"]
)

sleep(interval)  # Allow exit request to process

# Staff views exit requests
staff.view_requests()

sleep(interval)  # Allow view request to process

# Staff approves the exit request
staff.approve_request(request_id=1)

sleep(interval)  # Allow approval to process

# Students and staff log out
student1.logout()
student2.logout()
staff.logout()
