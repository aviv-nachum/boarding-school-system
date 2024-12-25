import time
from Server import Server
from Clients.Student import Student
from Clients.Staff import Staff
from Profiles.Staff_Profile import Staff_Profile
from Profiles.Student_Profile import Student_Profile
from threading import Thread

# TODO: make everything interactive

# Initialize and start the server
server = Server()
server.start()
user = Student()


interval = 2
time.sleep(interval)

# start menu
def start_menu(): # fix instantaneous disconnection problem 
    print("---start menu--- \n 1 - student \n 2 - staff ")
    client_type = input(">>")
    
    if client_type == "1":
        user = Student()
        user.start()
    elif client_type == "2":
        user = Staff()
        user.start()
    else:
        print("wrong input, please try again")
        start_menu()

start_menu()
time.sleep(interval)

# main menu
def main_menu():
    print("---main menu--- \n 1 - log in \n 2 - register ")
    action = input(">>")

    if action == "1":
        user.login(input("enter id: \n>>"))

    elif action == "2":
        profile = Student_Profile(
        id = input("enter id: \n>>"),
        name = input("enter name: \n>>"),
        surname = input("enter surname: \n>>"),
        grade = input("enter grade: \n>>"),
        class_number = input("enter class_number: \n>>"),
        head_teacher_id = input("enter head_teacher_id: \n>>"),
        head_madric_id = input("enter head_madric_id: \n>>")
        )

        user.register(profile)

main_menu()

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


time.sleep(interval)

# Create and start student clients
student1 = Student()
student2 = Student()
student1.start()
student2.start()

time.sleep(interval)  # Allow clients to connect

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

time.sleep(interval)  # Allow registration to process

student1.login(student1_profile.to_dict()["id"])
student2.login(student2_profile.to_dict()["id"])

time.sleep(interval)  # Allow login to process

# Create and start staff client
staff = Staff()
staff.start()

time.sleep(interval)  # Allow staff client to connect

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

time.sleep(interval)  # Allow registration to process

staff.login(staff_profile["id"])

time.sleep(interval)  # Allow login to process

# Student interval submits an exit request to their head teacher
student1.submit_request(
    content="Requesting permission to leave school early for a doctor’s appointment.",
    approver_id=student1_profile.to_dict()["head_teacher_id"]
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

