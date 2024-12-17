import time
from Server import Server
from Student import Student
from Staff import Staff
from Profile import Profile
from threading import Thread

# TODO: make everything interactive

# Initialize and start the server
server = Server()
server.start()

interval = 5

time.sleep(interval)

# Create and start student clients
student1 = Student()
student2 = Student()
student1.start()
student2.start()

time.sleep(interval)  # Allow clients to connect

# Student profiles with unique IDs
student1_profile = Profile(
    id=101,
    name="Alice",
    surname="Chohen",
    grade="12",
    class_number=3,
    head_teacher_id=201,
    head_madric_id=301
).to_dict()

student2_profile = Profile(
    id=102,
    name="Aviad",
    surname="Gabay",
    grade="12",
    class_number=3,
    head_teacher_id=201,
    head_madric_id=301
).to_dict()

# Students register and log in
student1.register(student1_profile)  
student2.register(student2_profile)

time.sleep(interval)  # Allow registration to process

student1.login(student1_profile["id"])
student2.login(student2_profile["id"])

time.sleep(interval)  # Allow login to process

# Create and start staff client
staff = Staff()
staff.start()

time.sleep(interval)  # Allow staff client to connect

# Staff profile with unique ID
staff_profile = {
    "id": 201,  # Ensure unique ID
    "name": "Mr.",
    "surname": "Anderson",
    "client_student_id_dict": {  # Students assigned to this staff member
        101: student1_profile,
        102: student2_profile
    },
    "Request_ids":{}
}

# Staff register and log in
staff.register(staff_profile)

time.sleep(interval)  # Allow registration to process

staff.login(staff_profile["id"])

time.sleep(interval)  # Allow login to process

# Student interval submits an exit request to their head teacher
student1.submit_request(
    content="Requesting permission to leave school early for a doctor’s appointment.",
    approver_id=student1_profile["head_teacher_id"]
)

time.sleep(interval)  # Allow exit request to process

# Staff views exit requests
staff.view_requests()

time.sleep(interval)  # Allow view request to process

# Staff approves the exit request
staff.approve_request(request_id=1)

time.sleep(interval)  # Allow approval to process

# Students and staff log out
student1.logout()
student2.logout()
staff.logout()

# main menu 
# 1 - log in
# 2 - register
# user_id = student1[id]

# student menu
# 1 - log out  -- db[user_id].logout() -> user_id = NULL -> main menu 
# 2 - ask for exit request
#     L 1 return
#     L 2 enter exit request

# staff menu
# 1 - log out
# 2 - view exit requests
#     L 1 return
#     L 2 select exit request
#       L 1 return
#       L 2 aprove exit request
#       L 3 decline exit request 