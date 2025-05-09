"""
Defines action handlers for various operations in the boarding school system.
"""

from Encryption_handeling.API import API
import json
import sqlite3

# Initialize the API instance
api = API()

# Dictionary to store action handlers
action_handlers = {}

def action_handler(action_name):
    """
    Decorator to register a function as an action handler.

    Args:
        action_name (str): The name of the action to handle.

    Returns:
        function: The decorated function.
    """
    def decorator(func):
        action_handlers[action_name] = func  # Register the function in the action_handlers dictionary
        return func
    return decorator

@action_handler("signupStudent")
def signup_student(handler, req):
    """
    Handles the signup action for students.

    Args:
        handler (Handler): The handler managing the request.
        req (dict): The request data.
    """
    profile = req.get("profile", None)
    username = profile.get("name", None)
    password = profile.get("password", None)
    student_id = profile.get("id", None)
    if not username or not password or not profile:
        print("Missing required fields for signupStudent.")
        return
    api.sign_up(username, password, "student", profile)
    cookie = handler.create_cookie(username, student_id)
    handler.conn.send_msg(json.dumps({"status": "success", "message": "Student registered successfully", "cookie": cookie}).encode('utf-8'))

@action_handler("signupStaff")
def signup_staff(handler, req):
    """
    Handles the signup action for staff members.

    Args:
        handler (Handler): The handler managing the request.
        req (dict): The request data.
    """
    profile = req.get("profile", None)
    username = profile.get("name", None)
    password = profile.get("password", None)
    staff_id = profile.get("id", None)
    if not username or not password or not profile:
        print("Missing required fields for signupStaff.")
        return
    api.sign_up(username, password, "staff", profile)
    cookie = handler.create_cookie(username, staff_id)
    handler.conn.send_msg(json.dumps({"status": "success", "message": "Staff registered successfully", "cookie": cookie}).encode('utf-8'))

@action_handler("login")
def login(handler, req):
    """
    Handles the login action for users.

    Args:
        handler (Handler): The handler managing the request.
        req (dict): The request data.
    """
    username = req.get("username", None)
    password = req.get("password", None)
    if not username or not password:
        print("Missing required fields for login.")
        return
    user = api.get_user(username)
    if not user:
        print("Invalid username or password. not user")
        handler.conn.send_msg(json.dumps({"status": "error", "message": "Invalid username or password"}).encode('utf-8'))
        return
    if not api.check_password(user, password):
        print("Invalid username or password. not check_password")
        handler.conn.send_msg(json.dumps({"status": "error", "message": "Invalid username or password"}).encode('utf-8'))
        return
    cookie = handler.create_cookie(user.username, user.profile.id)
    handler.conn.send_msg(json.dumps({
        "status": "success",
        "message": "Login successful",
        "cookie": cookie,
        "profile": user.profile.to_dict()
    }).encode('utf-8'))

@action_handler("remove_user")
def remove_user(handler, req):
    """
    Handles the action to remove a user.

    Args:
        handler (Handler): The handler managing the request.
        req (dict): The request data.
    """
    username = req.get("username", None)
    if not username:
        print("Missing required fields for remove_user.")
        return
    api.delete_user(username)
    handler.conn.send_msg(json.dumps({"status": "success", "message": "User removed successfully"}).encode('utf-8'))

@action_handler("logout")
def logout(handler, req):
    """
    Handles the logout action for users.

    Args:
        handler (Handler): The handler managing the request.
        req (dict): The request data.
    """
    handler.conn.send_msg(json.dumps({"status": "success", "message": "Logout successful"}).encode('utf-8'))

