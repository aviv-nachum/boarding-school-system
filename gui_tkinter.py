"""
GUI class for handling user interaction in the boarding school system using tkinter.
Provides menus for students and staff with the same functionality as the terminal-based GUI.
"""

import tkinter as tk
from tkinter import messagebox
from Clients.Student import Student
from Clients.Staff import Staff
from Profiles.Staff_Profile import Staff_Profile
from Profiles.Student_Profile import Student_Profile
from db_manager import get_user
from time import sleep


class GUIApp:
    """
    Represents the graphical user interface for the boarding school system using tkinter.
    """
    def __init__(self, root):
        """
        Initializes the GUI application.

        Args:
            root (tk.Tk): The root window of the tkinter application.
        """
        self.root = root
        self.root.title("Boarding School System")
        self.root.geometry("800x600")  # Set the window size to 800x600
        self.current_user = None  # Tracks the currently logged-in user
        self.main_menu()

    def main_menu(self):
        """
        Displays the main menu for the system.
        """
        self.clear_window()

        tk.Label(self.root, text="--- Main Menu ---", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Log in as Student", command=self.login_student, width=20).pack(pady=5)
        tk.Button(self.root, text="Log in as Staff", command=self.login_staff, width=20).pack(pady=5)
        tk.Button(self.root, text="Register as Student", command=self.register_student, width=20).pack(pady=5)
        tk.Button(self.root, text="Register as Staff", command=self.register_staff, width=20).pack(pady=5)
        tk.Button(self.root, text="Exit", command=self.exit_program, width=20).pack(pady=5)

    def register_student(self):
        """
        Displays the registration form for a new student.
        """
        self.clear_window()

        tk.Label(self.root, text="--- Register as Student ---", font=("Arial", 16)).pack(pady=10)
        entries = self.create_form(["ID", "Name", "Surname", "Grade", "Class Number", "Head Teacher ID", "Head Madrich ID", "Password"])

        def submit():
            data = {key: entry.get() for key, entry in entries.items()}
            profile = Student_Profile(
                id=data["ID"],
                name=data["Name"],
                surname=data["Surname"],
                grade=data["Grade"],
                class_number=int(data["Class Number"]),
                head_teacher_id=int(data["Head Teacher ID"]),
                head_madric_id=int(data["Head Madrich ID"]),
                password=data["Password"],
                role="student"
            )
            self.current_user = Student(data["Name"], data["Password"], profile)
            self.current_user.start()
            sleep(1)
            self.current_user.register(profile)
            messagebox.showinfo("Success", "Student registered successfully.")
            self.main_menu()

        tk.Button(self.root, text="Submit", command=submit).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=5)

    def login_student(self):
        """
        Displays the login form for a student.
        """
        self.clear_window()

        tk.Label(self.root, text="--- Log in as Student ---", font=("Arial", 16)).pack(pady=10)
        entries = self.create_form(["Name", "Password"])

        def submit():
            name = entries["Name"].get()
            password = entries["Password"].get()
            user_data = get_user(name)
            if user_data and user_data.role == "student" and user_data.password == password:
                self.current_user = Student(name, password, user_data.profile)
                self.current_user.start()
                sleep(1)
                self.current_user.login(user_data.profile.id)
                self.student_menu()
            else:
                messagebox.showerror("Error", "Invalid username or password.")

        tk.Button(self.root, text="Login", command=submit).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=5)

    def register_staff(self):
        """
        Displays the registration form for a new staff member.
        """
        self.clear_window()

        tk.Label(self.root, text="--- Register as Staff ---", font=("Arial", 16)).pack(pady=10)
        entries = self.create_form(["ID", "Name", "Surname", "Password"])

        def submit():
            data = {key: entry.get() for key, entry in entries.items()}
            profile = Staff_Profile(
                id=data["ID"],
                name=data["Name"],
                surname=data["Surname"],
                password=data["Password"],
                role="staff"
            )
            self.current_user = Staff(data["Name"], data["Password"], profile)
            self.current_user.start()
            sleep(1)
            self.current_user.register(profile)
            messagebox.showinfo("Success", "Staff registered successfully.")
            self.main_menu()

        tk.Button(self.root, text="Submit", command=submit).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=5)

    def login_staff(self):
        """
        Displays the login form for a staff member.
        """
        self.clear_window()

        tk.Label(self.root, text="--- Log in as Staff ---", font=("Arial", 16)).pack(pady=10)
        entries = self.create_form(["Name", "Password"])

        def submit():
            name = entries["Name"].get()
            password = entries["Password"].get()
            user_data = get_user(name)
            if user_data and user_data.role == "staff" and user_data.password == password:
                self.current_user = Staff(name, password, user_data.profile)
                self.current_user.start()
                sleep(1)
                self.current_user.login(user_data.profile.id)
                self.staff_menu()
            else:
                messagebox.showerror("Error", "Invalid username or password.")

        tk.Button(self.root, text="Login", command=submit).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=5)

    def student_menu(self):
        """
        Displays the student menu.
        """
        self.clear_window()

        tk.Label(self.root, text="--- Student Menu ---", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Submit Request", command=self.submit_request).pack(pady=5)
        tk.Button(self.root, text="Logout", command=self.main_menu).pack(pady=5)

    def submit_request(self):
        """
        Displays the form to submit a new exit request.
        """
        self.clear_window()

        tk.Label(self.root, text="--- Submit Request ---", font=("Arial", 16)).pack(pady=10)
        entries = self.create_form(["Request Content", "Approver ID"])

        def submit():
            content = entries["Request Content"].get()
            approver_id = entries["Approver ID"].get()
            self.current_user.submit_request(content, approver_id)
            messagebox.showinfo("Success", "Request submitted successfully.")
            self.student_menu()

        tk.Button(self.root, text="Submit", command=submit).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.student_menu).pack(pady=5)

    def staff_menu(self):
        """
        Displays the staff menu.
        """
        self.clear_window()

        tk.Label(self.root, text="--- Staff Menu ---", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="View Exit Requests", command=self.view_requests).pack(pady=5)
        tk.Button(self.root, text="View Approved Requests", command=self.view_approved_requests).pack(pady=5)
        tk.Button(self.root, text="Logout", command=self.main_menu).pack(pady=5)

    def view_requests(self):
        """
        Displays the list of pending exit requests and allows approval of a selected request.
        """
        self.clear_window()

        tk.Label(self.root, text="--- Pending Requests ---", font=("Arial", 16)).pack(pady=10)

        # Create a Listbox to display the requests
        listbox = tk.Listbox(self.root, width=100, height=20)
        listbox.pack(pady=10)

        # Fetch and display the pending requests
        requests = self.current_user.view_requests()  # Fetch the requests from the server
        if not requests:  # Handle the case where no requests are returned
            tk.Label(self.root, text="No pending requests.", font=("Arial", 12)).pack(pady=10)
            tk.Button(self.root, text="Back", command=self.staff_menu).pack(pady=5)
            return

        # Populate the Listbox with requests
        for req in requests:
            listbox.insert(tk.END, f"Request ID: {req['id']}, Student ID: {req['student_id']}, Content: {req['content']}, Approved: {req['approved']}")

        def approve_selected_request():
            """
            Approves the selected request from the Listbox.
            """
            selected_index = listbox.curselection()  # Get the index of the selected item
            if selected_index:
                selected_request = requests[selected_index[0]]  # Get the corresponding request
                self.current_user.approve_request(selected_request['id'])  # Approve the request
                messagebox.showinfo("Success", f"Request ID {selected_request['id']} approved.")
                self.view_requests()  # Refresh the requests view
            else:
                messagebox.showerror("Error", "No request selected.")

        # Add a button to approve the selected request
        tk.Button(self.root, text="Approve Selected Request", command=approve_selected_request).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.staff_menu).pack(pady=5)

    def view_approved_requests(self):
        """
        Displays the list of approved exit requests.
        """
        self.clear_window()

        tk.Label(self.root, text="--- Approved Requests ---", font=("Arial", 16)).pack(pady=10)

        # Create a Listbox to display the approved requests
        listbox = tk.Listbox(self.root, width=100, height=20)
        listbox.pack(pady=10)

        # Fetch and display the approved requests
        requests = self.current_user.view_approved_requests()  # Fetch the approved requests from the server
        if not requests:  # Handle the case where no approved requests are returned
            tk.Label(self.root, text="No approved requests.", font=("Arial", 12)).pack(pady=10)
            tk.Button(self.root, text="Back", command=self.staff_menu).pack(pady=5)
            return

        # Populate the Listbox with approved requests
        for req in requests:
            listbox.insert(tk.END, f"Request ID: {req['id']}, Student ID: {req['student_id']}, Content: {req['content']}, Approved: {req['approved']}")

        # Add a Back button to return to the staff menu
        tk.Button(self.root, text="Back", command=self.staff_menu).pack(pady=5)

    def exit_program(self):
        """
        Exits the program.
        """
        self.root.destroy()

    def clear_window(self):
        """
        Clears all widgets from the current window.
        """
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_form(self, fields):
        """
        Creates a form with the specified fields.

        Args:
            fields (list): A list of field names.

        Returns:
            dict: A dictionary mapping field names to their entry widgets.
        """
        entries = {}
        for field in fields:
            tk.Label(self.root, text=field).pack(pady=5)
            entry = tk.Entry(self.root)
            entry.pack(pady=5)
            entries[field] = entry
        return entries


if __name__ == "__main__":
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()