import time
from Server import Server
from Student import Student
from Staff import Staff

# TODO: make everything interactive

# Initialize and start the server
server = Server()
server.start()

time.sleep(1)  # Allow the server to start before clients connect # TODO: replace all sleep with Thread.join

# Create and start student clients
student1 = Student()
student2 = Student()
student1.start()
student2.start()

time.sleep(1)  # Allow clients to connect

# Student profiles with unique IDs
student1_profile = { # TODO: hace a class "profile" to contain profile info
    "id": 101,  # Ensure unique ID
    "name": "Alice",
    "surname": "Johnson",
    "grade": "10",
    "class_number": 1,
    "head_teacher_id": 201,
    "head_madric_id": 301,
    "role": "student"
}

student2_profile = {
    "id": 102,  # Ensure unique ID
    "name": "Bob",
    "surname": "Smith",
    "grade": "10",
    "class_number": 1,
    "head_teacher_id": 201,
    "head_madric_id": 301,
    "role": "student"
}

# Students register and log in
student1.register(student1_profile)  # Use 'register' instead of 'signup'
student2.register(student2_profile)

time.sleep(1)  # Allow registration to process

student1.login(student1_profile["id"])
student2.login(student2_profile["id"])

time.sleep(1)  # Allow login to process

# Create and start staff client
staff = Staff()
staff.start()

time.sleep(1)  # Allow staff client to connect

# Staff profile with unique ID
staff_profile = {
    "id": 201,  # Ensure unique ID
    "name": "Mr.",
    "surname": "Anderson",
    "client_student_id_dict": {  # Students assigned to this staff member
        101: student1_profile,
        102: student2_profile
    },
    "role": "teacher"  # Staff-specific role
}

# Staff register and log in
staff.register(staff_profile)

time.sleep(1)  # Allow registration to process

staff.login(staff_profile["id"])

time.sleep(1)  # Allow login to process

# Student 1 submits an exit request to their head teacher
student1.submit_request(
    content="Requesting permission to leave school early for a doctor’s appointment.",
    approver_id=staff_profile["id"]
)

time.sleep(1)  # Allow exit request to process

# Staff views exit requests
staff.view_requests()

time.sleep(1)  # Allow view request to process

# Staff approves the exit request
staff.approve_request(request_id=1)

time.sleep(1)  # Allow approval to process

# Students and staff log out
student1.logout()
student2.logout()
staff.logout()
