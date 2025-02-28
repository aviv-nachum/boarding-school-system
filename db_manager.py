import os
import sqlite3
import json
from Profiles.Staff_Profile import Staff_Profile
from Profiles.Student_Profile import Student_Profile
from Clients.User import User
from Profiles.Profile import Profile

def store_in_DB(user):
    connection = sqlite3.connect('Database/system.db')
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (username, password, role, profile)
            VALUES (?, ?, ?, ?)
        """, (user.username, user.password, user.role, json.dumps(user.profile)))
        connection.commit()
    except sqlite3.IntegrityError as e:
        print(f"Error storing user in DB: {e}")
    finally:
        connection.close()

def remove_from_DB(username):
    connection = sqlite3.connect('Database/system.db')
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        connection.commit()
    except sqlite3.OperationalError as e:
        print(f"Error removing user from DB: {e}")
    finally:
        connection.close()

def get_user(username):
    connection = sqlite3.connect('Database/system.db')
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT username, password, role, profile FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        if user_data:
            profile_data = json.loads(user_data[3])
            if user_data[2] == "student":
                profile = Student_Profile.from_dict(profile_data)
            elif user_data[2] == "staff":
                profile = Staff_Profile.from_dict(profile_data)
            else:
                profile = None
            return User(username=user_data[0], password=user_data[1], role=user_data[2], profile=profile)
        else:
            return None
    except sqlite3.OperationalError as e:
        print(f"Error retrieving user from DB: {e}")
        return None
    finally:
        connection.close()

def reset_database():
    db_path = 'Database/system.db'
    
    # Remove the existing database file if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing database file successfully")

    # Create a new database file and reset its structure
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            profile TEXT NOT NULL
        )''')

    cursor.execute('''CREATE TABLE exit_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            content TEXT,
            approved BOOLEAN,
            approver_id TEXT,
            FOREIGN KEY (student_id) REFERENCES users (username),
            FOREIGN KEY (approver_id) REFERENCES users (username)
        )''')

    connection.commit()
    connection.close()
    print("Database reset and structure created successfully")