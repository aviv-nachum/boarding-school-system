import time
from Server import Server
from Student import Student
from Staff import Staff

def interactive_main():
    server = Server()
    server.start()
    server.join()  # Wait for the server thread to finish

    # Create and start student clients
    student1 = Student()
    student2 = Student()
    student1.start()
    student2.start()

    student1_profile = {
        "id": 101,
        "name": "Alice",
        "surname": "Johnson",
        "grade": "10",
        "class_number": 1,
        "head_teacher_id": 201,
        "head_madric_id": 301,
        "role": "student"
    }

    student2_profile = {
        "id": 102,
        "name": "Bob",
        "surname": "Smith",
        "grade": "10",
        "class_number": 1,
        "head_teacher_id": 201,
        "head_madric_id": 301,
        "role": "student"
    }

    student1.register(student1_profile)
    student2.register(student2_profile)

    time.sleep(1)

    student1.login(student1_profile["id"])
    student2.login(student2_profile["id"])

    # Staff
    staff = Staff()
    staff.start()

    staff_profile = {
        "id": 201,
        "name": "Mr.",
        "surname": "Anderson",
        "client_student_id_dict": {
            101: student1_profile,
            102: student2_profile
        },
        "role": "teacher"
    }

    staff.register(staff_profile)
    staff.login(staff_profile["id"])

    # Submit and view exit request
    student1.submit_request("Doctor’s appointment request", approver_id=staff_profile["id"])
    staff.view_requests()

    # Approve request
    staff.approve_request(request_id=1)

    # Logout all
    student1.logout()
    student2.logout()
    staff.logout()

if __name__ == "__main__":
    interactive_main()