@action_handler("submit_request")
def submit_request(handler, req):
    """
    Handles the action to submit a request.

    Args:
        handler (Handler): The handler managing the request.
        req (dict): The request data.
    """
    profile = req.get("profile", None)
    name = profile.get("name", None)
    student_id = profile.get("id", None)
    content = req.get("content", None)
    approver_id = req.get("approver_id", None)
    if not student_id or not content or not approver_id:
        print("Missing required fields for submit_request.")
        return
    connection = sqlite3.connect('Database/system.db')
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO exit_requests (student_id, content, approved, approver_id)
            VALUES (?, ?, ?, ?)
        """, (student_id, content, False, approver_id))
        connection.commit()
        cookie = handler.create_cookie(name, student_id)
        handler.conn.send_msg(json.dumps({"status": "success", "message": "Request submitted successfully", "cookie": cookie}).encode('utf-8'))
    except sqlite3.OperationalError as e:
        print(f"Error submitting request: {e}")
        handler.conn.send_msg(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
    finally:
        connection.close()

@action_handler("approve_request")
def approve_request(handler, req):
    """
    Handles the action to approve a request.

    Args:
        handler (Handler): The handler managing the request.
        req (dict): The request data.
    """
    request_id = req.get("request_id", None)
    if not request_id:
        print("Missing required fields for approve_request.")
        return
    connection = sqlite3.connect('Database/system.db')
    cursor = connection.cursor()
    try:
        cursor.execute("""
            UPDATE exit_requests SET approved = 1 WHERE id = ?
        """, (request_id,))
        connection.commit()
        handler.conn.send_msg(json.dumps({"status": "success", "message": "Request approved successfully"}).encode('utf-8'))
    except sqlite3.OperationalError as e:
        print(f"Error approving request: {e}")
        handler.conn.send_msg(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
    finally:
        connection.close()

@action_handler("view_requests")
def view_requests(handler, req):
    """
    Handles the action to view pending requests.

    Args:
        handler (Handler): The handler managing the request.
        req (dict): The request data.
    """
    profile = req.get("profile", None)
    if not profile:
        print("Missing profile in the request.")
        handler.conn.send_msg(json.dumps({"status": "error", "message": "Profile is required"}).encode('utf-8'))
        return

    approver_id = profile.get("id", None)
    if not approver_id:
        print("Missing approver ID in the profile.")
        handler.conn.send_msg(json.dumps({"status": "error", "message": "Approver ID is required"}).encode('utf-8'))
        return

    connection = sqlite3.connect('Database/system.db')
    cursor = connection.cursor()
    try:
        # Fetch requests where the approver_id matches
        cursor.execute("""
            SELECT * FROM exit_requests WHERE approver_id = ?
        """, (approver_id,))
        requests = cursor.fetchall()

        # Format the requests into a response
        response = [{"id": r[0], "student_id": r[1], "content": r[2], "approved": bool(r[3])} for r in requests]

        # Send the response back to the client
        cookie = handler.create_cookie(profile.get("name", None), approver_id)
        handler.conn.send_msg(json.dumps({
            "status": "success",
            "requests": response,
            "cookie": cookie,
            "profile": profile
        }).encode('utf-8'))
    except sqlite3.OperationalError as e:
        print(f"Error viewing requests: {e}")
        handler.conn.send_msg(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
    finally:
        connection.close()

@action_handler("view_approved_requests")
def view_approved_requests(handler, req):
    """
    Handles the action to view approved requests.

    Args:
        handler (Handler): The handler managing the request.
        req (dict): The request data.
    """
    profile = req.get("profile", None)
    if not profile:
        print("Missing profile in the request.")
        handler.conn.send_msg(json.dumps({"status": "error", "message": "Profile is required"}).encode('utf-8'))
        return

    approver_id = profile.get("id", None)
    if not approver_id:
        print("Missing approver ID in the profile.")
        handler.conn.send_msg(json.dumps({"status": "error", "message": "Approver ID is required"}).encode('utf-8'))
        return

    try:
        # Fetch approved requests using the API
        requests = handler.api.get_approved_requests(approver_id)

        # Send the response back to the client
        cookie = handler.create_cookie(profile.get("name", None), approver_id)
        handler.conn.send_msg(json.dumps({
            "status": "success",
            "requests": requests,
            "cookie": cookie,
            "profile": profile
        }).encode('utf-8'))
    except Exception as e:
        print(f"Error handling view_approved_requests: {e}")
        handler.conn.send_msg(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
