#visual calory data

#valid email checker login sign up
#crude error check on updating
#on the meal planner page calorie goals should have visible default value

#YANG: changes in RDAwindw and Analysis classes
#Yang: Move the back button in sign in page

import math
import subprocess
from sklearn.linear_model import LinearRegression
def execute_and_clear(command):
        subprocess.call(command, shell=True)
        subprocess.call('cls', shell=True)
        print('PS M:\python trial error> &'+ '\x1b[33m' + ' c:/python3/python.exe ' + '\x1b[0m' + '\033[96m'+ '"m:/python trial error/Healthy_U.py"'+ '\033[0m')
execute_and_clear("pip install reportlab")
#execute_and_clear("pip install tkcalendar")
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
import numpy as np
from datetime import datetime, timedelta
import io
import concurrent.futures
import webbrowser
from PIL import ImageTk, Image
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import hashlib
import secrets
import sys
import requests
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

class Database:
    def __init__(self):
        self.connection = sqlite3.connect('users.db')
        self.cursor = self.connection.cursor()
        self.create_users_table()
        self.create_food_log_table()
        self.create_water_log_table()
        self.create_weight_log_table()

    def create_users_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                username TEXT PRIMARY KEY,
                                password_hash TEXT,
                                salt TEXT,
                                name TEXT,
                                age INTEGER,
                                gender TEXT,
                                weight INTEGER,
                                height INTEGER,
                                lifestyle TEXT,
                                water_intake TEXT,
                                goals TEXT
                              )''')
        self.connection.commit()

    def create_food_log_table(self):
        # Create the food_log table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS food_log (
                                    username TEXT,
                                    datetime DATETIME,
                                    food_item TEXT,
                                    quantity TEXT,
                                    calories FLOAT, 
                                    protein FLOAT, 
                                    fat FLOAT, 
                                    carb FLOAT, 
                                    fibre FLOAT
                                )''')
        self.connection.commit()
        #self.cursor.execute('''ALTER TABLE food_log RENAME COLUMN date TO datetime''')
        #self.connection.commit()
        #self.cursor.execute('''DELETE FROM food_log;''')
        #self.connection.commit()
        #self.cursor.execute('''ALTER TABLE food_log ADD COLUMN total_daily_calories FLOAT''')
        # self.connection.commit()
        # self.cursor.execute("DROP TABLE IF EXISTS food_log;")
        # self.connection.commit()

    def create_water_log_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS water_log (
                                username TEXT,
                                datetime TEXT,
                                amount INTEGER
                              )''')
        self.connection.commit()
        #self.cursor.execute('''DELETE FROM water_log;''')
        #self.connection.commit()
        # self.cursor.execute('''ALTER TABLE water_log RENAME COLUMN date TO datetime''')
        # self.connection.commit()
        # Debugging: Print the schema of the food_log table
        # self.cursor.execute("PRAGMA table_info(water_log)")
        # print("Schema of water_log table:")
        # for column in self.cursor.fetchall():
        #     print(column)
        # self.cursor.execute('''SELECT * FROM water_log''')
        # print("Contents of food_log table:")
        # for row in self.cursor.fetchall():
        #     print(row)
        # self.connection.commit()

    def create_weight_log_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS weight_log (
                                username TEXT,
                                date TEXT,
                                weight INTEGER
                              )''')
        self.connection.commit()
        #self.cursor.execute('''ALTER TABLE weight_log RENAME COLUMN datetime TO date''')
        #self.connection.commit()
        #self.cursor.execute('''DELETE FROM weight_log;''')
        #self.connection.commit()
            
    def add_user(self, username, password):
        salt = secrets.token_hex(16)  # Generate a random salt
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        self.cursor.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                            (username, password_hash, salt))
        self.connection.commit()

    def save_additional_info(self, username, name, age, gender, weight, height, lifestyle, water_intake, goals):
        self.cursor.execute("UPDATE users SET name=?, age=?, gender=?, weight=?, height=?, lifestyle=?, water_intake=?, goals=? WHERE username=?",
                            (name, age, gender, weight, height, lifestyle, water_intake, goals, username))
        self.connection.commit()

    def get_user(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        return self.cursor.fetchone()

    def populate_food_log(self, username, datetime, food_item, quantity, calories, protein, fat, carb, fibre):
        try:
            self.cursor.execute("INSERT INTO food_log (username, datetime, food_item, quantity, calories, protein, fat, carb, fibre) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (username, datetime, food_item, quantity, calories, protein, fat, carb, fibre))
            self.connection.commit()
        except sqlite3.Error as e:
            print("Error occurred while inserting into food_log:", e)

    def get_food_log(self, username):
        query = "SELECT * FROM food_log WHERE username=?"
        self.cursor.execute(query, (username,))
        return self.cursor.fetchall()

    def log_water_intake(self, username, datetime, amount):
        try:
            self.cursor.execute("INSERT INTO water_log (username, datetime, amount) VALUES (?, ?, ?)",
                                (username, datetime, amount))
            self.connection.commit()
        except sqlite3.Error as e:
            print("Error occurred while inserting into water_log:", e)

    def get_water_intake(self, username):
        query = "SELECT * FROM water_log WHERE username=?"
        self.cursor.execute(query, (username,))
        return self.cursor.fetchall()
    
    def log_weight(self, username, date, weight):
        self.cursor.execute("INSERT INTO weight_log (username, date, weight) VALUES (?, ?, ?)",
                            (username, date, weight))
        self.connection.commit()
    
    def get_weight_log(self, username):
        query = "SELECT * FROM weight_log WHERE username=?"
        self.cursor.execute(query, (username,))
        return self.cursor.fetchall()
    
    def check_weight_entry(self, username, date):
        self.cursor.execute("SELECT * FROM weight_log WHERE username=? AND date=?", (username, date))
        entry = self.cursor.fetchone()
        if entry:
            return True
        else:
            return False
        

    def display_food_log_by_date_range(self, username, start_date, end_date):
        # Adjust end_date to include all entries on the end date
        end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        end_date = end_date.strftime("%Y-%m-%d")

        query = "SELECT * FROM food_log WHERE username=? AND datetime BETWEEN ? AND ? ORDER BY datetime ASC"
        self.cursor.execute(query, (username, start_date, end_date))
        return self.cursor.fetchall()
    
    def display_hydration_log_by_date_range(self, username, start_date, end_date):
        # Adjust end_date to include all entries on the end date
        end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        end_date = end_date.strftime("%Y-%m-%d")

        query = "SELECT * FROM water_log WHERE username=? AND datetime BETWEEN ? AND ? ORDER BY datetime ASC"
        self.cursor.execute(query, (username, start_date, end_date))
        return self.cursor.fetchall()

    def display_weight_log_by_date_range(self, username, start_date, end_date):
        # Adjust end_date to include all entries on the end date
        end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        end_date = end_date.strftime("%Y-%m-%d")

        query = "SELECT * FROM weight_log WHERE username=? AND date BETWEEN ? AND ? ORDER BY date ASC"
        self.cursor.execute(query, (username, start_date, end_date))
        return self.cursor.fetchall()
        
class AdditionalInfoWindow:
        def __init__(self, parent, username):
            self.parent = parent
            self.username = username
            self.additional_info_window = tk.Toplevel(self.parent)
            self.additional_info_window.title('Additional Information')
            self.additional_info_window.resizable(0, 0)
            self.center_window(self.additional_info_window, 1166, 718)
            self.create_variables()
            self.create_additional_info_widgets()
            self.create_error_widgets()  # Create error widgets once

        def create_error_widgets(self):
            self.error_window = tk.Toplevel(self.additional_info_window)
            self.error_window.title("Error")
            self.error_messages = tk.Text(self.error_window, height=10, width=50)
            self.error_messages.pack()
            ok_button = tk.Button(self.error_window, text="OK", command=self.error_window.destroy)
            ok_button.pack()
            self.error_window.withdraw()  # Hide error window initially

        def center_window(self, window, width, height):
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            x_coordinate = (screen_width / 2) - (width / 2)
            y_coordinate = (screen_height / 2) - (height / 2)
            window.geometry(f'{width}x{height}+{int(x_coordinate)}+{int(y_coordinate)}')

        def create_variables(self):
            self.name_var = tk.StringVar()
            self.age_var = tk.StringVar()
            self.gender_var = tk.StringVar()
            self.weight_var = tk.StringVar()
            self.height_var = tk.StringVar()
            self.lifestyle_var = tk.StringVar()
            self.water_intake_var = tk.StringVar()
            self.goals_var = tk.StringVar()

        def create_additional_info_widgets(self):


            bg_image = Image.open('images/background2.jpg')
            bg_photo = ImageTk.PhotoImage(bg_image)

            # Create a label to display the background image
            bg_label = tk.Label(self.additional_info_window, image=bg_photo)
            bg_label.image = bg_photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                
            additional_info_frame = tk.Frame(self.additional_info_window, bg='#FFF8F4', width=950, height=600)
            additional_info_frame.place(x=100, y=50)

        
            tk.Label(additional_info_frame, text="Additional Information", bg="#FFF8F4", fg="black",
                    font=("yu gothic ui", 25, "bold")).place(x=280, y=20)

            fields = ["First Name", "Age", "Gender", "Weight (kg)", "Height (cm)", "Current Lifestyle", "Avg Daily Water Intake (litres)", "Future Goals"]
            entries = [self.name_var, self.age_var, self.gender_var, self.weight_var, self.height_var, self.lifestyle_var, self.water_intake_var, self.goals_var]


            # Create a custom style
            style = ttk.Style()
            style.configure("Custom.TLabel", background="#FFF8F4")

            for i, field in enumerate(fields):
                label = ttk.Label(additional_info_frame, text=field, font=("yu gothic ui", 15, "bold"), style="Custom.TLabel")
                label.place(x=180, y=100+i*50)
                
                entry = ttk.Entry(additional_info_frame, textvariable=entries[i], background="#FFF8F4")
                entry.place(x=560, y=100+i*50)



            gender_combobox = ttk.Combobox(additional_info_frame, textvariable=self.gender_var, values=["Male", "Female"], state="readonly")
            gender_combobox.place(x=560, y=200)

            lifestyle_combobox = ttk.Combobox(additional_info_frame, textvariable=self.lifestyle_var, values=["Sedentary", "Light", "Moderate", "Active"], state="readonly")
            lifestyle_combobox.place(x=560, y=350)

            water_intake_combobox = ttk.Combobox(additional_info_frame, textvariable=self.water_intake_var, values=["Less than 1L", "1-2L", "2-4L", "4-6L", "6-8L", "More than 8L"], state="readonly")
            water_intake_combobox.place(x=560, y=400)

            goals_combobox = ttk.Combobox(additional_info_frame, textvariable=self.goals_var, values=["Weight Loss", "Maintenance", "Muscle Gain", "Performance"], state="readonly")
            goals_combobox.place(x=560, y=450)

            # Button to submit additional information
            submit_button = tk.Button(additional_info_frame, text="Submit", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                                    cursor='hand2', fg='white', command=self.submit_additional_info, bg='#53c200')
            submit_button.place(x=375, y=500)

        def submit_additional_info(self):
            # Retrieve user input from the entry fields
            name = self.name_var.get()
            age = self.age_var.get()
            gender = self.gender_var.get()
            weight = self.weight_var.get()
            height = self.height_var.get()
            lifestyle = self.lifestyle_var.get()
            water_intake = self.water_intake_var.get()
            goals = self.goals_var.get()

            # Error checking
            error_message = self.validate_input(name, age, gender, weight, height, lifestyle, water_intake, goals)
            if error_message:
                self.show_error_message(error_message)
            else:
                db = Database()
                db.save_additional_info(self.username, name, age, gender, weight, height, lifestyle, water_intake, goals)
                messagebox.showinfo("Success", "Additional information saved successfully")
                self.parent.withdraw()
                self.additional_info_window.destroy()
                HomePage()

        def validate_input(self, name, age, gender, weight, height, lifestyle, water_intake, goals):
            if not name:
                return "Please enter your first name only"
            if not age.isdigit() or int(age) <= 0 or int(age) > 120:
                return "Please enter a valid age"
            if gender not in ["Male", "Female"]:
                return "Please select a valid gender"
            if not weight.isdigit() or int(weight) <= 0 or int(weight) > 600:
                return "Please enter a valid weight"
            if not height.isdigit() or int(height) <= 0 or int(weight) > 250:
                return "Please enter a valid height"
            if lifestyle not in ["Sedentary", "Light", "Moderate", "Active"]:
                return "Please select a valid lifestyle"
            if water_intake not in ["Less than 1L", "1-2L", "2-4L", "4-6L", "6-8L", "More than 8L"]:
                return "Please select a valid water intake"
            if goals not in ["Weight Loss", "Maintenance", "Muscle Gain", "Performance"]:
                return "Please select valid goals"
            return None

        def show_error_message(self, message):
            self.error_messages.config(state=tk.NORMAL)
            self.error_messages.delete('1.0', tk.END)
            self.error_messages.insert(tk.END, message)
            self.error_messages.config(state=tk.DISABLED)
            self.error_window.deiconify()
            self.error_window.lift()

        def create_error_widgets(self):
            self.error_window = tk.Toplevel(self.additional_info_window)
            self.error_window.title("Error")
            self.error_messages = tk.Text(self.error_window, height=10, width=50)
            self.error_messages.pack()
            ok_button = tk.Button(self.error_window, text="OK", command=self.error_window.withdraw)
            ok_button.pack()
            self.error_window.withdraw()  # Hide error window initially

class SignupWindow:
    def __init__(self, parent):
        self.parent = parent
        self.signup_window = tk.Toplevel(self.parent)
        self.signup_window.title('Sign Up')
        self.signup_window.resizable(0, 0)
        self.center_window(self.signup_window, 1166, 718)
        self.create_variables()
        self.create_signup_widgets()

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (width / 2)
        y_coordinate = (screen_height / 2) - (height / 2)
        window.geometry(f'{width}x{height}+{int(x_coordinate)}+{int(y_coordinate)}')

    def create_variables(self):
        self.signup_username = tk.StringVar()  
        self.signup_password = tk.StringVar()  

    def create_signup_widgets(self):
        bg_image = Image.open('images/background2.jpg')
        bg_photo = ImageTk.PhotoImage(bg_image)

        # Create a label to display the background image
        bg_label = tk.Label(self.signup_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.signup_frame = tk.Frame(self.signup_window, bg='#FFF8F4', width=950, height=600)
        self.signup_frame.place(x=100, y=50)
        self.sign_up_image = Image.open('images\\hyy.png')
        photo = ImageTk.PhotoImage(self.sign_up_image)
        self.sign_up_image_label = tk.Label(self.signup_frame, image=photo, bg='#FFF8F4')
        self.sign_up_image_label.image = photo
        self.sign_up_image_label.place(x=400, y=60)

        tk.Label(self.signup_frame, text="Please Enter Your Details Below", bg="#FFF8F4", fg="black",
                 font=("yu gothic ui", 15, "bold")).place(x=335, y=170)
    
        self.create_label_with_icon("Username:", 350, 250, 'images\\username_icon.png')
        self.signup_username_entry = self.create_entry_with_line(380, 278, 221, textvariable=self.signup_username)

        self.create_label_with_icon("Password:", 350, 320, 'images\\password_icon.png')
        self.signup_password_entry = self.create_entry_with_line(380, 348, 218, textvariable=self.signup_password, password=True)
        # Create show/hide password button
        self.create_show_hide_button()

        self.create_button("Sign Up", self.signup_user, 357, 400)

        self.create_back_button_and_close_signup_window(357,400)

    def create_show_hide_button(self):
        self.show_image = ImageTk.PhotoImage(file='images\\show.png')
        self.hide_image = ImageTk.PhotoImage(file='images\\hide.png')
        self.show_button = tk.Button(self.signup_frame, image=self.show_image, command=self.show_hide_password, relief=tk.FLAT,
                                     activebackground="#FFF8F4", borderwidth=0, background="#FFF8F4", cursor="hand2")
        self.show_button.place(x=600, y=353)

    def show_hide_password(self):
        show_char = '' if self.signup_password_entry.cget('show') else '*'
        self.signup_password_entry.config(show=show_char)
        image = self.hide_image if show_char else self.show_image
        self.show_button.config(image=image)

    def create_label_with_icon(self, text, x, y, icon_path):
        label = tk.Label(self.signup_frame, text=text, font=("yu gothic ui", 13, "bold"), bg="#FFF8F4", fg="#4f4e4d")
        label.place(x=x, y=y)
        icon = Image.open(icon_path)
        self.photo = ImageTk.PhotoImage(icon)  # Store the image in a class-level variable
        icon_label = tk.Label(self.signup_frame, image=self.photo, bg='#FFF8F4')
        icon_label.image = self.photo  # Ensure image is not garbage collected
        icon_label.place(x=x, y=y+30)

    def create_entry_with_line(self, x, y, width, textvariable=None, password=False):
        entry = tk.Entry(self.signup_frame, textvariable=textvariable, highlightthickness=2, relief=tk.FLAT, bg="#FFF8F4", fg="#4f4e4d", font=("yu gothic ui ", 12, "bold"), show="*" if password else "")
        entry.place(x=x, y=y, width=width)
        tk.Canvas(self.signup_frame, width=250, height=1, bg="#FFF8F4", highlightthickness=0).place(x=x, y=y+25)
        return entry

    def create_button(self, text, command, x, y):
        tk.Button(self.signup_frame, text=text, font=("yu gothic ui", 13, "bold"), width=25, bd=0,
                  bg='#53c200', cursor='hand2', activebackground='#53c200', fg='white',
                  command=command).place(x=x, y=y)

    def create_back_button_and_close_signup_window(self,x,y):
        back_button = tk.Button(self.signup_frame, text="Back", font=("yu gothic ui", 13, "bold"), width=25, bd=0,bg='#3047ff',cursor='hand2', fg='white',
                                command=self.signup_window.destroy)
        back_button.place(x=x, y=y+50)
    
    def signup_user(self):
        SignupWindow.username = self.signup_username.get()
        SignupWindow.password = self.signup_password.get()

        if  SignupWindow.username and SignupWindow.password:
            db = Database()
            existing_user = db.get_user(SignupWindow.username)
            if existing_user:
                messagebox.showerror("Error", "Username already exists!")
            else:
                db.add_user( SignupWindow.username, SignupWindow.password)
                messagebox.showinfo("Success", "Registration Success")
                # Open the additional info window after successful signup
                AdditionalInfoWindow(self.parent, SignupWindow.username)
                self.signup_window.destroy()
        else:
            messagebox.showerror("Error", "Please enter both username and password")

class LoginPage:
    bg_img_path = 'images/background2.jpg'
    name_path = 'images/healthyu-.png'
    logo_path = 'images/logo.png'
    stock_user_img = 'images/hyy.png'
    USERNAME_ICON_PATH = 'images/username_icon.png'
    PASSWORD_ICON_PATH = 'images/password_icon.png'
    SHOW_IMAGE_PATH = 'images/show.png'
    HIDE_IMAGE_PATH = 'images/hide.png'

    def __init__(self, window):
        self.window = window
        self.set_window_properties()
        self.create_widgets()

    def set_window_properties(self):
        self.window.title('Login Page')
        self.window.resizable(0, 0)
        self.window_width = 1166
        self.window_height = 718

        # Get the screen width and height
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Calculate x and y coordinates for the window to be centered
        x_coordinate = int((screen_width - self.window_width) / 2)
        y_coordinate = int((screen_height - self.window_height) / 2)

        # Set the window geometry
        self.window.geometry(f'{self.window_width}x{self.window_height}+{x_coordinate}+{y_coordinate}')


    def create_widgets(self):
        self.create_background()
        self.create_login_frame()
        self.create_username_widgets()
        self.create_password_widgets()
        self.create_buttons()

    def create_background(self):
        bg_frame = Image.open(self.bg_img_path)
        photo = ImageTk.PhotoImage(bg_frame)
        self.bg_panel = tk.Label(self.window, image=photo)
        self.bg_panel.image = photo
        self.bg_panel.pack(fill='both', expand='yes')

    def create_login_frame(self):
        self.lgn_frame = tk.Frame(self.window, bg='#FFF8F4', width=950, height=600)
        self.lgn_frame.place(x=100, y=50)

        #name of the company
        name_frame = Image.open(self.name_path)
        name_photo = ImageTk.PhotoImage(name_frame)
        self.name_panel = tk.Label(self.window, image=name_photo, bg='#FFF8F4')
        self.name_panel.image = name_photo
        self.name_panel.place(x=120, y=90)
        
        #logo of the company
        logo_frame= Image.open(self.logo_path)
        photo = ImageTk.PhotoImage(logo_frame)
        self.logo_panel = tk.Label(self.window, image=photo, bg='#FFF8F4')
        self.logo_panel.image = photo
        self.logo_panel.place(x=200, y=230)

        #stock img of a user
        user_img_frame= Image.open(self.stock_user_img)
        photo = ImageTk.PhotoImage(user_img_frame)
        self.user_img_panel = tk.Label(self.window, image=photo, bg='#FFF8F4')
        self.user_img_panel.image = photo
        self.user_img_panel.place(x=750, y=90)

        #account text under the img
        self.sign_in_label = tk.Label(self.window, text="Account", bg="#FFF8F4", fg="black",
                                    font=("yu gothic ui", 15, "bold"))
        self.sign_in_label.place(x=780, y=200)

    def create_username_widgets(self):
        self.create_label_with_icon("Username:", 550, 200, self.USERNAME_ICON_PATH)
        self.username_entry = self.create_entry_with_line(580, 235, 270)

    def create_password_widgets(self):
        self.create_label_with_icon("Password", 550, 280, self.PASSWORD_ICON_PATH)
        self.password_entry = self.create_entry_with_line(580, 316, 244, password=True)
        self.create_show_hide_button()

    def create_label_with_icon(self, text, x, y, icon_path):
        label = tk.Label(self.lgn_frame, text=text, bg="#FFF8F4", fg="#4f4e4d",
                         font=("yu gothic ui", 13, "bold"))
        label.place(x=x, y=y)
        icon = Image.open(icon_path)
        photo = ImageTk.PhotoImage(icon)
        icon_label = tk.Label(self.lgn_frame, image=photo, bg='#FFF8F4')
        icon_label.image = photo
        icon_label.place(x=x, y=y+30)

    def create_entry_with_line(self, x, y, width, password=False):
        entry = tk.Entry(self.lgn_frame, highlightthickness=0, relief=tk.FLAT, bg="#FFF8F4", fg="#6b6a69",
                         font=("yu gothic ui ", 12, "bold"), insertbackground='#6b6a69')
        entry.place(x=x, y=y, width=width)
        if password:
            entry.config(show='*')
        line = tk.Canvas(self.lgn_frame, width=300, height=2.0, bg="#bdb9b1", highlightthickness=0)
        line.place(x=x-30, y=y+24)
        return entry

    def create_show_hide_button(self):
        self.show_image = ImageTk.PhotoImage(file=self.SHOW_IMAGE_PATH)
        self.hide_image = ImageTk.PhotoImage(file=self.HIDE_IMAGE_PATH)
        self.show_button = tk.Button(self.lgn_frame, image=self.show_image, command=self.show_hide_password, relief=tk.FLAT,
                                     activebackground="#FFF8F4", borderwidth=0, background="#FFF8F4", cursor="hand2")
        self.show_button.place(x=830, y=317)

    def show_hide_password(self):
        show_char = '' if self.password_entry.cget('show') else '*'
        self.password_entry.config(show=show_char)
        image = self.hide_image if show_char else self.show_image
        self.show_button.config(image=image)

    def create_buttons(self):
        self.create_button("Login", self.login_verify, 570, 400, bg='#3047ff')
        self.create_button("Sign Up", self.open_signup_window, 570, 470, bg='#53c200')

    def create_button(self, text, command, x, y, **kwargs):
        button = tk.Button(self.lgn_frame, text=text, font=("yu gothic ui", 13, "bold"), width=25, bd=0,
                           cursor='hand2', fg='white', command=command, **kwargs)
        button.place(x=x, y=y)

    def login_verify(self):
        LoginPage.username = self.username_entry.get()
        LoginPage.password = self.password_entry.get()

        if LoginPage.username and LoginPage.password:
            db = Database()
            user = db.get_user(LoginPage.username)
            if user:
                stored_password_hash = user[1]
                stored_salt = user[2]
                input_password_hash = hashlib.pbkdf2_hmac('sha256', LoginPage.password.encode(), stored_salt.encode(), 100000).hex()

                #print("Stored: ",stored_password_hash)
                #print("Stored: ",stored_salt)
                #print("New",input_password_hash)
                if input_password_hash == stored_password_hash:
                    messagebox.showinfo("Success", "Login Success")
                    self.window.withdraw()#hide the window
                    HomePage()  # Call the home page
                else:
                    messagebox.showerror("Error", "Password Incorrect")
            else:
                messagebox.showerror("Error", "User Not Found")
        else:
            messagebox.showerror("Error", "Please enter both username and password")

    # def login_success(self):
    #     login_success_screen = tk.Toplevel(self.window)
    #     login_success_screen.title("Success")
    #     tk.Label(login_success_screen, text="Login Success").pack()
    #     tk.Button(login_success_screen, text="OK", command=login_success_screen.destroy).pack()

    def password_not_recognized(self):
        self.create_error_popup("Password Incorrect")

    def user_not_found(self):
        self.create_error_popup("User Not Found")

    def create_error_popup(self, message):
        error_screen = tk.Toplevel(self.window)
        error_screen.title("Error")
        self.center_window(error_screen, 150, 100)
        tk.Label(error_screen, text=message).pack()
        tk.Button(error_screen, text="OK", command=error_screen.destroy).pack()

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (width / 2)
        y_coordinate = (screen_height / 2) - (height / 2)
        window.geometry(f'{width}x{height}+{int(x_coordinate)}+{int(y_coordinate)}')

    def open_signup_window(self):
        SignupWindow(self.window)

class DailyJournal:
    def __init__(self, parent):
        # Constructor code here
        self.parent = parent
        self.journal_window = tk.Toplevel(self.parent)
        self.journal_window.title('Daily Journal')
        self.journal_window.resizable(0, 0)
        self.center_window(self.journal_window, 1166, 718)
        self.create_widgets()
        self.daily_protein_intake = 0
        self.daily_fat_intake = 0
        self.daily_carbs_intake = 0
        self.daily_fibre_intake = 0
        # Initialize food log
        self.food_log = {}
        self.water_log = {}  # Initialize water log dictionary
        self.weight_log = {} 

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (width / 2)
        y_coordinate = (screen_height / 2) - (height / 2)
        window.geometry(f'{width}x{height}+{int(x_coordinate)}+{int(y_coordinate)}')

    def create_widgets(self):
        bg_image = Image.open('images/background2.jpg')
        bg_photo = ImageTk.PhotoImage(bg_image)

        # Create a label to display the background image
        bg_label = tk.Label(self.journal_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create a peach-colored frame for the background
        peach_frame = tk.Frame(self.journal_window, bg='#FFF8F4', width=1000, height=600)
        peach_frame.place(x=80, y=60)

        journal_frame = tk.Frame(peach_frame, bg='#FFF8F4', width=950, height=600)
        journal_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Food Journal Entry Section
        food_journal_entry_frame = ttk.LabelFrame(journal_frame, text="Food Journal")
        food_journal_entry_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        self.create_food_journal_entry_section(food_journal_entry_frame)

        # Hydration Tracker Section
        hydration_tracker = ttk.LabelFrame(journal_frame, text="Hydration Tracker")
        hydration_tracker.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")
        self.create_hydration_tracker_section(hydration_tracker)

        # Daily Weight Log Section
        daily_weight_log = ttk.LabelFrame(journal_frame, text="Daily Weight Log")
        daily_weight_log.grid(row=0, column=2, padx=20, pady=10, sticky="nsew")
        self.create_daily_weight_section(daily_weight_log)

       # Back Button
        back_button = tk.Button(peach_frame, text="Back",font=("yu gothic ui", 13, "bold"), width=15, bd=0,cursor='hand2', fg='white',bg='#53c200', command=self.back)
        back_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

    def create_food_journal_entry_section(self, parent):
        # Load the image for the button
        food_journal_img = Image.open("images\FoodL.PNG")
        food_journal_img = food_journal_img.resize((220, 200))
        food_journal_entry_photo = ImageTk.PhotoImage(food_journal_img)

        # Create a button with the image
        food_journal_entry_button = tk.Button(parent, image=food_journal_entry_photo, command=self.show_food_journal_entry)
        food_journal_entry_button.image = food_journal_entry_photo
        food_journal_entry_button.pack(pady=0)

    def create_hydration_tracker_section(self, parent):
        # Load the image for the button
        hydration_tracker_img = Image.open("images\HydrateL.PNG")
        hydration_tracker_img = hydration_tracker_img.resize((220, 200))  
        hydration_tracker_photo = ImageTk.PhotoImage(hydration_tracker_img)

        # Create a button with the image
        hydration_tracker_button = tk.Button(parent, image=hydration_tracker_photo, command=self.show_hydration_tracker)
        hydration_tracker_button.image = hydration_tracker_photo
        hydration_tracker_button.pack(pady=0)

    def create_daily_weight_section(self, parent):
        # Load the image for the button
        daily_weight_img = Image.open("images\WeightL.PNG")
        daily_weight_img = daily_weight_img.resize((220, 200))  
        daily_weight_photo = ImageTk.PhotoImage(daily_weight_img)

        # Create a button with the image
        daily_weight_button = tk.Button(parent, image=daily_weight_photo, command=self.show_daily_weight)
        daily_weight_button.image = daily_weight_photo
        daily_weight_button.pack(pady=10)
    
    def show_food_journal_entry(self):
        # Create a new Toplevel window
        self.food_journal_entry_window = tk.Toplevel(self.journal_window)
        self.food_journal_entry_window.title("Food Journal Entry")
        self.food_journal_entry_window.resizable(0, 0)  # Make the window non-resizable
        self.center_window(self.food_journal_entry_window, 1166, 718)  # Resize the window

        # Copy the background image
        bg_image = Image.open('images/background2.jpg')
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self.food_journal_entry_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)


        # Create the peach-colored frame
        peach_frame = tk.Frame(self.food_journal_entry_window, bg='#FFF8F4', width=1000, height=700)
        peach_frame.place(x=100, y=10)

        # Create the peach-colored frame
        additional_info_frame = tk.Frame(self.food_journal_entry_window, bg='#FFF8F4', width=950, height=600)
        additional_info_frame.place(x=100, y=10)

        # Create food entry widgets within the additional info frame
        self.add_food_entry_widgets(additional_info_frame, self.food_journal_entry_window)

        # Back Button
        # back_button = ttk.Button(self.food_journal_entry_window, text="Back", command=self.food_journal_entry_window.destroy)
        # back_button.place(x=10, y=10)

    def create_bar_graph(self):
        # Destroy any existing graph frames and their contents
        for widget in self.food_journal_entry_window.winfo_children():
            if isinstance(widget, tk.Frame) and widget.winfo_name() == "graph_frame":
                widget.destroy()

        # Create a frame to hold the new graph within the food_journal_entry_window
        graph_frame = tk.Frame(self.food_journal_entry_window, name="graph_frame", bg='#FFF8F4', width=550, height=300)

        # Define the nutritional values
        nutrients = ['Protein', 'Fat', 'Carbs', 'Fibre']
        values = [self.daily_protein_intake, self.daily_fat_intake, self.daily_carbs_intake, self.daily_fibre_intake]

        # Check if all values are zero
        if all(value == 0 for value in values):
            # If all values are zero, display a label indicating that the data is not available
            error_label = tk.Label(graph_frame, text="Data not available", font=("Arial", 12), bg='#FFF8F4')
            error_label.pack()
        else:
            # Create the bar chart
            fig, ax = plt.subplots(figsize=(8, 5))  # Adjust the figure size as needed
            bars = ax.bar(nutrients, values, color=['blue', 'green', 'red', 'orange'])

            # Add labels and title
            ax.set_xlabel('Nutrients')
            ax.set_ylabel('Intake')
            ax.set_title('Daily Nutritional Intake')

            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)

            # Add text labels on top of each bar
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2.0, height, f'{value:.1f}', ha='center', va='bottom')

            # Display the plot
            plt.tight_layout()  # Adjust layout to prevent clipping of labels
            plt.savefig('bar_chart.png')  # Save the plot as an image
            plt.close()

            # Display the plot in the graph frame
            img = Image.open('bar_chart.png')
            img = img.resize((550, 300))  # Resize the image to fit the frame
            chart_img = ImageTk.PhotoImage(img)
            chart_label = tk.Label(graph_frame, image=chart_img)
            chart_label.image = chart_img
            chart_label.pack()

            # Create the pie chart
            pie_frame = tk.Frame(graph_frame, bg='#FFF8F4')
            pie_frame.pack()

            sizes = values[:]
            labels = nutrients[:]
            colors = ['gold', 'lightcoral', 'lightskyblue', 'lightgreen']

            # Check if all sizes are zero
            if all(size == 0 for size in sizes):
                # If all sizes are zero, display a label indicating that the data is not available
                error_label = tk.Label(pie_frame, text="Data not available for the Graphs", font=("Arial", 12), bg='#FFF8F4')
                error_label.pack()
            else:
                plt.figure(figsize=(6, 4))
                plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
                plt.axis('equal')
                plt.title('Macro-Nutritional Composition')

                # Display the pie chart
                plt.tight_layout()
                plt.savefig('pie_chart.png')
                plt.close()

                pie_img = Image.open('pie_chart.png')
                pie_img = pie_img.resize((550, 300))  # Resize the image to fit the frame
                pie_chart_img = ImageTk.PhotoImage(pie_img)
                pie_chart_label = tk.Label(pie_frame, image=pie_chart_img)
                pie_chart_label.image = pie_chart_img
                pie_chart_label.pack()

        # Ensure that the frame is packed within the food_journal_entry_window
        graph_frame.grid(row=0, column=2, padx=525, pady=70)  # Adjust the placement as needed

    def add_food_entry_widgets(self, parent, window):
       # Label and entry for food item
        tk.Label(parent, text="Food/Drink Item:",bg='#FFF8F4',font='Helvetica').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.food_entry = ttk.Entry(parent)
        self.food_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Label and entry for quantity
        tk.Label(parent, text="Quantity:",bg='#FFF8F4',font='Helvetica').grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.quantity_entry = ttk.Entry(parent)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Button to log food item
        tk.Button(parent, text="Log Food",width=10, cursor='hand2', fg='white',bg='#53c200',command=lambda: self.log_food(window)).grid(row=4, column= 1, padx=5, pady=5, sticky="w")

        # Back Button
        back_button = tk.Button(parent, width=10,text="Back",cursor='hand2', fg='white',bg='#060270', command=self.food_journal_entry_window.destroy)
        back_button.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        # Date picker
        tk.Label(parent, text="Select Date:",bg='#FFF8F4',font='Helvetica').grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.date_picker = ttk.Entry(parent)
        self.date_picker.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.date_picker.insert(0, datetime.now().strftime('%Y-%m-%d'))  # Set default value to current date

        # Time picker
        tk.Label(parent, text="Select Time:",bg='#FFF8F4',font='Helvetica').grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.time_picker = ttk.Combobox(parent, values=self.get_time_options(), state='readonly')
        self.time_picker.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.time_picker.set(datetime.now().strftime('%H:%M'))  # Set default value to current time

        # Section for food logged on the particular day
        tk.Label(parent, text="Food Logged Today:",bg='#FFF8F4',font='Helvetica').grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.food_logged_today = tk.Text(parent, width=50, height=10)
        self.food_logged_today.bind("<Key>", lambda e: "break")  # Disable any key presses
        self.food_logged_today.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Section for food logged within the last 7 days
        tk.Label(parent, text="Food Logged in Last 7 Days:",bg='#FFF8F4',font='Helvetica').grid(row=7, column=0, padx=5, pady=5, sticky="w")
        self.food_logged_last_week = tk.Text(parent, width=50, height=17)
        self.food_logged_last_week.bind("<Key>", lambda e: "break")  # Disable any key presses
        self.food_logged_last_week.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    # Progress bar for displaying daily calories consumed
        self.progress_bar = ttk.Progressbar(parent, orient="horizontal", length=560, mode="determinate")
        self.progress_bar.grid(row=0, column=2, padx=10, pady=10)

        # # Label for displaying the percentage achieved
        self.percentage_label = ttk.Label(parent, background="#06b025")
        self.percentage_label.place(x=700, y=12)

        # Set the default maximum value of the progress bar
        self.progress_bar['maximum'] = 2250

        # Update the food logged sections
        self.update_food_sections()

    def get_time_options(self):
            # Generate time options from 00:00 to 23:45 in 15-minute intervals
            time_options = [(datetime.min + timedelta(minutes=i)).strftime('%H:%M') for i in range(0, 1440, 15)]
            return time_options
    
    def log_food(self, window):
        db = Database()
        food_item = self.food_entry.get()
        quantity = self.quantity_entry.get()
        selected_date = self.date_picker.get()
        selected_time = self.time_picker.get()

        # Validate input
        if not food_item or not quantity:
            messagebox.showerror("Error", "Please enter both food item and quantity.")
            return

        # Combine date and time into a datetime object
        selected_datetime = datetime.strptime(f"{selected_date} {selected_time}", '%Y-%m-%d %H:%M')

        # Check if the selected datetime is within the valid range (not more than 7 days ago and not in the future)
        valid_range = timedelta(days=7)
        current_datetime = datetime.now()
        if selected_datetime < current_datetime - valid_range:
            messagebox.showerror("Error", "Selected date and time cannot be more than 7 days ago.")
            return
        elif selected_datetime > current_datetime:
            messagebox.showerror("Error", "Selected date and time cannot be in the future.")
            return

        # Retrieve nutritional information using Edamam Food Database API
        nutritional_info = self.get_nutritional_info(food_item, quantity)

        if nutritional_info:
            try:
                username_value = LoginPage.username
            except AttributeError:
                username_value = SignupWindow.username

            calories = nutritional_info['ENERC_KCAL']
            protein = nutritional_info['PROCNT']
            fat = nutritional_info['FAT']
            carbs = nutritional_info['CHOCDF']
            fibre = nutritional_info['FIBTG']

            # Add food log entry to the database
            db.populate_food_log(username_value, selected_datetime, food_item, quantity, calories, protein, fat, carbs,
                                fibre)

            # Clear input fields
            self.food_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)

            # Update sections with logged food items
            self.update_food_sections()

            messagebox.showinfo("Success", "Food logged successfully.")
        else:
            messagebox.showerror("Error", f"Nutritional information for '{food_item}' not found.")

    def update_food_sections(self, window=None):
        # Clear existing content in text widgets
        self.food_logged_today.delete(1.0, tk.END)
        self.food_logged_last_week.delete(1.0, tk.END)
        db = Database()
        try:
            username_value = LoginPage.username
        except AttributeError:
            username_value = SignupWindow.username
        
        # Reset daily nutritional intake values to zero
        self.daily_protein_intake = 0
        self.daily_fat_intake = 0
        self.daily_carbs_intake = 0
        self.daily_fibre_intake = 0
        
        # Retrieve logged food items from the database
        # Call the get_food_log method to retrieve food logs for the specified user
        food_logs = db.get_food_log(username_value)
        
        # Get today's date
        today_date = datetime.today().date()
        
        # Get the date 7 days ago
        last_week_date = today_date - timedelta(days=7)

        daily_calory_intake=0

        # Format and insert today's entries into the text widget
        today_entries = []
        for entry in food_logs:
            entry_datetime = datetime.strptime(entry[1], '%Y-%m-%d %H:%M:%S')  # Parse datetime string
            entry_date = entry_datetime.date()
            if entry_date == today_date:
                daily_calory_intake= entry[4]+daily_calory_intake
                self.daily_protein_intake += entry[5]
                self.daily_fat_intake += entry[6]
                self.daily_carbs_intake += entry[7]
                self.daily_fibre_intake += entry[8]
                formatted_entry = f"{entry[3]} {entry[2]} {entry[1]}"  # Format the entry
                today_entries.append(formatted_entry)
        if today_entries:
            self.food_logged_today.insert(tk.END, "\n".join(today_entries))

        # Format and insert entries from last week into the text widget
        last_week_entries = []
        for entry in food_logs:
            entry_datetime = datetime.strptime(entry[1], '%Y-%m-%d %H:%M:%S')  # Parse datetime string
            entry_date = entry_datetime.date()
            if last_week_date <= entry_date < today_date:
                formatted_entry = f"{entry[3]} {entry[2]} {entry[1]}"  # Format the entry
                last_week_entries.append(formatted_entry)
        if last_week_entries:
            self.food_logged_last_week.insert(tk.END, "\n".join(last_week_entries))

        # Update the progress bar
        self.update_progress_bar(daily_calory_intake)
        self.create_bar_graph()

    def update_progress_bar(self, total_daily_calories):
        # Update the progress bar based on total calories consumed today
        self.progress_bar['value'] = min(total_daily_calories, self.progress_bar['maximum'])

        # Calculate percentage achieved
        percentage_achieved = int((total_daily_calories / self.progress_bar['maximum']) * 100)
        
        # Dynamically set the background color of the label based on progress
        if percentage_achieved < 49:
            bg_color = "#e6e6e6"
        else:
            bg_color = "#06b025"  # Green color

        # Update the label showing the percentage
        self.percentage_label.config(text=f"{percentage_achieved}%", font=("Helvetica", 8), background=bg_color)

        # Configure a custom style for the progress bar
        style = ttk.Style()
        style.layout("Custom.Horizontal.TProgressbar",
                    [('Custom.Horizontal.Progressbar.trough',
                    {'children': [('Custom.Horizontal.Progressbar.pbar',
                                    {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'nswe'}),
                    ('Custom.Horizontal.Progressbar.label', {'sticky': ''})])

        # Apply the custom style to the progress bar
        self.progress_bar['style'] = "Custom.Horizontal.TProgressbar"

    def get_nutritional_info(self, food_item, quantity):
        # Replace 'YOUR_APP_ID' and 'YOUR_APP_KEY' with your actual Edamam API credentials
        api_url = f"https://api.edamam.com/api/food-database/v2/parser?ingr={quantity}%20{food_item}&app_id=3b52434d&app_key=0bffeded1a2736b694084de83bc09a87"
        
        try:
            response = requests.get(api_url)
            data = response.json()
            #print(data)
            if 'hints' in data and data['hints']:
                # Retrieving nutritional information for the first matched item
                nutritional_info = data['hints'][0]['food']['nutrients']
                return nutritional_info
            else:
                return None
        except Exception as e:
            print("Error occurred:", e)
            return None

    def show_hydration_tracker(self):
        # Create a new Toplevel window for hydration tracker
        self.hydration_tracker_window = tk.Toplevel(self.journal_window)
        self.hydration_tracker_window.title("Hydration Tracker")
        self.hydration_tracker_window.resizable(0, 0)  # Make the window non-resizable
        self.center_window(self.hydration_tracker_window, 1166, 718)  # Resize the window

        # Copy the background image
        bg_image = Image.open('images/background2.jpg')
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self.hydration_tracker_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create the peach-colored frame
        peach_frame = tk.Frame(self.hydration_tracker_window, bg='#FFF8F4', width=1050, height=700)
        peach_frame.place(x=100, y=10)

        # Create the peach-colored frame
        additional_info_frame = tk.Frame(self.hydration_tracker_window, bg='#FFF8F4', width=950, height=600)
        additional_info_frame.place(x=100, y=10)

        # Create hydration entry widgets within the additional info frame
        self.add_hydration_entry_widgets(additional_info_frame, self.hydration_tracker_window)

        # Update the display of logged water intake
        self.update_water_logged_sections(self.hydration_tracker_window)

        # Display the hydration graph
        self.create_hydration_graph(self.hydration_tracker_window)

    def create_hydration_graph(self, parent):
        # Destroy any existing graph frames and their contents
        for widget in parent.winfo_children():
            if isinstance(widget, tk.Frame) and widget.winfo_name() == "hydration_graph_frame":
                widget.destroy()

        # Create a frame to hold the new graph within the parent window
        graph_frame = tk.Frame(parent, name="hydration_graph_frame", bg='#FFF8F4', width=600, height=400)

        # Extract data from sums_per_date dictionary
        days = [date.strftime('%Y-%m-%d') for date in self.sums_per_date.keys()]
        actual_intake = list(self.sums_per_date.values())

        # Plotting the graph
        plt.figure(figsize=(10, 6))

        # Plot threshold line
        plt.plot(days, [2000] * len(days), linestyle='-', color='blue', label='Threshold')

        # Plot actual intake
        plt.plot(days, actual_intake, marker='s', linestyle='-', color='red', label='Actual Intake')

        # Annotate each point with its corresponding value
        for i, value in enumerate(actual_intake):
            plt.text(days[i], value, str(value), ha='center', va='bottom', fontsize=8)

        # Shade areas between lines
        plt.fill_between(days, actual_intake, 2000, where=(np.array(actual_intake) >= 2000), color='yellow', alpha=0.5)
        plt.fill_between(days, actual_intake, 2000, where=(np.array(actual_intake) < 2000), color='lightgreen', alpha=0.5)

        plt.xlabel('Days')
        plt.ylabel('Water Intake (ml)')
        plt.title('Weekly Hydration Tracker')
        plt.legend()
        plt.grid(True)

        # Display the graph
        plt.tight_layout()
        plt.savefig('hydration_tracker_graph.png')  # Save the plot as an image
        plt.close()

        # Display the plot in the graph frame
        img = Image.open('hydration_tracker_graph.png')
        img = img.resize((600, 400))  # Resize the image to fit the frame
        chart_img = ImageTk.PhotoImage(img)
        chart_label = tk.Label(graph_frame, image=chart_img)
        chart_label.image = chart_img
        chart_label.pack()

        # Ensure that the frame is packed within the parent window
        graph_frame.grid(row=0, column=1, padx=525, pady=150)

    def add_hydration_entry_widgets(self, parent, window):
        # Label and entry for fluid intake
        tk.Label(parent, text="Fluid Intake (ml):", bg='#FFF8F4', font='Helvetica').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.fluid_intake_entry = ttk.Entry(parent)
        self.fluid_intake_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Button to log hydration
        tk.Button(parent, text="Log Hydration", cursor='hand2', fg='white', bg='#53c200', command=lambda: self.log_water_intake(window)).grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Back Button
        back_button = tk.Button(parent, width=10, text="Back", cursor='hand2', fg='white', bg='#060270', command=self.hydration_tracker_window.destroy)
        back_button.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        # Date picker
        tk.Label(parent, text="Select Date:", bg='#FFF8F4', font='Helvetica').grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.hydration_date_picker = ttk.Entry(parent)
        self.hydration_date_picker.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.hydration_date_picker.insert(0, datetime.now().strftime('%Y-%m-%d'))  # Set default value to current date

        # Time picker
        tk.Label(parent, text="Select Time:", bg='#FFF8F4', font='Helvetica').grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.hydration_time_picker = ttk.Combobox(parent, values=self.get_time_options(), state='readonly')
        self.hydration_time_picker.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.hydration_time_picker.set(datetime.now().strftime('%H:%M'))  # Set default value to current time

        # Section for water intake logged on the particular day
        tk.Label(parent, text="Water Intake Logged Today:", bg='#FFF8F4', font='Helvetica').grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.water_logged_today = tk.Text(parent, width=50, height=10)
        self.water_logged_today.bind("<Key>", lambda e: "break")  # Disable any key presses
        self.water_logged_today.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Section for water intake logged within the last 7 days
        tk.Label(parent, text="Water Intake Logged in Last 7 Days:", bg='#FFF8F4', font='Helvetica').grid(row=8, column=0, padx=5, pady=5, sticky="w")
        self.water_logged_last_week = tk.Text(parent, width=50, height=17)
        self.water_logged_last_week.bind("<Key>", lambda e: "break")  # Disable any key presses
        self.water_logged_last_week.grid(row=9, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Progress bar for displaying daily calories consumed
        self.water_progress_bar = ttk.Progressbar(parent, orient="horizontal", length=560, mode="determinate")
        self.water_progress_bar.grid(row=0, column=4, padx=10, pady=10)

        # Label for displaying the percentage achieved
        self.water_percentage_label = ttk.Label(parent, background="#06b025")
        self.water_percentage_label.place(x=700, y=12)

        # Set the default maximum value of the progress bar
        self.water_progress_bar['maximum'] = 5000

        # Update the progress bar initially
        # self.update_water_progress_bar()

    def update_water_logged_sections(self, parent):
        # Clear the text widgets first
        self.water_logged_today.delete(1.0, tk.END)
        self.water_logged_last_week.delete(1.0, tk.END)

        db = Database()
        try:
            username_value = LoginPage.username
        except AttributeError:
            username_value = SignupWindow.username

        # Retrieve logged water intake from the database
        water_logs = db.get_water_intake(username_value)
        #print(water_logs)

        # Get today's date
        today_date = datetime.today().date()

        # Get the date 7 days ago
        last_week_date = today_date - timedelta(days=7)

        daily_water_intake = 0

        # Format and insert today's entries into the text widget
        today_water_entries = []
        for entry in water_logs:
            entry_datetime = datetime.strptime(entry[1], '%Y-%m-%d %H:%M:%S')  # Parse datetime string
            entry_date = entry_datetime.date()
            if entry_date == today_date:
                daily_water_intake = daily_water_intake + entry[2]
                formatted_entry = f"{entry_datetime.strftime('%Y-%m-%d %H:%M')}: {entry[2]} ml"  # Format the entry
                today_water_entries.append(formatted_entry)
        if today_water_entries:
            self.water_logged_today.insert(tk.END, "\n".join(today_water_entries))

        # Dictionary to store sums for each date
        sums_per_date = {}
        # Initialize dates for the past 7 days except today
        for i in range(1, 8):
            date = today_date - timedelta(days=i)
            sums_per_date[date] = 0

        # Format and insert entries from last week into the text widget
        last_week_water_entries = []
        for entry in water_logs:
            entry_datetime = datetime.strptime(entry[1], '%Y-%m-%d %H:%M:%S')  # Parse datetime string
            entry_date = entry_datetime.date()
            if last_week_date <= entry_date < today_date:
                formatted_entry = f"{entry_datetime.strftime('%Y-%m-%d %H:%M')}: {entry[2]} ml"  # Format the entry
                last_week_water_entries.append(formatted_entry)
                if entry_date not in sums_per_date:
                    sums_per_date[entry_date] = 0
                sums_per_date[entry_date] += entry[2]

        if last_week_water_entries:
            self.water_logged_last_week.insert(tk.END, "\n".join(last_week_water_entries))

        # Update the progress bar initially
        self.update_water_progress_bar(daily_water_intake)
         # Store sums_per_date as an attribute of the class
        self.sums_per_date = sums_per_date
         # Display the hydration graph
        self.create_hydration_graph(parent)

    def log_water_intake(self, window):
        db = Database()
        water_amount = self.fluid_intake_entry.get()
        selected_date = self.hydration_date_picker.get()
        selected_time = self.hydration_time_picker.get()

        # Validate input
        if not water_amount:
            messagebox.showerror("Error", "Please enter the amount of water intake.")
            return
        # Validate input
        if not water_amount.isdigit() or int(water_amount) <= 0:
            messagebox.showerror("Error", "Please enter a positive integer value for fluid intake.")
            return

        # Combine date and time into a datetime object
        selected_datetime = datetime.strptime(f"{selected_date} {selected_time}", '%Y-%m-%d %H:%M')

        # Check if the selected datetime is within the valid range
        valid_range = timedelta(days=7)
        current_datetime = datetime.now()
        if selected_datetime < current_datetime - valid_range:
            messagebox.showerror("Error", "Selected date and time cannot be more than 7 days ago.")
            return
        elif selected_datetime > current_datetime:
            messagebox.showerror("Error", "Selected date and time cannot be in the future.")
            return

        try:
            username_value = LoginPage.username
        except AttributeError:
            username_value = SignupWindow.username

        # Add water intake log entry to the database
        db.log_water_intake(username_value, selected_datetime, water_amount)

        # Update the logged water intake dictionaries
        if selected_date not in self.water_log:
            self.water_log[selected_date] = []

        self.water_log[selected_date].append({"amount": water_amount, "timestamp": selected_datetime})

        # Update sums_per_date dictionary with the new data
        if selected_datetime.date() not in self.sums_per_date:
            self.sums_per_date[selected_datetime.date()] = 0

        self.sums_per_date[selected_datetime.date()] += int(water_amount)

        # Update the display of logged water intake and hydration graph
        self.update_water_logged_sections(window)

        # Clear input fields
        self.fluid_intake_entry.delete(0, tk.END)
        self.hydration_date_picker.delete(0, tk.END)
        self.hydration_date_picker.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.hydration_time_picker.set(datetime.now().strftime('%H:%M'))

        messagebox.showinfo("Success", "Water intake logged successfully.")

    def update_water_progress_bar(self,daily_water_intake):
        # Calculate total water intake logged for the day
        for entry in self.water_log.get(datetime.today().strftime('%Y-%m-%d'), []):
            daily_water_intake += int(entry["amount"])

        # Update the progress bar value
        self.water_progress_bar["value"] = min(daily_water_intake, self.water_progress_bar["maximum"])

        # Calculate percentage achieved
        percentage_achieved = int((daily_water_intake / self.water_progress_bar["maximum"]) * 100)

        # Dynamically set the background color of the label based on progress
        if percentage_achieved < 49:
            bg_color = "#e6e6e6"
        else:
            bg_color = "#06b025"  # Green color

        # Update the label showing the percentage
        self.water_percentage_label.config(text=f"{percentage_achieved}%", font=("Helvetica", 8), background=bg_color)

        # Configure a custom style for the progress bar if needed
        style = ttk.Style()
        style.layout("Water.Horizontal.TProgressbar",
                    [('Water.Horizontal.Progressbar.trough',
                    {'children': [('Water.Horizontal.Progressbar.pbar',
                                    {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'nswe'}),
                    ('Water.Horizontal.Progressbar.label', {'sticky': ''})])

        # Apply the custom style to the progress bar if needed
        self.water_progress_bar["style"] = "Water.Horizontal.TProgressbar"

    def show_daily_weight(self):
        # Create a new Toplevel window for daily weight tracker
        self.daily_weight_window = tk.Toplevel(self.journal_window)
        self.daily_weight_window.title("Daily Weight Tracker")
        self.daily_weight_window.resizable(0, 0)  # Make the window non-resizable
        self.center_window(self.daily_weight_window, 1166, 718)  # Resize the window

        # Copy the background image (assuming you have a background image)
        bg_image = Image.open('images/background2.jpg')  # Adjust the path accordingly
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self.daily_weight_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create the peach-colored frame
        peach_frame = tk.Frame(self.daily_weight_window, bg='#FFF8F4', width=1050, height=700)
        peach_frame.place(x=100, y=10)

        # Create the frame for weight entry
        weight_entry_frame = tk.Frame(self.daily_weight_window, bg='#FFF8F4', width=950, height=600)
        weight_entry_frame.place(x=100, y=10)

        # Add weight entry widgets within the weight entry frame
        self.add_weight_entry_widgets(weight_entry_frame)

        self.update_weight_logged_sections()

        self.create_weight_check_in_graph(self.daily_weight_window)

    def create_weight_check_in_graph(self, parent):
        try:
            # Destroy any existing graph frames and their contents
            for widget in parent.winfo_children():
                if isinstance(widget, tk.Frame) and widget.winfo_name() == "weight_check_in_graph_frame":
                    widget.destroy()

            # Create a frame to hold the new graph within the parent window
            graph_frame = tk.Frame(parent, name="weight_check_in_graph_frame", bg='#FFF8F4', width=600, height=400)

            # Extract data from weight_entries_per_date dictionary
            dates = list(self.weight_entries_per_date.keys())
            weights = list(self.weight_entries_per_date.values())

            # Filter out None values
            valid_dates = []
            valid_weights = []
            for date, weight in zip(dates, weights):
                if weight is not None:
                    valid_dates.append(date)
                    valid_weights.append(weight)

            if not valid_weights:
                # If valid_weights is empty, display message on the window
                message_label = tk.Label(graph_frame, text="No valid weights found.", fg="red")
                message_label.pack()
                # Ensure that the frame is packed within the parent window
                graph_frame.grid(row=0, column=2, padx=525, pady=150)
                return
            
            # Plotting the graph
            fig, ax = plt.subplots(figsize=(10, 6))

            # Plot weight data
            ax.plot(valid_dates, valid_weights, marker='o', linestyle='-', color='Slateblue', alpha=0.6, label='Weight')

            # Shade the area underneath the points
            ax.fill_between(valid_dates, valid_weights, color='skyblue', alpha=0.4)

            ax.set_xlabel('Date')
            ax.set_ylabel('Weight (kg)')
            ax.set_title('Weight Check-in')
            ax.legend()
            ax.grid(True)

            # Calculate y-axis range dynamically based on user's weight data with padding
            min_weight = min(valid_weights) - 5
            max_weight = max(valid_weights) + 5
            ax.set_ylim(min_weight, max_weight)

            # Save the plot as an image
            plt.tight_layout()
            plt.savefig('weight_check_in_graph.png')  
            plt.close()

            # Display the plot in the graph frame
            img = Image.open('weight_check_in_graph.png')
            img = img.resize((600, 400))  # Resize the image to fit the frame
            chart_img = ImageTk.PhotoImage(img)
            chart_label = tk.Label(graph_frame, image=chart_img)
            chart_label.image = chart_img
            chart_label.pack()

            # Ensure that the frame is packed within the parent window
            graph_frame.grid(row=0, column=1, padx=525, pady=150)

        except Exception as e:
            # Handle the error gracefully, for example, printing an error message
            print(f"An error occurred: {e}")

    def add_weight_entry_widgets(self, parent):
        # Label and entry for weight
        tk.Label(parent, text="Weight (kg):",bg='#FFF8F4',font='Helvetica').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.weight_entry = ttk.Entry(parent)
        self.weight_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Button to log weight
        tk.Button(parent, text="Log Weight",width=10,cursor='hand2', fg='white',bg='#53c200', command=self.log_weight).grid(row=2, column=1, padx=5, pady=5, sticky="w")

        #Back Button
        back_button = tk.Button(parent, text="Back",width=10,cursor='hand2', fg='white',bg='#060270', command=self.daily_weight_window.destroy)
        back_button.grid(row=2,column=0,padx=5, pady=5, sticky="w")

        # Date picker
        tk.Label(parent, text="Select Date:",bg='#FFF8F4',font='Helvetica').grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.weight_date_picker = ttk.Entry(parent)
        self.weight_date_picker.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.weight_date_picker.insert(0, datetime.now().strftime('%Y-%m-%d'))  # Set default value to current date

       # Section for weight logged on the particular day
        tk.Label(parent, text="Weight Logged Today:",bg='#FFF8F4',font='Helvetica').grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.weight_logged_today = tk.Text(parent, width=50, height=10)
        self.weight_logged_today.bind("<Key>", lambda e: "break")  # Disable any key presses
        self.weight_logged_today.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Section for weight logged within the last 7 days
        tk.Label(parent, text="Weight Logged in Last 7 Days:",bg='#FFF8F4',font='Helvetica').grid(row=7, column=0, padx=5, pady=5, sticky="w")
        self.weight_logged_last_week = tk.Text(parent, width=50, height=17)
        self.weight_logged_last_week.bind("<Key>", lambda e: "break")  # Disable any key presses
        self.weight_logged_last_week.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        status_label=tk.Label(parent, text="Status:",bg='#FFF8F4',font='Helvetica')
        status_label.grid(row= 3, column=0,padx=5,pady=5,sticky="w")

        # Add this line to your add_weight_entry_widgets method to create the signaling box
        self.signaling_box = tk.Label(parent)
        self.signaling_box.grid(row=3, column=1, rowspan=2, padx=5, pady=5,sticky="w")
        # Initialize the signaling box color to red
        self.signaling_box.config(bg='#FF898F',text="❌DAILY WEIGHT NOT RECORDED❌",font='Helvetica')

    def log_weight(self):
        weight_value = self.weight_entry.get()
        selected_date = self.weight_date_picker.get()

        # Validate input
        if not weight_value:
            messagebox.showerror("Error", "Please enter the weight.")
            return
        if not weight_value.isdigit() or int(weight_value) <= 0:
            messagebox.showerror("Error", "Please enter a positive integer value for weight.")
            return

        try:
            username_value = LoginPage.username
        except AttributeError:
            username_value = SignupWindow.username

        # Validate date
        try:
            selected_datetime = datetime.strptime(selected_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use the format YYYY-MM-DD.")
            return

        # Check if the selected date is in the future or more than 7 days backdated
        valid_range = timedelta(days=7)
        current_datetime = datetime.now()
        if selected_datetime > current_datetime:
            messagebox.showerror("Error", "Selected date cannot be in the future.")
            return
        elif current_datetime - selected_datetime > valid_range:
            messagebox.showerror("Error", "Selected date cannot be more than 7 days ago.")
            return

        # Check if the weight entry already exists for the selected date
        db = Database()
        if db.check_weight_entry(username_value, selected_date):
            messagebox.showerror("Error", "Weight entry already exists for this date.")
            return

        # Add the weight entry to the database
        db.log_weight(username_value, selected_date, weight_value)

        # Update the logged weights dictionary
        self.weight_log[selected_date] = [{"weight": weight_value}]

        # Update the display of logged weights
        self.update_weight_logged_sections()

        # Clear input fields
        self.weight_entry.delete(0, tk.END)
        self.weight_date_picker.delete(0, tk.END)
        self.weight_date_picker.insert(0, datetime.now().strftime('%Y-%m-%d'))

        messagebox.showinfo("Success", "Weight logged successfully.")

    def update_weight_logged_sections(self):
        # Clear the text widgets first
        self.weight_logged_today.delete(1.0, tk.END)
        self.weight_logged_last_week.delete(1.0, tk.END)

        db = Database()
        try:
            username_value = LoginPage.username
        except AttributeError:
            username_value = SignupWindow.username

        # Retrieve logged weight entries from the database
        weight_logs = db.get_weight_log(username_value)

        # Get today's date
        today_date = datetime.today().date()

        # Get the date 7 days ago
        last_week_date = today_date - timedelta(days=7)

        # Format and insert today's entries into the text widget
        today_weight_entries = []
        for entry in weight_logs:
            entry_date = datetime.strptime(entry[1], '%Y-%m-%d').date()  # Extract date from timestamp
            if entry_date == today_date:
                formatted_entry = f"{entry_date.strftime('%Y-%m-%d')}: {entry[2]} kg"  # Format the entry
                today_weight_entries.append(formatted_entry)
        if today_weight_entries:
            # Initialize the signaling box color to red
            self.signaling_box.config(bg='#7DDA58',text="✔DAILY WEIGHT RECORDED✔",font='Helvetica')
            self.weight_logged_today.insert(tk.END, "\n".join(today_weight_entries))

        # Format and insert entries from last week into the text widget
        # Initialize variables
        last_week_weight_entries = []
        weight_entries_per_date = {}

        # Loop through weight logs
        for entry in weight_logs:
            entry_date = datetime.strptime(entry[1], '%Y-%m-%d').date()  # Extract date from timestamp
            
            # Check if entry date is within last week
            if last_week_date <= entry_date < today_date:
                # Format and append entry to last week entries list
                last_week_weight_entries.append(f"{entry_date.strftime('%Y-%m-%d')}: {entry[2]} kg")
            
            # Store weight entry per date
            if last_week_date <= entry_date < today_date:
                weight_entries_per_date[entry_date.strftime('%Y-%m-%d')] = entry[2]

        # Insert last week weight entries into text widget
        if last_week_weight_entries:
            self.weight_logged_last_week.insert(tk.END, "\n".join(last_week_weight_entries))

        # Sort weight entries per date in chronological order
        sorted_weight_entries_per_date = dict(sorted(weight_entries_per_date.items()))

        # Print sorted weight entries per date
        self.weight_entries_per_date = sorted_weight_entries_per_date
        #print(sorted_weight_entries_per_date)
        
        self.create_weight_check_in_graph(self.daily_weight_window)

    def back(self):
        # Define the action when the back button is clicked
        self.journal_window.destroy()  # Close the journal window

class SettingsPage:
    def __init__(self, parent):
        self.parent = parent
        self.settings_window = tk.Toplevel(self.parent)
        self.settings_window.title('Settings')
        self.settings_window.resizable(0, 0)
        self.center_window(self.settings_window, 1166, 718)
        self.create_widgets()

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x_coordinate = (screen_width / 2) - (width / 2)
        y_coordinate = (screen_height / 2) - (height / 2)
        window.geometry(f'{width}x{height}+{int(x_coordinate)}+{int(y_coordinate)}')

    def create_widgets(self):
        bg_image = Image.open('images/background2.jpg')
        bg_photo = ImageTk.PhotoImage(bg_image)

        # Create a label to display the background image
        bg_label = tk.Label(self.settings_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create a peach-colored frame for the background
        peach_frame = tk.Frame(self.settings_window, bg='#FFF8F4', width=1000, height=600)
        peach_frame.place(x=80, y=60)

        settings_frame = tk.Frame(peach_frame, bg='#FFF8F4', width=950, height=600)
        settings_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Personal Information Section
        personal_info_frame = ttk.LabelFrame(settings_frame, text="Edit Personal Information")
        personal_info_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        self.create_personal_info_section(personal_info_frame)

        # Change Password Section
        change_password_frame = ttk.LabelFrame(settings_frame, text="Change Password")
        change_password_frame.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")
        self.create_change_password_section(change_password_frame)

        # Feedback and Support Section
        feedback_support_frame = ttk.LabelFrame(settings_frame, text="Feedback and Support")
        feedback_support_frame.grid(row=0, column=2, padx=20, pady=10, sticky="nsew")
        self.create_feedback_support_section(feedback_support_frame)

       # Button
        back_button = tk.Button(peach_frame, text="Back", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                                cursor='hand2', fg='white', command=self.back, bg='#3047ff')
        back_button.place(relx=0.4, rely=0.8, anchor=tk.CENTER)

        logout_button = tk.Button(peach_frame, text="Log Out", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=self.log_out, bg='#53c200')
        logout_button.place(relx=0.6, rely=0.8, anchor=tk.CENTER)

    def create_personal_info_section(self, parent):
        # Load the image for the button
        prsnl_info_img = Image.open("images\prsnl_info.png")
        prsnl_info_img = prsnl_info_img.resize((220, 200))
        prsnl_info_photo = ImageTk.PhotoImage(prsnl_info_img)

        # Create a button with the image
        prsnl_info_button = tk.Button(parent, image=prsnl_info_photo, command=self.show_personal_info)
        prsnl_info_button.image = prsnl_info_photo
        prsnl_info_button.pack(pady=0)

    def show_personal_info(self):
        db = Database()
        try:
            username_value = LoginPage.username
            print(f"Username: {username_value}")
            user_info = db.get_user(LoginPage.username)
            password = LoginPage.password
        except AttributeError:
            print("AttributeError: LoginPage.username is not defined or does not exist")
            user_info = db.get_user(SignupWindow.username)
            password = SignupWindow.password

        if user_info:
            print(user_info)

            # Create a new window to display personal information
            personal_info_window = tk.Toplevel(self.settings_window)
            personal_info_window.title("Personal Information")

            # Center the window
            window_width = 1166
            window_height = 718
            screen_width = personal_info_window.winfo_screenwidth()
            screen_height = personal_info_window.winfo_screenheight()
            x_coordinate = (screen_width - window_width) // 2
            y_coordinate = (screen_height - window_height) // 2
            personal_info_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

            # Load background image
            bg_image = Image.open('images/background2.jpg')
            bg_photo = ImageTk.PhotoImage(bg_image)

            # Create a label to display the background image
            bg_label = tk.Label(personal_info_window, image=bg_photo)
            bg_label.image = bg_photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

            additional_info_frame = tk.Frame(personal_info_window, bg='#FFF8F4', width=950, height=600)
            additional_info_frame.place(x=100, y=50)

            # Create a peach-colored frame for the background
            peach_frame = tk.Frame(personal_info_window, bg='#FFF8F4', width=1000, height=600)
            peach_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            # Display personal information fields
            tk.Label(peach_frame, text="Personal Information", font=("Helvetica", 20, "bold"),bg='#FFF8F4').grid(row=0, column= 0)

            # Define the order of fields according to the database
            fields = ["Name", "Age", "Gender", "Weight(kg)", "Height(cm)", "Lifestyle", "Water Intake", "Goals"]
            values = user_info[3:]  # Skip the username

            for i,(field,value) in enumerate(zip(fields, values)):
                tk.Label(peach_frame, text=f"{field}:", font=("Helvetica", 14), anchor="w",bg='#FFF8F4').grid(row=i+1, column=0, padx=5, pady=5, sticky="w")
                tk.Label(peach_frame, text=value, font=("Helvetica", 14), anchor="w", fg="#333333",bg='#FFF8F4').grid(row=i+1, column=1, padx=5, pady=5, sticky="w")

            # Provide options to edit this information
            edit_button =tk.Button(peach_frame, text="Edit Information", command=lambda: self.edit_personal_info(user_info),cursor='hand2', fg='white',bg='#2596be',font=("Helvetica", 16))
            edit_button.grid(row=i + 2, column=0, columnspan=2, pady=5)
            # Back Button
            
            back_button = tk.Button(peach_frame, text="Back", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=personal_info_window.destroy, bg='#53c200')
            back_button.grid(row=i + 3, column=0,columnspan=2, pady=5)
        else:
            messagebox.showerror("Error", "User not found.")

    def edit_personal_info(self, user_info):
        # Destroy all widgets in the current window
        for widget in self.settings_window.winfo_children():
            widget.destroy()

        # Load background image
        bg_image = Image.open('images/background2.jpg')
        bg_photo = ImageTk.PhotoImage(bg_image)

        # Create a label to display the background image
        bg_label = tk.Label(self.settings_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        additional_info_frame = tk.Frame(self.settings_window, bg='#FFF8F4', width=950, height=600)
        additional_info_frame.place(x=100, y=50)

        # Create a peach-colored frame for the background
        peach_frame = tk.Frame(self.settings_window, bg='#FFF8F4', width=1000, height=600)
        peach_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Display personal information fields for editing
        tk.Label(peach_frame, bg='#FFF8F4',text="Edit Personal Information", font=("Helvetica", 20, "bold")).grid(row=0, column= 0)

        # Define the order of fields according to the database
        fields = ["First Name:", "Age:", "Gender:", "Weight(kg):", "Height(cm):", "Current Lifestyle:", "Avg Daily Water Intake:", "Future Goals:"]
        values = user_info[3:]  # Skip the username

        entries = []

        for i,(field, value) in enumerate(zip(fields, values)):
            if field in ["Gender:", "Current Lifestyle:", "Avg Daily Water Intake:", "Future Goals:"]:
                tk.Label(peach_frame, text=field,bg='#FFF8F4',font=("Helvetica", 14)).grid(row=i+1, column=0, padx=5, pady=5, sticky="w")

                # Create comboboxes for Gender, Lifestyle, Water Intake, and Future Goals
                if field == "Gender:":
                    gender_var = tk.StringVar(value=value)
                    gender_combobox = ttk.Combobox(peach_frame, textvariable=gender_var, values=["Male", "Female"], state="readonly")
                    gender_combobox.grid(row=i+1, column=1, padx=5, pady=5, sticky="w")

                    entries.append(gender_var)

                elif field == "Current Lifestyle:":
                    lifestyle_var = tk.StringVar(value=value)
                    lifestyle_combobox = ttk.Combobox(peach_frame, textvariable=lifestyle_var, values=["Sedentary", "Light", "Moderate", "Active"], state="readonly")
                    lifestyle_combobox.grid(row=i+1, column=1, padx=5, pady=5, sticky="w")

                    entries.append(lifestyle_var)

                elif field == "Avg Daily Water Intake:":
                    water_intake_var = tk.StringVar(value=value)
                    water_intake_combobox = ttk.Combobox(peach_frame, textvariable=water_intake_var, values=["Less than 1L", "1-2L", "2-4L", "4-6L", "6-8L", "More than 8L"], state="readonly")
                    water_intake_combobox.grid(row=i+1, column=1, padx=5, pady=5, sticky="w")

                    entries.append(water_intake_var)

                elif field == "Future Goals:":
                    goals_var = tk.StringVar(value=value)
                    goals_combobox = ttk.Combobox(peach_frame, textvariable=goals_var, values=["Weight Loss", "Maintenance", "Muscle Gain", "Performance"], state="readonly")
                    goals_combobox.grid(row=i+1, column=1, padx=5, pady=5, sticky="w")

                    entries.append(goals_var)
            else:
                tk.Label(peach_frame, text=field,bg='#FFF8F4',font=("Helvetica", 14)).grid(row=i+1, column=0, padx=5, pady=5, sticky="w")
                entry = tk.Entry(peach_frame)
                entry.insert(tk.END, value)
                entry.grid(row=i+1, column=1, padx=5, pady=5, sticky="w")
                entries.append(entry)

        def save_changes():
            # Retrieve updated information from entry fields
            updated_info = []
            error_message = None

            for entry in entries:
                if isinstance(entry, tk.Entry):
                    value = entry.get()
                    updated_info.append(value)
                    if not value:
                        error_message = f"Please enter {field.strip(':')}"

                    # Additional checks if needed
                    if field == "Age:":
                        if not value.isdigit() or int(value) <= 0 or int(value) > 120:
                            error_message = "Please enter a valid age"

                    elif field == "Weight(kg):":
                        if not value.isdigit() or int(value) <= 0 or int(value) > 600:
                            error_message = "Please enter a valid weight"

                    elif field == "Height(cm):":
                        if not value.isdigit() or int(value) <= 0 or int(value) > 250:
                            error_message = "Please enter a valid height"

                else:
                    updated_info.append(entry.get())

            if error_message:
                messagebox.showerror("Error", error_message)
            else:
                # Save changes to the database
                db = Database()
                db.save_additional_info(user_info[0], *updated_info)  # Pass username and updated information

                # Inform the user that changes have been saved
                messagebox.showinfo("Success", "Changes have been saved successfully.")

                # Go back to the main settings page
                self.create_widgets()

        #Button
        save_button = tk.Button(peach_frame, text="Next", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=save_changes, bg='#53c200')
        back_button = tk.Button(peach_frame, text="Back", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=self.create_widgets, bg='#3047ff')
        save_button.grid(row=i+2, column=1, padx=5, pady=5,sticky="w" )
        back_button.grid(row=i+2, column=0, padx=5, pady=5)



    def create_change_password_section(self, parent):
        # Load the image for the button
        change_password_img = Image.open("images/change_password.jpg")
        change_password_img = change_password_img.resize((220, 200))  # Resize the image if needed
        change_password_photo = ImageTk.PhotoImage(change_password_img)

        # Create a button with the image
        change_password_button = tk.Button(parent, image=change_password_photo, command=self.show_change_password)
        change_password_button.image = change_password_photo
        change_password_button.pack(pady=0)

    def show_change_password(self):
        # Create a new window to display the change password section
        change_password_window = tk.Toplevel(self.settings_window)
        change_password_window.title("Change Password")

        # Center the window
        window_width = 1166
        window_height = 718
        screen_width = change_password_window.winfo_screenwidth()
        screen_height = change_password_window.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2
        change_password_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Load background image
        bg_image = Image.open('images/background2.jpg')
        bg_photo = ImageTk.PhotoImage(bg_image)

        # Create a label to display the background image
        bg_label = tk.Label(change_password_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        change_password_frame = tk.Frame(change_password_window, bg='#FFF8F4', width=950, height=600)
        change_password_frame.place(x=100, y=50)

        # Create a peach-colored frame for the background
        peach_frame = tk.Frame(change_password_window, bg='#FFF8F4', width=1000, height=600)
        peach_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Display change password section
        tk.Label(peach_frame, bg='#FFF8F4',text="Change Password", font=("Helvetica", 16, "bold")).grid(row=0, column=0, pady=10, sticky="nsew")

        # Function to verify the entered password
        def verify_password():
            entered_password = current_password_entry.get()
            if entered_password == LoginPage.password:
                # Passwords match, enable new password fields
                new_password_entry.config(state=tk.NORMAL)
                confirm_new_password_entry.config(state=tk.NORMAL)
                current_password_entry.config(state=tk.DISABLED)
                verify_password_button.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Error", "Incorrect current password")

        # Function to enable/disable change password button
        def validate_new_passwords(*args):
            new_password = new_password_entry.get()
            confirm_new_password = confirm_new_password_entry.get()
            if new_password == confirm_new_password and new_password:
                verify_password_button.config(state=tk.NORMAL)
            else:
                verify_password_button.config(state=tk.DISABLED)

        # Function to change the password
        def change_password():
            new_password = new_password_entry.get()
            confirm_new_password = confirm_new_password_entry.get()
            if new_password == confirm_new_password:
                db = Database()
                try:
                    username_value = LoginPage.username
                    user = db.get_user(LoginPage.username)
                except AttributeError:
                    user = db.get_user(SignupWindow.username)
                username = user[0]
                password = new_password  # Getting the new password directly
                # updating to the database
                conn = sqlite3.connect("users.db")
                if username:
                    db = Database()
                    user = db.get_user(username)
                    if user:
                        new_salt = secrets.token_hex(16)  # Generate a new salt
                        new_password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), new_salt.encode(),100000).hex()
                        input_password_hash = user[1]
                        cursor = conn.cursor()
                        sql = "UPDATE users SET password_hash = ?, salt = ? WHERE username = ?"
                        cursor.execute(sql, (new_password_hash, new_salt, username))  # Passing `sql` as second argument
                        conn.commit()

                        print(f"{cursor.rowcount} record updated")
                        print("New: ", new_password_hash)
                        
                        print("New: ", new_salt)
                        print("Input: ", input_password_hash)
                        if new_password_hash != input_password_hash:
                            messagebox.showinfo("Reminder", f"Your password has been changed to: '{password}'")  # Changed self.password to password
                            LoginPage.password = new_password  # Update LoginPage.password
                            change_password_window.destroy()  # Destroy the window upon successful password change
                        else:
                            messagebox.showerror("Error", "Error")
                else:
                    messagebox.showerror("Error", "We cannot find the user")
            else:
                messagebox.showerror("Error", "Passwords do not match")

        tk.Label(peach_frame, bg='#FFF8F4',text="Enter Current Password:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        current_password_entry = tk.Entry(peach_frame, show="*",width=25)
        current_password_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    
        veri_button = tk.Button(peach_frame, text="VERIFY", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=verify_password, bg='#3047ff')
        veri_button.grid(row=2, column=1, padx=10, pady=5, sticky="w")


        tk.Label(peach_frame,bg='#FFF8F4', text="Enter New Password:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        new_password_entry = tk.Entry(peach_frame, show="*", state=tk.DISABLED,width=25)
        new_password_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        new_password_entry.bind("<KeyRelease>", validate_new_passwords)

        tk.Label(peach_frame, bg='#FFF8F4',text="Confirm New Password:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        confirm_new_password_entry = tk.Entry(peach_frame, show="*", state=tk.DISABLED, width=25)
        confirm_new_password_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        confirm_new_password_entry.bind("<KeyRelease>", validate_new_passwords)

        verify_password_button = tk.Button(peach_frame, text="SAVE", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=change_password, bg='#53c200',state=tk.DISABLED)

        verify_password_button.grid(row=5, column=1, padx=10, pady=5, sticky="w")

        back_button = tk.Button(peach_frame, text="Back", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=change_password_window.destroy, bg='#1e81b0')
        back_button.grid(row=5, column=0, padx=10, pady=5, sticky="w")

    def create_feedback_support_section(self, parent):
        # Load the image for the feedback button
        feedback_img = Image.open("images/feedback.png")
        feedback_img = feedback_img.resize((220, 200))  # Adjust size as needed
        feedback_photo = ImageTk.PhotoImage(feedback_img)

        # Create a button with the image
        feedback_button = tk.Button(parent, image=feedback_photo, command=self.show_feedback)
        feedback_button.image = feedback_photo
        feedback_button.pack(pady=10)

    def show_feedback(self):
        # Create a new window for feedback
        feedback_window = tk.Toplevel(self.parent)
        feedback_window.title("Feedback")

        # Center the window
        window_width = 1166
        window_height = 718
        screen_width = feedback_window.winfo_screenwidth()
        screen_height = feedback_window.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2
        feedback_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Load background image
        bg_image = Image.open('images/background2.jpg')
        bg_photo = ImageTk.PhotoImage(bg_image)

        # Create a label to display the background image
        bg_label = tk.Label(feedback_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        additional_info_frame = tk.Frame(feedback_window, bg='#FFF8F4', width=950, height=630)
        additional_info_frame.place(x=100, y=50)
        
        # Create a peach-colored frame for the background
        feedback_frame = tk.Frame(feedback_window, bg='#FFF8F4', width=1000, height=600)
        feedback_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Feedback Form
        tk.Label(feedback_frame, text="Feedback & Support Form", font=("Helvetica", 16), bg='#FFF8F4').pack(pady=0)
        tk.Label(feedback_frame, text="Name:", bg='#FFF8F4').pack()
        name_entry = tk.Entry(feedback_frame)
        name_entry.pack()
        tk.Label(feedback_frame, text="Email:", bg='#FFF8F4').pack()
        email_entry = tk.Entry(feedback_frame)
        email_entry.pack()
        tk.Label(feedback_frame, text="Feedback:", bg='#FFF8F4').pack()
        feedback_text = tk.Text(feedback_frame, width=50, height=10)
        feedback_text.pack()

        # Rating System
        rating_var = tk.IntVar()
        tk.Label(feedback_frame, text="Rating:", bg='#FFF8F4').pack()

        # Create a frame to hold the Radiobuttons horizontally
        rating_frame = tk.Frame(feedback_frame, bg='#FFF8F4')
        rating_frame.pack()

        # Create Radiobuttons for each rating option
        for i in range(1, 6):
            tk.Radiobutton(rating_frame, text=str(i), variable=rating_var, value=i, bg='#FFF8F4').pack(side=tk.LEFT, padx=5)

        def open_faqs_page():
            # URL of the FAQs page
            faqs_url = "https://www.england.nhs.uk/supporting-our-nhs-people/support-now/wellbeing-apps/faqs/"
            # Open the URL in the default web browser
            webbrowser.open(faqs_url)
        def open_email_client():
            # Construct the email address
            email_address = "mailto:support@healthyu.com"
            # Open the default email client
            webbrowser.open(email_address)
        def initiate_phone_call():
            # Construct the phone number with tel: scheme
            phone_number = "tel:+442222222222"
            # Open the default web browser to initiate the phone call
            webbrowser.open(phone_number)
       # Support Options
        tk.Label(feedback_frame, text="Support Options:", bg='#FFF8F4').pack()
        # Bind the label to the callback function to open the FAQs page when clicked
        label_faqs = tk.Label(feedback_frame, text="FAQs", fg="blue", cursor="hand2", bg='#FFF8F4')
        label_faqs.pack()
        label_faqs.bind("<Button-1>", lambda e: open_faqs_page())
        # Implement a callback to open the FAQs page when clicked
        # Example: label.bind("<Button-1>", callback_function)
        label_email = tk.Label(feedback_frame, text="Customer Support Email: support@healthyu.com", fg="blue", cursor="hand2", bg='#FFF8F4')
        label_email.pack()
        label_email.bind("<Button-1>", lambda e: open_email_client())
        label_phone = tk.Label(feedback_frame, text="Contact Number: +44 22222 22222", fg="blue", cursor="hand2", bg='#FFF8F4')
        label_phone.pack()
        label_phone.bind("<Button-1>", lambda e: initiate_phone_call())
        tk.Label(feedback_frame, text="Office Working Hours: Mon-Fri, 9am-5pm", bg='#FFF8F4').pack()
        tk.Label(feedback_frame, text="Office Address: 123 Main Street, City, Country", bg='#FFF8F4').pack()

        def show_thank_you_message():
            # Display a messagebox with the thank you message
            messagebox.showinfo("Thank you for your feedback!")
            # Destroy the current window
            feedback_window.destroy()
        # Submit button
        submit_button = tk.Button(feedback_frame, text="SUBMIT", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=show_thank_you_message, bg='#53c200')
        submit_button.pack(pady=10)
        back_buttom = tk.Button(feedback_frame, text="BACK", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=feedback_window.destroy, bg='#3047ff')
        back_buttom.pack(pady = 10)
        def open_instagram():
            # Open Instagram website
            webbrowser.open("https://www.instagram.com")

        # Social Media Links
        label_instagram = tk.Label(feedback_frame, bg='#FFF8F4')
        label_instagram.pack()

        # Configuring the label with different text parts
        label_instagram_text = "Connect with us on"
        label_instagram_instagram = "Instagram"
        label_instagram_rest = "!!"

        label_instagram_text_widget = tk.Label(label_instagram, text=label_instagram_text, bg='#FFF8F4')
        label_instagram_text_widget.pack(side="left")
        label_instagram_instagram_widget = tk.Label(label_instagram, text=label_instagram_instagram, fg="blue", cursor="hand2", bg='#FFF8F4')
        label_instagram_instagram_widget.pack(side="left")
        label_instagram_rest_widget = tk.Label(label_instagram, text=label_instagram_rest, bg='#FFF8F4')
        label_instagram_rest_widget.pack(side="left")

        # Bind the label to open the Instagram website when clicked
        label_instagram_instagram_widget.bind("<Button-1>", lambda e: open_instagram())

    def submit_feedback(self, name, email, feedback):
        # Save feedback to a file or database
        print("Feedback submitted:")
        print("Name:", name)
        print("Email:", email)
        print("Feedback:", feedback)

    def back(self):
        # Placeholder for back functionality
        self.settings_window.destroy()

    def log_out(self):
        # Placeholder for log out functionality
        messagebox.showinfo("Logged Out", "You have been logged out.")
        sys.exit()

class RecipeSearchWindow:
    APP_ID = "933067e1"
    API_KEY = "2e9a0e40772cceedf9440979570c7119"
    URL = f'https://api.edamam.com/search?app_id={APP_ID}&app_key={API_KEY}'

    def __init__(self, parent):
        self.parent = parent
        self.recipe_window = tk.Toplevel(parent)
        self.recipe_window.title("Recipe Finder")
        self.recipe_window.config(bg="#343a40")

        # Calculate the screen width and height
        screen_width = self.recipe_window.winfo_screenwidth()
        screen_height = self.recipe_window.winfo_screenheight()

        # Set the window size and position it in the center of the screen
        window_width = 1166
        window_height = 718
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.recipe_window.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # Load and display background image
        bg_image = Image.open('images/background2.jpg')
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self.recipe_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create additional info frame
        self.additional_info_frame = tk.Frame(self.recipe_window, bg='#FFF8F4', width=950, height=700)
        self.additional_info_frame.place(x=100, y=10)

        self.create_search_entry()

        self.message_box_open = False  # Flag to track if message box is open

    def create_search_entry(self):
        # Add text above the search entry
        instructions_label = tk.Label(self.recipe_window, text="Enter the recipe you want the instructions on:", font=("Arial", 12),bg="#FFF8F4")
        instructions_label.pack(pady=(50, 10))

        self.search_entry = tk.Entry(self.recipe_window, width=70, font=("Arial", 14), foreground="black", background="white")
        self.search_entry.pack(pady=(0, 5))

        # Create a frame to hold the buttons
        button_frame = tk.Frame(self.recipe_window, bg="#FFF8F4")
        button_frame.pack()

        #Button
        search_button = tk.Button(button_frame, text="SEARCH", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=self.query_recipes, bg='#53c200')
        back_button = tk.Button(button_frame, text="BACK", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=self.recipe_window.destroy, bg='#3047ff')
        search_button.pack(side="left", padx=(0, 100))
        back_button.pack(side="left", padx=(10, 0))

    def query_recipes(self):
        def make_request(url):
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
                data = response.json()
                return data
            except requests.exceptions.RequestException as e:
                print("Request Error:", e)
                return None

        key_word = self.search_entry.get()
        response = make_request(self.get_url_q(key_word))

        if response:
            hits = response.get('hits', [])
            if hits:
                self.display_recipes(hits)
                # Store hits for later use
                self.hits = hits
            else:
                # Destroy previous listbox if it exists
                for widget in self.recipe_window.winfo_children():
                    if isinstance(widget, tk.Listbox):
                        widget.destroy()
                if not self.message_box_open:  # Check if message box is not open
                    self.message_box_open = True
                    messagebox.showinfo("No Results", f"No results found for '{key_word}'.")
        else:
            if not self.message_box_open:  # Check if message box is not open
                self.message_box_open = True
                messagebox.showerror("Error", "Failed to fetch data from the server. Please try again later.")

    def get_url_q(self, key_word, _from=0, to=20):
        url = RecipeSearchWindow.URL + f'&q={key_word}&to={to}&from={_from}'
        return url

    def display_recipes(self, recipes):
        # Destroy previous listbox if it exists
        for widget in self.additional_info_frame.winfo_children():
            if isinstance(widget, (tk.Listbox, tk.Label)):  # Adjusted to include Label widget
                widget.destroy()

        # Add text above the display box
        instructions_label = tk.Label(self.additional_info_frame, text=" Please Double click on the Name of the recipe to access detailed instructions about the recipe", font=("Arial", 12), wraplength=800)
        instructions_label.pack(pady=(140, 20))

        recipe_listbox = tk.Listbox(self.additional_info_frame, width=80, height=20, font=("Arial", 16))  # Increase font size to 16
        recipe_listbox.pack(pady=(0, 10), padx=(40, 40))  # Adjusted padding for the listbox
        for i, recipe in enumerate(recipes, 1):
            recipe_listbox.insert(tk.END, f"{i}) {recipe['recipe']['label']}")
        recipe_listbox.bind("<Double-Button-1>", self.display_selected_recipe)

    def display_selected_recipe(self, event):
        if not self.message_box_open:  # Check if message box is not open
            widget = event.widget
            index = int(widget.curselection()[0])
            selected_recipe = widget.get(index)
            recipe_index = int(selected_recipe.split(')')[0]) - 1
            recipe = self.hits[recipe_index]['recipe']
            recipe_info = f"Recipe: {recipe['label']}\nIngredients:\n"
            for ingredient in recipe['ingredients']:
                recipe_info += f"- {ingredient['text']}\n"

            # Extract nutritional information and cooking time
            nutritional_info = f"Nutritional Information:\n"
            nutritional_info += f"- Calories: {recipe['calories']:.2f} kcal\n"
            nutritional_info += f"- Total Fat: {recipe['totalNutrients']['FAT']['quantity']:.2f} {recipe['totalNutrients']['FAT']['unit']}\n"
            nutritional_info += f"- Carbohydrates: {recipe['totalNutrients']['CHOCDF']['quantity']:.2f} {recipe['totalNutrients']['CHOCDF']['unit']}\n"
            nutritional_info += f"- Protein: {recipe['totalNutrients']['PROCNT']['quantity']:.2f} {recipe['totalNutrients']['PROCNT']['unit']}\n"
            
            if 'totalTime' in recipe:
                if recipe['totalTime'] == 0.0:
                    cooking_time = "Cooking Time: Not available\n"
                else:
                    cooking_time = f"Cooking Time: {recipe['totalTime']} minutes\n"
            else:
                cooking_time = "Cooking Time: Not available\n"
            recipe_info += '\n' + nutritional_info + '\n' + cooking_time

            # Load image
            image_url = recipe['image']
            response = requests.get(image_url)
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((400, 400))
            img = ImageTk.PhotoImage(img)

            # Create a new dialog window to display recipe details
            recipe_dialog = tk.Toplevel(self.recipe_window)
            recipe_dialog.title("Recipe Details")

            # Set the size of the dialog window and center it on the screen
            dialog_width = 1166
            dialog_height = 718
            screen_width = recipe_dialog.winfo_screenwidth()
            screen_height = recipe_dialog.winfo_screenheight()
            x = (screen_width - dialog_width) // 2
            y = (screen_height - dialog_height) // 2
            recipe_dialog.geometry(f'{dialog_width}x{dialog_height}+{x}+{y}')

            # Load and display background image
            bg_image = Image.open('images/background2.jpg')
            bg_photo = ImageTk.PhotoImage(bg_image)
            bg_label = tk.Label(recipe_dialog, image=bg_photo)
            bg_label.image = bg_photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

            # Create additional info frame
            additional_info_frame = tk.Frame(recipe_dialog, bg='#FFF8F4', width=950, height=700)
            additional_info_frame.place(x=60, y=80)

            # Create a Frame to hold image and text within the additional info frame
            frame = tk.Frame(additional_info_frame, bg="#FFF8F4")
            frame.pack(padx=20, pady=20)

            # Display image
            img_label = tk.Label(frame, image=img, bg="#FFF8F4")
            img_label.image = img
            img_label.grid(row=0, column=0, padx=10, pady=10)

            # Display recipe information
            recipe_text = tk.Text(frame, wrap="word", font=("Arial", 14), bg="#FFF8F4", bd=0, width=50, height=20)
            recipe_text.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

            recipe_text.insert(tk.END, recipe_info)
            recipe_text.configure(state="disabled")

            # Add hyperlink
            url = recipe['url']
            hyperlink_label = tk.Label(frame, text="Click here to view the detailed instructions of the recipe", fg="blue", cursor="hand2", bg="#FFF8F4")
            hyperlink_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
            hyperlink_label.bind("<Button-1>", lambda event, url=url: self.open_url(event, url))

            # Add back button to close the dialog
            back_button = tk.Button(frame, text="BACK", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=lambda: self.close_recipe_dialog(recipe_dialog), bg='#53c200')
            back_button.grid(row=2, column=0, columnspan=2, pady=(10, 0))

            # Resize columns and rows of the frame
            frame.grid_columnconfigure(1, weight=1)
            frame.grid_rowconfigure(0, weight=1)

            self.message_box_open = True  # Set the flag to indicate that a message box is open

            recipe_dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_recipe_dialog(recipe_dialog))

    def close_recipe_dialog(self, recipe_dialog):
        recipe_dialog.destroy()
        self.message_box_open = False  # Reset the flag when the message box is closed

    def open_url(self, event, url):
        import webbrowser
        webbrowser.open_new(url)
        
class MealPlanner(tk.Toplevel):
    API_KEY="f2f13e73715140f2b4f925855a51da2a"
    #API_KEY = "6dee9616d2e64fa09dee8faeb537acb5"
    URL = f'https://api.spoonacular.com/mealplanner/generate'

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Meal Planner")
        self.resizable(0,0)
        self.config(bg="#FFF8F4")  # Peachy color

        # Calculate the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Set the window size and position it in the center of the screen
        window_width = 1166
        window_height = 718
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')

        bg_frame = Image.open('images/background2.jpg')
        bg_photo = ImageTk.PhotoImage(bg_frame)
        bg_label = tk.Label(self, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.pack(fill= 'both',expand='yes')

        # Create a canvas
        self.canvas = tk.Canvas(self, bg='#FFF8F4', width=950, height=600)
        self.canvas.place(x=100, y=50)

        # Add a scrollbar to the canvas
        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)


        self.additional_info_frame = tk.Frame(self.canvas, bg='#FFF8F4')


        self.canvas.create_window((0, 0), window=self.additional_info_frame, anchor=tk.CENTER)

        self.additional_info_frame.bind("<Configure>", self.on_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)  # Bind canvas configuration event

        # Bind MouseWheel event to enable scrolling
        self.bind_all("<MouseWheel>", self.on_mousewheel)

        self.allergies_options = ["None","Celery-free", "Crustacean-free", "Dairy-free", "Egg-free", "Fish-free", "Gluten-free", "Lupine-free", "Mustard-free", "Peanut-free", "Sesame-free", "Shellfish-free", "Soy-free", "Tree-Nut-free", "Wheat-free", "FODMAP-Free"]
        self.diets_options = ["None","Alcohol-free", "Balanced", "DASH", "High-Fiber", "High-Protein", "Keto", "Kidney friendly", "Kosher", "Low-Carb", "Low-Fat", "Low potassium", "Low-Sodium", "Mediterranean", "No oil added", "No-sugar", "Paleo", "Pescatarian", "Pork-free", "Red meat-free", "Sugar-conscious", "Vegan", "Vegetarian", "Mollusk-Free", "Sulfite-Free"]

        self.create_meal_selection()

    def on_canvas_configure(self, event):
        # Update scroll region to cover the entire canvas
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_configure(self, event):
        # Update scroll region to cover the entire frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def create_meal_selection(self):
    # Add text above the meal selection
        instructions_label = tk.Label(self.additional_info_frame, text="Please select the number of days", font=("Arial", 15),bg='#FFF8F4')
        instructions_label.grid(row=0, column=0, pady=10, columnspan=2)  # Use grid for centering

        # Duration selection widget
        duration_options = ['1 day', '2 day', '3 day', '4 day', '5 day', '6 day', '7 day']
        self.duration_var = tk.StringVar(self)
        self.duration_var.set(duration_options[0])  # default value

        duration_label = tk.Label(self.additional_info_frame, text="Duration of plan :",font=("Arial", 15),bg='#FFF8F4')
        duration_label.grid(row=1, column=0, pady=5)
        
        duration_dropdown = tk.OptionMenu(self.additional_info_frame, self.duration_var, *duration_options)
        duration_dropdown.grid(row=1, column=1, pady=5)


        next_button = tk.Button(self.additional_info_frame, text="Next", font=("yu gothic ui", 13, "bold"), width=10, bd=0,
                           cursor='hand2', fg='white', command=self.go_to_step_2, bg='#53c200')
        back_button = tk.Button(self.additional_info_frame, text="Back", font=("yu gothic ui", 13, "bold"), width=10, bd=0,
                           cursor='hand2', fg='white', command=self.destroy, bg='#3047ff')

        next_button.grid(row=2, column=1, pady=10)
        back_button.grid(row= 2, column=0, pady= 10)

        # Centering the additional_info_frame content
        self.additional_info_frame.update_idletasks()  # Update to get proper size
        frame_width = self.additional_info_frame.winfo_width()
        frame_height = self.additional_info_frame.winfo_height()
        frame_x = (self.canvas.winfo_width() - frame_width) / 2
        frame_y = (self.canvas.winfo_height() - frame_height) / 2
        self.canvas.create_window(frame_x, frame_y, window=self.additional_info_frame)

    def go_to_step_2(self):
        # Destroy previous widgets
        for widget in self.additional_info_frame.winfo_children():
            widget.destroy()

        # Add text for Step 2
        instructions_label = tk.Label(self.additional_info_frame, text="Please select your allergies and dietary preferences:", font=("Arial", 15),bg='#FFF8F4')
        instructions_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Allergies selection
        allergies_label = tk.Label(self.additional_info_frame, text="Allergies to keep in mind:",font=("Arial", 15),bg='#FFF8F4')
        allergies_label.grid(row=1, column=0, padx=10, pady=5)
        self.allergies_vars = []
        # Display allergies in multiple columns
        num_columns = 2
        for i, option in enumerate(self.allergies_options):
            var = tk.IntVar(value=1 if i == 0 else 0)  # Set the first checkbox to 1 (checked), others to 0 (unchecked)
            row_index = i % (len(self.allergies_options) // num_columns)
            col_index = i // (len(self.allergies_options) // num_columns)
            tk.Checkbutton(self.additional_info_frame, text=option, variable=var).grid(row=row_index + 1, column=col_index + 1, sticky=tk.W, padx=10, pady=5)
            self.allergies_vars.append(var)
    
         # Next button for allergies
        
        next_allergies_button = tk.Button(self.additional_info_frame, text="Next", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=self.go_to_step_2_1, bg='#53c200')
        back_button = tk.Button(self.additional_info_frame, text="Back", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=self.destroy, bg='#3047ff')

        next_allergies_button.grid(row=len(self.allergies_options) // num_columns + 2, column=2, pady=10)
        back_button.grid(row=len(self.allergies_options) // num_columns + 2, column=1, pady=10)

    def go_to_step_2_1(self):
        self.selected_allergies = [self.allergies_options[i] for i, var in enumerate(self.allergies_vars) if var.get() == 1 and self.allergies_options[i] != "None"]
        # Destroy previous widgets
        # Destroy previous widgets
        for widget in self.additional_info_frame.winfo_children():
            widget.destroy()

        # Diets selection
        diets_label = tk.Label(self.additional_info_frame, text="Diets to follow:",font=("Arial", 15),bg='#FFF8F4')
        diets_label.grid(row=0, column=0, padx=10, pady=5)

        num_columns = 2
        num_rows = len(self.diets_options) // num_columns + (len(self.diets_options) % num_columns > 0)  # Round up division

        self.diets_vars = []
        for i, option in enumerate(self.diets_options):
            var = tk.IntVar(value=1 if i == 0 else 0)
            row = i % num_rows + 1
            column = i // num_rows
            tk.Checkbutton(self.additional_info_frame, text=option, variable=var).grid(row=row, column=column, sticky=tk.W, padx=10, pady=5)
            self.diets_vars.append(var)

        # Next button for diets
        next_diets_button = tk.Button(self.additional_info_frame, text="Next", font=("yu gothic ui", 13, "bold"), width=10, bd=0,
                           cursor='hand2', fg='white', command=self.go_to_step_2_2, bg='#53c200')
        back_button = tk.Button(self.additional_info_frame, text="Back", font=("yu gothic ui", 13, "bold"), width=10, bd=0,
                           cursor='hand2', fg='white', command=self.go_to_step_2, bg='#3047ff')

        next_diets_button.grid(row=num_rows + 1, column=1, pady=10)
        back_button.grid(row=num_rows + 1, column=0,pady=10)


    def go_to_step_2_2(self):
        self.selected_diets = [self.diets_options[i] for i, var in enumerate(self.diets_vars) if var.get() == 1 and self.diets_options[i] != "None"]
        # Destroy previous widgets
        for widget in self.additional_info_frame.winfo_children():
            widget.destroy()

        # Calorie goals
        calorie_label = tk.Label(self.additional_info_frame, text="Calorie goals (min/max kcal):",font=("Arial", 15),bg='#FFF8F4')
        calorie_label.grid(row=0, column=0, padx=10, pady=5)
        self.min_cal_entry = tk.Entry(self.additional_info_frame)
        self.min_cal_entry.grid(row=0, column=1, padx=5, pady=5)
        self.max_cal_entry = tk.Entry(self.additional_info_frame)
        self.max_cal_entry.grid(row=0, column=2, padx=5, pady=5)

        # Next button for calorie goals
        next_calorie_button = tk.Button(self.additional_info_frame, text="Next", command=self.go_to_step_3,font=("Arial", 15))
        back_button = tk.Button(self.additional_info_frame, text="Back", command=  self.go_to_step_2_1,font=("Arial", 15))

        next_calorie_button = tk.Button(self.additional_info_frame, text="Next", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=self.go_to_step_3, bg='#53c200')
        back_button = tk.Button(self.additional_info_frame, text="Back", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=self.go_to_step_2_1, bg='#3047ff')

        next_calorie_button.grid(row=1, column=1, columnspan=2, pady=10)
        back_button.grid(row=1, column=0, columnspan=2,pady=10)

    def go_to_step_3(self):
        # Set default calorie values if not provided by the user
        self.min_cal = self.min_cal_entry.get()
        self.max_cal = self.max_cal_entry.get()
        if not self.min_cal or not self.max_cal:
            self.min_cal = "2250"
            self.max_cal = "2250"
        # Destroy previous widgets
        for widget in self.additional_info_frame.winfo_children():
            widget.destroy()

        # Make API request with selected preferences
        self.make_meal_plan_request()
        
    def make_meal_plan_request(self):
        # Extract the duration of the plan
        duration = int(self.duration_var.get().split()[0])
        for day in range(1, duration + 1):
            # Construct the request payload for each day
            payload = {
                "timeFrame": "day",  # Request meals for one day at a time
                "targetCalories": int((int(self.min_cal) + int(self.max_cal)) / 2),  # Use average of min and max calories
                "diet": ",".join(self.selected_diets),  # Use selected diets
                "exclude": ",".join(self.selected_allergies),  # Use selected allergies
                "apiKey": self.API_KEY
            }

            # Make API request for the current day
            response = requests.get(self.URL, params=payload)

            # Print the response content for debugging
            print(f"Response Content for Day {day}:", response.content)

            # Check if request was successful
            if response.status_code == 200:
                total_nutritional_value_of_each_day = response.json().get('nutrients', [])
                # Parse response and extract meal options for the current day
                meal_options = response.json().get('meals', [])
                # Preload images asynchronously
                self.preload_images(day, meal_options)
                # Display meal options for the current day
                self.display_meal_options(day, meal_options, total_nutritional_value_of_each_day)
            else:
                # Handle error
                print(f"Error for Day {day}:", response.text)

    def preload_images(self, day, meal_options):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for meal in meal_options:
                if 'imageType' in meal:
                    image_url = f"https://spoonacular.com/recipeImages/{meal['id']}-556x370.{meal['imageType']}"
                    future = executor.submit(self.download_image, image_url)
                    futures.append(future)
            for future in concurrent.futures.as_completed(futures):
                future.result()  # Wait for each image to finish downloading

    def download_image(self, image_url):
        
        response = requests.get(image_url)
        if response.status_code == 200:
            # Save the image data
            return response.content
        return None
    
    def display_meal_options(self, day, meal_options, total_nutritional_value_of_each_day):
        # Display day number
        day_label = tk.Label(self.additional_info_frame, text=f"Day {day}:", font=("Arial", 15, "bold"))
        day_label.grid(row=(day - 1) * 9, column=0, columnspan=3, pady=(10, 5))

        # Labels for breakfast, lunch, and dinner
        meal_labels = ["Breakfast", "Lunch", "Dinner"]

        for i, meal_label in enumerate(meal_labels):
            label = tk.Label(self.additional_info_frame, text=meal_label, font=("Arial", 12, "bold"))
            label.grid(row=(day - 1) * 9 + i * 2 + 1, column=1, pady=(10, 5), sticky="nsew")

        # Display meal options for the current day with one meal after each breakfast, lunch, and dinner
        for i, meal in enumerate(meal_options):
            meal_frame = tk.Frame(self.additional_info_frame, bg="white", bd=1, relief=tk.RIDGE)
            # Determine the meal type and adjust the row accordingly
            meal_type_row = (day - 1) * 9 + i * 2 + 2
            meal_frame.grid(row=meal_type_row, column=1, padx=10, pady=10, sticky="nsew")

            # Meal name label with double-click functionality to open source URL
            def open_source_url(event, url):
                webbrowser.open_new(url)

            meal_name_label = tk.Label(meal_frame, text=f"Meal Name: {meal['title']}", font=("Arial", 15, "bold"), bg="white", cursor="hand2")
            meal_name_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
            meal_name_label.bind("<Double-1>", lambda event, url=meal['sourceUrl']: open_source_url(event, url))

            # Image display
            if 'imageType' in meal:
                image_url = f"https://spoonacular.com/recipeImages/{meal['id']}-556x370.{meal['imageType']}"
                response = requests.get(image_url)
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    image = image.resize((100, 100), Image.BILINEAR)
                    photo = ImageTk.PhotoImage(image)
                    image_label = tk.Label(meal_frame, image=photo, bg="white")
                    image_label.image = photo
                    image_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")

            # Other meal information
            ready_label = tk.Label(meal_frame, text=f"Ready in minutes: {meal['readyInMinutes']}", bg="white")
            ready_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")

            servings_label = tk.Label(meal_frame, text=f"Servings: {meal['servings']}", bg="white")
            servings_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")

            # Double-click functionality to open source URL
            meal_name_label.bind("<Double-1>", lambda event, url=meal['sourceUrl']: open_source_url(event, url))

        # Display total 
        total_nutrients_label = tk.Label(self.additional_info_frame, text=f"Total Nutritional Values for Day {day}: Calories: {total_nutritional_value_of_each_day.get('calories', 0)} | Protein: {total_nutritional_value_of_each_day.get('protein', 0)}g | Fat: {total_nutritional_value_of_each_day.get('fat', 0)}g | Carbohydrates: {total_nutritional_value_of_each_day.get('carbohydrates', 0)}g", font=("Arial", 10, "bold"))
        total_nutrients_label.grid(row=(day - 1) * 9 + 7, column=1, pady=(10, 5), sticky="nsew")

        back_button = tk.Button(self.additional_info_frame, text="BACK TO HOME", font=("yu gothic ui", 13, "bold"), width=5, bd=0,
                           cursor='hand2', fg='white', command=self.destroy, bg='#53c200')
        back_button.grid(row=day *9 +7,column=1,pady=(10, 5), sticky="nsew")

class AboutUsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.about_us_window = tk.Toplevel(self.parent)
        self.about_us_window.title("About Us/Info")
        self.about_us_window.geometry('1166x718')
        self.center_window(self.about_us_window)
        self.set_background("images\\background2.jpg")
        self.create_about_us_content()
        self.add_image_box("images\\group_photo.png", 550, 400)


    def center_window(self, window):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x_coordinate = (screen_width - 1166) // 2
        y_coordinate = (screen_height - 718) // 2
        window.geometry(f'1166x718+{x_coordinate}+{y_coordinate}')

    def set_background(self, image_path):
        bg_image = Image.open(image_path)
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self.about_us_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def create_about_us_content(self):
        additional_info_frame = tk.Frame(self.about_us_window, bg='#FFF8F4', width=950, height=600)
        additional_info_frame.place(x=100, y=80)

        about_us_text = """Welcome to Our Application!

        We are a dedicated team of developers committed to crafting innovative solutions to address the diverse needs of our users. Our mission is to provide user-friendly software that enhances the overall quality of life and promotes holistic well-being.

        At the heart of our product lies a commitment to empowering users with comprehensive tools to track and manage their daily caloric intake and physical activity levels. Moreover, our platform grants users free access to an extensive recipe database, facilitating informed and enjoyable meal planning experiences.

        In addition to serving as a comprehensive dietary management tool,our application provides users with the flexibility to create and customize daily diet plans tailored to their individual preferences and nutritional requirements. Furthermore, users can seamlessly integrate their weight loss objectives and other health-related goals into an interactive calendar, fostering accountability and motivation.

        We are committed to fostering open communication and
        collaboration with our users. 

        Your feedback and suggestions are invaluable to us as 
        we continuously strive to enhance and refine our 
        product to better meet your needs and expectations.

        For inquiries, assistance, or feedback, 
        please feel free to reach out to us via email:

        Email:
        - xy22985@essex.ac.uk
        - nt22289@essex.ac.uk
        - mf21580@essex.ac.uk

        Thank you for choosing our application.
        """
    
        about_us_label = tk.Label(additional_info_frame, text=about_us_text, font=("Helvetica", 12), justify="left", bg='#FFF8F4', wraplength=900)
        about_us_label.pack(padx=20)

        back_button = tk.Button(additional_info_frame, text="BACK", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=self.about_us_window.destroy, bg='#3047ff')
        
        back_button.pack(pady=10)

    def add_image_box(self, image_path, x, y):
        img = Image.open(image_path)
        img = img.resize((450, 200))
        img_photo = ImageTk.PhotoImage(img)
        img_label = tk.Label(self.about_us_window, image=img_photo,bg='#FFF8F4')
        img_label.image = img_photo
        img_label.place(x=x, y=y)

import datetime as dt
class RDAWindow:
    def __init__(self, parent):
        self.parent = parent
        self.rda_window = tk.Toplevel(parent)
        self.rda_window.title("Personalized RDA Calculator")
        self.rda_window.geometry('1166x718')
        self.center_window(self.rda_window)
        self.set_background("images/background2.jpg")
        self.create_rda_content()

    def center_window(self, window):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x_coordinate = (screen_width - 1166) // 2
        y_coordinate = (screen_height - 718) // 2
        window.geometry(f'1166x718+{x_coordinate}+{y_coordinate}')

    def set_background(self, image_path):
        bg_image = Image.open(image_path)
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self.rda_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def create_rda_content(self):
        # Consistent color and font settings
        font_settings = ("Helvetica", 12,"bold")
        bg_color = '#FFF8F4'

        # Main frame for content
        content_frame = tk.Frame(self.rda_window, bg=bg_color,width=950, height=600)
        content_frame.place(x=420, y=160)
        db = Database()
        try:
            user_info = db.get_user(LoginPage.username)
        except AttributeError:
            user_info = db.get_user(SignupWindow.username)

        if user_info:
            # Extract user information from the tuple
            _, _, _, _, age, sex, weight, height, activity, _, _ = user_info

            # Input fields within the content frame
            tk.Label(content_frame, text="Sex (Male/Female):", bg=bg_color, font=font_settings).grid(row=0, column=0, padx=10, pady=10)
            self.sex_entry = tk.Entry(content_frame, font=font_settings)
            self.sex_entry.insert(tk.END, sex)
            self.sex_entry.grid(row=0, column=1, padx=10, pady=10)

            tk.Label(content_frame, text="Age (years):", bg=bg_color, font=font_settings).grid(row=1, column=0, padx=10, pady=10)
            self.age_entry = tk.Entry(content_frame, font=font_settings)
            self.age_entry.insert(tk.END, age)
            self.age_entry.grid(row=1, column=1, padx=10, pady=10)

            tk.Label(content_frame, text="Height (cm):", bg=bg_color, font=font_settings).grid(row=2, column=0, padx=10, pady=10)
            self.height_entry = tk.Entry(content_frame, font=font_settings)
            self.height_entry.insert(tk.END, height)
            self.height_entry.grid(row=2, column=1, padx=10, pady=10)

            tk.Label(content_frame, text="Weight (kg):", bg=bg_color, font=font_settings).grid(row=3, column=0, padx=10, pady=10)
            self.weight_entry = tk.Entry(content_frame, font=font_settings)
            self.weight_entry.insert(tk.END, weight)
            self.weight_entry.grid(row=3, column=1, padx=10, pady=10)

            tk.Label(content_frame, text="Activity Level:", bg=bg_color, font=font_settings).grid(row=4, column=0, padx=10, pady=10)
            self.activity_entry = tk.Entry(content_frame, font=font_settings)
            self.activity_entry.insert(tk.END, activity)
            self.activity_entry.grid(row=4, column=1, padx=10, pady=10)

            # Button to calculate RDA   # CHANGE yang
            calculate_button = tk.Button(content_frame, text="CALCULATE", font=font_settings,bd=0,width=15,fg="white",bg='#53c200',command=self.calculate_rda)
            calculate_button.grid(row=5, column=0, columnspan=2, pady=10)

            back = tk.Button(content_frame, text="BACK",font=font_settings,bd=0,width=15,fg="white",bg='#3047ff', command=self.rda_window.destroy)
            back.grid(row=6, column=0,  columnspan=2, pady=10)

    def calculate_rda(self):
        try:
            self.sex = self.sex_entry.get()
            self.age = int(self.age_entry.get())
            self.height = int(self.height_entry.get())
            self.weight = int(self.weight_entry.get())
            self.activity_level = self.activity_entry.get()

            # Perform RDA calculations
            bmi = self.calculate_bmi()
            bmr = self.calculate_bmr()
            caloric_needs = self.calculate_caloric_needs(bmr)
            macronutrient_intake = self.calculate_macronutrient_intake(caloric_needs)

            # Clear the content frame
            for widget in self.rda_window.winfo_children():
                widget.destroy()
            
            self.set_background("images/background2.jpg")
            # Main frame for content
            content_frame = tk.Frame(self.rda_window, bg='#FFF8F4', width=950, height=600)
            content_frame.place(x=60, y=70)# CHANGES yang

            bg_colour = '#FFF8F4'
            #CHANGES yang
            tk.Label(content_frame, text="\nRESULT:", bg=bg_colour,font=("yu gothic ui", 15, "bold")).grid(row=6, column=0, sticky='w',padx= 5)
            tk.Label(content_frame, text=f"BMI: {round(bmi, 1)}", bg=bg_colour,font=("yu gothic ui", 13)).grid(row=7, column=0, sticky='w',padx= 5)
            tk.Label(content_frame, text=f"BMR: {round(bmr)} kcal/day", bg=bg_colour,font=("yu gothic ui", 13)).grid(row=8, column=0, sticky='w',padx= 5)
            tk.Label(content_frame, text=f"Caloric Needs: {round(caloric_needs)} kcal/day", bg=bg_colour,font=("yu gothic ui", 13)).grid(row=9, column=0, sticky='w',padx= 5)

            # Create frames for the tables
            table_frame1 = tk.Frame(content_frame, bg=bg_colour)
            table_frame1.grid(row=10, column=0,padx=5, pady=30) #CHANGES yang

            table_frame2 = tk.Frame(content_frame, bg=bg_colour)
            table_frame2.grid(row=10, column=1,padx=5, pady=30)

            table_frame3 = tk.Frame(content_frame, bg=bg_colour)
            table_frame3.grid(row=10, column=2, padx=5,pady=30)

            back = tk.Button(content_frame, text="BACK",font=("yu gothic ui", 13,"bold"),bd=0,width=15,fg="white",bg='#3047ff', command=self.rda_window.destroy)
            back.grid(row=11, column=0, columnspan=3,pady=10)

            # Create Treeview widgets for all tables
            tree1 = ttk.Treeview(table_frame1,height=15) # CHANGES yang
            tree1.pack(fill='both', expand=True)

            tree2 = ttk.Treeview(table_frame2,height=15)
            tree2.pack(fill='both', expand=True)

            tree3 = ttk.Treeview(table_frame3,height=15)
            tree3.pack(fill='both', expand=True)

            

            # Define columns for all tables
            for tree in [tree1, tree2, tree3]:
                tree["columns"] = ("Recommended Intake Per Day",)
                tree.column("#0", width=150, anchor='w')
                tree.heading("#0", text="NUTRITION") #CHANGES yang
                tree.column("Recommended Intake Per Day", width=190, anchor='w')
                tree.heading("Recommended Intake Per Day", text="Intake Per Day")

            # Add data to the first table
            tree1.insert("", "end", text="Carbohydrate", values=(f"{round(macronutrient_intake[0])} - {round(macronutrient_intake[1])} grams",))
            tree1.insert("", "end", text="Total Fiber", values=(f"{math.ceil(macronutrient_intake[2])} grams",))
            tree1.insert("", "end", text="Protein", values=(f"{round(macronutrient_intake[3])} grams",))
            tree1.insert("", "end", text="Fat", values=(f"{round(macronutrient_intake[4])} - {round(macronutrient_intake[5])} grams",))
            tree1.insert("", "end", text="Saturated fatty acids", values=(macronutrient_intake[6],))
            tree1.insert("", "end", text="Trans fatty acids", values=(macronutrient_intake[7],))
            tree1.insert("", "end", text="α-Linolenic Acid", values=(f"{macronutrient_intake[8]} grams",))
            tree1.insert("", "end", text="Linoleic Acid", values=(f"{macronutrient_intake[9]} grams",))
            tree1.insert("", "end", text="Dietary Cholesterol", values=(macronutrient_intake[10],))
            tree1.insert("", "end", text="Total Water", values=(f"{macronutrient_intake[11]} liters (about 16 cups)",))

            # Add data to the second table
            if len(macronutrient_intake) > 12:
                vitamins = macronutrient_intake[12]
                for nutrient, (recommended, tolerable_ul) in vitamins.items():
                    tree2.insert("", "end", text=f"{nutrient}", values=(f"{recommended} mcg", f"{tolerable_ul} mcg" if tolerable_ul else "-"))

            # Add data to the third table
            if len(macronutrient_intake) > 13:
                minerals = macronutrient_intake[13]
                for nutrient, (recommended, tolerable_ul) in minerals.items():
                    tree3.insert("", "end", text=f"{nutrient}", values=(f"{recommended} mg", f"{tolerable_ul} mg" if tolerable_ul else "-"))

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for age, height, weight.")


    def calculate_bmi(self):
        return (self.weight / (self.height / 100) ** 2)

    def calculate_bmr(self):
        if self.sex.lower() == 'male':
            return 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * self.age)
        else:
            return 447.593 + (9.247 * self.weight) + (3.098 * self.height) - (4.330 * self.age)

    def calculate_caloric_needs(self, bmr):
        if self.activity_level.lower() == 'sedentary':
            return bmr * 1.2
        elif self.activity_level.lower() == 'lightly active':
            return bmr * 1.375
        elif self.activity_level.lower() == 'moderately active':
            return bmr * 1.55
        elif self.activity_level.lower() == 'very active':
            return bmr * 1.725
        else:
            return bmr * 1.9

    def calculate_macronutrient_intake(self, caloric_needs):
        carbohydrate_min = caloric_needs * 0.45 / 4
        carbohydrate_max = caloric_needs * 0.65 / 4
        total_fiber = (caloric_needs / 1000) * 14
        protein = 0.8 * self.weight
        fat_min = caloric_needs * 0.20 / 9
        fat_max = caloric_needs * 0.35 / 9
        saturated_fat = 'As low as possible while consuming a nutritionally adequate diet.'
        trans_fat = 'As low as possible while consuming a nutritionally adequate diet.'
        alpha_linolenic_acid = 1.6
        linoleic_acid = 17
        dietary_cholesterol = 'As low as possible while consuming a nutritionally adequate diet.'
        if self.sex.lower() == 'female':
            total_water = 2.7
            vitamin_intake = {
                'Vitamin A': (700, 3000),
                'Vitamin C': (75, 2000),
                'Vitamin D': (15, 100),
                'Vitamin B6': (1.3, 100),
                'Vitamin E': (15, 1000),
                'Vitamin K': (90, 'ND'),
                'Thiamin': (1.1, 'ND'),
                'Vitamin B12': (2.4, 'ND'),
                'Riboflavin': (1.1, 'ND'),
                'Folate': (400, 1000),
                'Niacin': (14, 20),
                'Choline': (0.425, 3.5)
            }
            mineral_intake = {
                'Calcium': (1000, 2500),
                'Chloride': (2.3, 3.6),
                'Chromium': (25, 'ND'),
                'Copper': (900, 10000),
                'Fluoride': (3, 10),
                'Iodine': (150, 1100),
                'Iron': (18, 45),
                'Magnesium': (310, 350),
                'Manganese': (1.8, 11),
                'Molybdenum': (45, 2000),
                'Phosphorus': (0.7, 4),
                'Potassium': (2600, 'ND'),
                'Selenium': (55, 400),
                'Sodium': (1500, 2300),
                'Zinc': (8, 40)
            }
        else:
            total_water = 3.7
            vitamin_intake = {
                'Vitamin A': (900, 3000),
                'Vitamin C': (90, 2000),
                'Vitamin D': (15, 100),
                'Vitamin B6': (1.3, 100),
                'Vitamin E': (15, 1000),
                'Vitamin K': (120, 'ND'),
                'Thiamin': (1.2, 'ND'),
                'Vitamin B12': (2.4, 'ND'),
                'Riboflavin': (1.3, 'ND'),
                'Folate': (400, 1000),
                'Niacin': (16, 35),
                'Choline': (0.55, 3.5)
            }
            mineral_intake = {
                'Calcium': (1000, 2500),
                'Chloride': (2.3, 3.6),
                'Chromium': (35, 'ND'),
                'Copper': (900, 10000),
                'Fluoride': (4, 10),
                'Iodine': (150, 1100),
                'Iron': (8, 45),
                'Magnesium': (400, 350),
                'Manganese': (2.3, 11),
                'Molybdenum': (45, 2000),
                'Phosphorus': (0.7, 4),
                'Potassium': (3400, 'ND'),
                'Selenium': (55, 400),
                'Sodium': (1500, 2300),
                'Zinc': (11, 40)
            }

        return (carbohydrate_min, carbohydrate_max, total_fiber, protein, fat_min, fat_max, saturated_fat, trans_fat, alpha_linolenic_acid, linoleic_acid, dietary_cholesterol, total_water, vitamin_intake, mineral_intake)

    def back(self):
        self.rda_window.destroy()

class WeightAnalysis:
    def __init__(self, parent, start_date, end_date):
        self.parent = parent
        self.start_date = start_date  # Store start_date and end_date as instance attributes
        self.end_date = end_date
        self.weight_analysis_window = tk.Toplevel(parent)
        self.weight_analysis_window.title("Weight Analysis")
        self.weight_analysis_window.geometry('1166x718')
        self.center_window(self.weight_analysis_window)
        self.set_background("images\\background2.jpg")
        self.create_weight_analysis_content()  # Pass start_date and end_date to the method
    
    def center_window(self, window):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x_coordinate = (screen_width - 1166) // 2
        y_coordinate = (screen_height - 718) // 2
        window.geometry(f'1166x718+{x_coordinate}+{y_coordinate}')

    def set_background(self, image_path):
        bg_image = Image.open(image_path)
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self.weight_analysis_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def create_weight_analysis_content(self):
        # Create a scrollable canvas
        canvas = tk.Canvas(self.weight_analysis_window, bg='#FFF8F4', width=950, height=600)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(self.weight_analysis_window, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        additional_info_frame = tk.Frame(canvas, bg='#FFF8F4') # Add the frame to the canvas
        canvas.create_window((0, 0), window=additional_info_frame, anchor="nw")
        self.additional_info_frame = additional_info_frame  # Store the frame as an instance attribute

        # Create labels and entry boxes for weight analysis specific information
        # For example:
        # Label for weight analysis title
        analysis_title_label = tk.Label(additional_info_frame, text="Weight Analysis", font=("Helvetica", 20, "bold"), bg='#FFF8F4')
        analysis_title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Add a button to trigger displaying weight data
        display_weight_button = tk.Button(additional_info_frame, text="Display Weight Data", font=("Helvetica", 12), command=self.display_weight_entries)
        display_weight_button.grid(row=1, column=0, padx=10, pady=10)

        # Back Button
        back_button = tk.Button(additional_info_frame, text="Back", font=("yu gothic ui", 13, "bold"),
                                width=15, bd=0, cursor='hand2', fg='white', bg='#3047ff', command=self.back)
        back_button.grid(row=2, column=0, padx=10, pady=10)

    def display_weight_entries(self):
        db = Database()
        # Clear any existing content in the frame
        for widget in self.additional_info_frame.winfo_children():
            widget.destroy()

        try:
            weight_info = db.display_weight_log_by_date_range(LoginPage.username, self.start_date, self.end_date)
        except AttributeError:
            # If AttributeError occurs, try to get weight log using the username from SignupWindow
            weight_info = db.display_weight_log_by_date_range(SignupWindow.username, self.start_date, self.end_date)

        if weight_info:
            # Sort weight entries by date in ascending order
            weight_info_sorted = sorted(weight_info, key=lambda x: x[1])
            
            row_index = 0  # Track the row index for placing tables
            
            # Create Treeview widget for displaying weight entries
            tree = ttk.Treeview(self.additional_info_frame, columns=('Date', 'Weight'))
            tree.grid(row=row_index, column=0, padx=10, pady=10, sticky='nsew')

            # Add headings
            tree.heading('#0', text='Index')
            for col in tree['columns']:
                tree.heading(col, text=col)

            # Add data
            for i, entry in enumerate(weight_info_sorted):
                date = entry[1]
                weight = entry[2]

                tree.insert('', 'end', text=str(i+1), values=(date, f'{weight} kg'))

            # Set column width
            tree.column('#0', width=50)
            for col in tree['columns']:
                tree.column(col, width=100)

            # Create a frame to hold the new graph within the parent window
            graph_frame = tk.Frame(self.additional_info_frame, bg='#FFF8F4', width=600, height=400)
            graph_frame.grid(row=row_index, column=1, padx=10, pady=10)

            # Calculate weight entries per date from the table data
            weight_entries_per_date = {}
            for entry in weight_info_sorted:
                date = entry[1]
                weight = entry[2]
                if date not in weight_entries_per_date:
                    weight_entries_per_date[date] = []
                weight_entries_per_date[date].append(weight)

            # Extract data from weight_entries_per_date dictionary
            dates = list(weight_entries_per_date.keys())
            weights = [sum(weight_entries_per_date[date]) / len(weight_entries_per_date[date]) for date in dates]

            if weights:
                # Plotting the graph
                fig, ax = plt.subplots(figsize=(10, 6))

                # Plot weight data
                ax.plot(dates, weights, marker='o', linestyle='-', color='Slateblue', alpha=0.6, label='Weight')

                # Shade the area underneath the points
                ax.fill_between(dates, weights, color='skyblue', alpha=0.4)

                ax.set_xlabel('Date')
                ax.set_ylabel('Weight (kg)')
                ax.set_title('Weight Check-in')
                ax.legend()
                ax.grid(True)

                # Calculate y-axis range dynamically based on user's weight data with padding
                min_weight = min(weights) - 5
                max_weight = max(weights) + 5
                ax.set_ylim(min_weight, max_weight)

                # Save the plot as an image
                plt.tight_layout()
                plt.savefig('weight_check_in_graph.png')  
                plt.close()

                # Display the plot in the graph frame
                img = Image.open('weight_check_in_graph.png')
                img = img.resize((600, 400))  # Resize the image to fit the frame
                chart_img = ImageTk.PhotoImage(img)
                chart_label = tk.Label(graph_frame, image=chart_img)
                chart_label.image = chart_img
                chart_label.pack()

            else:
                # If no valid weight data found, display a message
                no_weight_label = tk.Label(graph_frame, text="No valid weight entries found.", font=("Helvetica", 12))
                no_weight_label.pack()

        else:
            # If no weight information found, display a message
            no_weight_label = tk.Label(self.additional_info_frame, text="No weight entries found.", font=("Helvetica", 12))
            no_weight_label.grid(row=0, column=0, padx=10, pady=10)

    def back(self):
        self.weight_analysis_window.destroy()

class HydrationAnalysis:
    def __init__(self, parent, start_date, end_date):
        self.parent = parent
        self.start_date = start_date  # Store start_date and end_date as instance attributes
        self.end_date = end_date
        self.hydration_analysis_window = tk.Toplevel(parent)
        self.hydration_analysis_window.title("Hydration Analysis")
        self.hydration_analysis_window.geometry('1166x718')
        self.center_window(self.hydration_analysis_window)
        self.set_background("images\\background2.jpg")
        self.create_hydration_analysis_content()  # Pass start_date and end_date to the method
        self.daily_water_goal_per_user = 2500  # Define daily water goal per user
    
    def center_window(self, window):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x_coordinate = (screen_width - 1166) // 2
        y_coordinate = (screen_height - 718) // 2
        window.geometry(f'1166x718+{x_coordinate}+{y_coordinate}')

    def set_background(self, image_path):
        bg_image = Image.open(image_path)
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self.hydration_analysis_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def create_hydration_analysis_content(self):
        # Create a scrollable canvas
        self.canvas = tk.Canvas(self.hydration_analysis_window, bg='#FFF8F4', width=950, height=600)
        self.canvas.place(x=100, y=50)

        # Add a scrollbar to the canvas
        scrollbar = tk.Scrollbar(self.hydration_analysis_window, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.additional_info_frame = tk.Frame(self.canvas, bg='#FFF8F4') 
        self.canvas.create_window((0, 0), window=self.additional_info_frame, anchor=tk.CENTER)

    # Implement other methods specific to hydration analysis if needed
        db = Database()
        try:
            hydration_info = db.display_hydration_log_by_date_range(LoginPage.username, self.start_date, self.end_date)
        except AttributeError:
            # If AttributeError occurs, try to get hydration log using the username from SignupWindow
            hydration_info = db.display_hydration_log_by_date_range(SignupWindow.username, self.start_date, self.end_date)
            
        if hydration_info:
            # Group hydration entries by date
            hydration_by_date = {}
            for hydration in hydration_info:
                date = hydration[1].split()[0]
                if date not in hydration_by_date:
                    hydration_by_date[date] = {'entries': [], 'total_amount': 0}
                hydration_by_date[date]['entries'].append(hydration)
                # Update total amount
                hydration_by_date[date]['total_amount'] += hydration[2]
            
            row_index = 2  # Track the row index for placing tables
            
            # Create separate table for each date
            for date, data in hydration_by_date.items():
                # Display the date above the table
                date_label = tk.Label(self.additional_info_frame, text=date, font=("Helvetica", 12))
                date_label.grid(row=row_index, column=2, padx=350, pady=5)

                # Create Treeview widget for displaying table
                tree = ttk.Treeview(self.additional_info_frame, columns=('Time', 'Amount'))
                tree.grid(row=row_index + 1, column=2, padx=350, pady=10)

                # Add headings
                tree.heading('#0', text='Index')
                for col in tree['columns']:
                    tree.heading(col, text=col)

                # Add data
                for i, entry in enumerate(data['entries']):
                    time = entry[1].split()[1]
                    amount = entry[2]

                    tree.insert('', 'end', text=str(i+1), values=(time, f'{amount} ml'))

                # Set column width
                tree.column('#0', width=50)
                for col in tree['columns']:
                    tree.column(col, width=100)

                # Display total amount below the table
                total_label = tk.Label(self.additional_info_frame, text=f"Total amount: {data['total_amount']} ml", font=("Helvetica", 10))
                total_label.grid(row=row_index + 2, column=1, padx=350, pady=5)

                # Create and integrate the progress bar
                progress_bar = ttk.Progressbar(self.additional_info_frame, orient="horizontal", length=200, mode="determinate")
                progress_bar.grid(row=row_index + 3, column=1, padx=350, pady=5)

                # Calculate percentage of daily water intake
                percentage_achieved = min(int(data['total_amount'] / 3000 * 100), 100)
                progress_bar["value"] = percentage_achieved

                # Dynamically set the background color of the label based on progress
                if percentage_achieved < 49:
                    bg_color = "#e6e6e6"
                else:
                    bg_color = "#06b025"  # Green color

                # Update the percentage label
                percentage_label = tk.Label(self.additional_info_frame, text=f"{percentage_achieved}%", font=("Helvetica", 8), background=bg_color)
                percentage_label.grid(row=row_index + 3, column=3, padx=350, pady=5)

                row_index += 4  # Move to the next row for the next table and date
            
            # After processing all hydration data, create and display the hydration graph
            # Extract data from hydration_by_date dictionary
            days = list(hydration_by_date.keys())
            actual_intake = [data['total_amount'] for data in hydration_by_date.values()]

            # Plotting the graph
            plt.figure(figsize=(10, 6))

            # Plot threshold line with the threshold value set to 3000 ml
            plt.plot(days, [3000] * len(days), linestyle='-', color='blue', label='Threshold')

            # Plot actual intake
            plt.plot(days, actual_intake, marker='s', linestyle='-', color='red', label='Actual Intake')

            # Annotate each point with its corresponding value
            for i, value in enumerate(actual_intake):
                plt.text(days[i], value, str(value), ha='center', va='bottom', fontsize=8)

            # Shade areas between lines
            plt.fill_between(days, actual_intake, 2000, where=(np.array(actual_intake) >= 2000), color='yellow', alpha=0.5)
            plt.fill_between(days, actual_intake, 2000, where=(np.array(actual_intake) < 2000), color='lightgreen', alpha=0.5)

            plt.xlabel('Days')
            plt.ylabel('Water Intake (ml)')
            plt.title('Weekly Hydration Tracker')
            plt.legend()
            plt.grid(True)

            # Save the plot as an image
            plt.tight_layout()
            plt.savefig('hydration_tracker_graph.png')

            # Display the plot in the frame
            img = Image.open('hydration_tracker_graph.png')
            img = img.resize((600, 400))  # Resize the image to fit the frame
            chart_img = ImageTk.PhotoImage(img)
            chart_label = tk.Label(self.additional_info_frame, image=chart_img)
            chart_label.image = chart_img
            chart_label.grid(row=row_index, column=2, columnspan=2, padx=350, pady=10)

        else:
            # If no hydration information found, display a message
            no_hydration_label = tk.Label(self.additional_info_frame, text="No hydration entries found.", font=("Helvetica", 12))
            no_hydration_label.grid(row=0, column=2, padx=350, pady=10)

    def back(self):
        self.hydration_analysis_window.destroy()

    def display_hydration_data(self):
        self.display_hydration_searches()

import matplotlib.dates as mdates
class FoodAnalysis:
    def __init__(self, parent, start_date, end_date):
        self.parent = parent
        self.start_date = start_date  # Store start_date and end_date as instance attributes
        self.end_date = end_date
        self.food_analysis_window = tk.Toplevel(parent)
        self.food_analysis_window.title("Food Analysis")
        self.food_analysis_window.geometry('1166x718')
        self.center_window(self.food_analysis_window)
        self.set_background("images\\background2.jpg")
        self.create_food_analysis_content()  # Pass start_date and end_date to the method
        self.daily_caloric_goal_per_user= 2250

    def center_window(self, window):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x_coordinate = (screen_width - 1166) // 2
        y_coordinate = (screen_height - 718) // 2
        window.geometry(f'1166x718+{x_coordinate}+{y_coordinate}')

    def set_background(self, image_path):
        bg_image = Image.open(image_path)
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self.food_analysis_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def create_food_analysis_content(self):
        # Create a scrollable canvas
        canvas = tk.Canvas(self.food_analysis_window, bg='#FFF8F4', width=950, height=600)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(self.food_analysis_window, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        additional_info_frame = tk.Frame(canvas, bg='#FFF8F4') # Add the frame to the canvas
        canvas.create_window((0, 0), window=additional_info_frame, anchor="nw")
        self.additional_info_frame = additional_info_frame  # Store the frame as an instance attribute

        # Create labels and entry boxes for food analysis specific information
        # For example:
        # Label for food analysis title
        analysis_title_label = tk.Label(additional_info_frame, text="Food Analysis", font=("Helvetica", 20, "bold"), bg='#FFF8F4')
        analysis_title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Add a button to trigger displaying food searches
        display_food_button = tk.Button(additional_info_frame, text="Display Food Searches", font=("Helvetica", 12), command=self.display_food_searches)
        display_food_button.grid(row=1, column=0, padx=10, pady=10)

        # Back Button
        back_button = tk.Button(additional_info_frame, text="Back", font=("yu gothic ui", 13, "bold"),
                                width=15, bd=0, cursor='hand2', fg='white', bg='#3047ff', command=self.back)
        back_button.grid(row=2, column=0, padx=10, pady=10)

    def display_food_searches(self):
        db=Database()
        # Clear any existing content in the frame
        for widget in self.additional_info_frame.winfo_children():
            widget.destroy()
        try:
            food_info = db.display_food_log_by_date_range(LoginPage.username, self.start_date, self.end_date)
        except AttributeError:
            # If AttributeError occurs, try to get food log using the username from SignupWindow
            food_info = db.display_food_log_by_date_range(SignupWindow.username, self.start_date, self.end_date)
        if food_info:
            # Group food items by date
            food_by_date = {}
            for food in food_info:
                date = food[1].split()[0]
                if date not in food_by_date:
                    food_by_date[date] = {'foods': [], 'totals': {'calories': 0, 'protein': 0, 'fat': 0, 'carb': 0, 'fibre': 0}}
                food_by_date[date]['foods'].append(food)
                # Update totals
                food_by_date[date]['totals']['calories'] += int(food[4])
                food_by_date[date]['totals']['protein'] += int(food[5])
                food_by_date[date]['totals']['fat'] += int(food[6])
                food_by_date[date]['totals']['carb'] += int(food[7])
                food_by_date[date]['totals']['fibre'] += int(food[8])

            row_index = 0  # Track the row index for placing tables

            # Create separate table for each date
            for date, data in food_by_date.items():
                # Display the date above the table
                date_label = tk.Label(self.additional_info_frame, text=date, font=("Helvetica", 12))
                date_label.grid(row=row_index, column=0, padx=10, pady=5, sticky='w')

                # Create Treeview widget for displaying table
                tree = ttk.Treeview(self.additional_info_frame, columns=('Time', 'Food', 'Quantity', 'Calories', 'Protein', 'Fat', 'Carb', 'Fibre'))
                tree.grid(row=row_index + 1, column=0, padx=10, pady=10, sticky='nsew')

                # Add headings
                tree.heading('#0', text='Index')
                for col in tree['columns']:
                    tree.heading(col, text=col)

                # Add data
                for i, food in enumerate(data['foods']):
                    time = food[1].split()[1]
                    # Convert floating-point values to integers
                    calories = int(food[4])
                    protein = int(food[5])
                    fat = int(food[6])
                    carb = int(food[7])
                    fibre = int(food[8])

                    tree.insert('', 'end', text=str(i+1), values=(time, food[2], food[3], f'{calories} kcal', f'{protein} g', f'{fat} g', f'{carb} g', f'{fibre} g'))

                # Set column width
                tree.column('#0', width=50)
                for col in tree['columns']:
                    tree.column(col, width=100)

                # Display totals below the table
                total_label = tk.Label(self.additional_info_frame, text=f"Total: Calories - {data['totals']['calories']} kcal, Protein - {data['totals']['protein']} g, Fat - {data['totals']['fat']} g, Carb - {data['totals']['carb']} g, Fibre - {data['totals']['fibre']} g", font=("Helvetica", 10))
                total_label.grid(row=row_index + 2, column=0, padx=10, pady=5, sticky='w')

                # Create bar graph
                bar_graph_frame = tk.Frame(self.additional_info_frame, bg='#FFF8F4')
                bar_graph_frame.grid(row=row_index + 3, column=0, padx=10, pady=10, sticky='nsew')
                self.create_bar_graph(bar_graph_frame, data['totals'])

                # Create pie chart
                pie_chart_frame = tk.Frame(self.additional_info_frame, bg='#FFF8F4')
                pie_chart_frame.grid(row=row_index + 4, column=0, padx=10, pady=10, sticky='nsew')
                self.create_pie_chart(pie_chart_frame, data['totals'])

                # # Create linear regression graph
                # linear_regression_frame = tk.Frame(self.additional_info_frame, bg='#FFF8F4')
                # linear_regression_frame.grid(row=row_index + 5, column=0, padx=10, pady=10, sticky='nsew')
                # self.analyze_calorie_consumption(linear_regression_frame)

                row_index += 5  # Move to the next row for the next table, date, and graphs
            start_date_dt = datetime.strptime(self.start_date, '%Y-%m-%d')
            end_date_dt = datetime.strptime(self.end_date, '%Y-%m-%d')

           # Sort dates to ensure order
            sorted_dates = sorted(food_by_date.keys(), key=lambda x: datetime.strptime(x, '%Y-%m-%d'))

            # Calculate the difference in days from the start_date for each date
            days_from_start = [(datetime.strptime(date, '%Y-%m-%d') - start_date_dt).days for date in sorted_dates]
            total_calories = [food_by_date[date]['totals']['calories'] for date in sorted_dates]

            # Perform linear regression
            days_from_start_np = np.array(days_from_start).reshape(-1, 1)  # Convert to numpy array and reshape for sklearn
            total_calories_np = np.array(total_calories)

            model = LinearRegression()
            model.fit(days_from_start_np, total_calories_np)

            # Determine the prediction period based on the user-selected date range
            date_difference = (end_date_dt - start_date_dt).days
            if date_difference <= 30:
                prediction_period = 7  # Predict for the next week if the period is less than a month
            elif date_difference <= 365:
                prediction_period = 30  # Predict for the next month if the period is less than a year
            else:
                prediction_period = 365  # Predict for the next year if the period is over a year

            # Extend the dates for prediction
            extended_dates = [start_date_dt + timedelta(days=x) for x in range(date_difference + prediction_period + 1)]
            extended_days_from_start = [(date - start_date_dt).days for date in extended_dates]

            # Predict for the extended period
            extended_days_from_start_np = np.array(extended_days_from_start).reshape(-1, 1)
            extended_predicted_calories = model.predict(extended_days_from_start_np)

            # Plotting with extended prediction
            plt.figure(figsize=(10, 6))
            dates_for_plotting = [datetime.strptime(date, '%Y-%m-%d') for date in sorted_dates]
            plt.scatter(dates_for_plotting, total_calories, color='blue', label='Actual Calories')

            # Plot the linear regression line for the user-selected duration in red
            user_selected_dates = extended_dates[:date_difference + 1]
            user_selected_predicted_calories = extended_predicted_calories[:date_difference + 1]
            plt.plot(user_selected_dates, user_selected_predicted_calories, color='red', label='Predicted Calories (User Selected)')

            # Plot the extended predicted line beyond the user-selected duration in green
            extended_prediction_dates = extended_dates[date_difference:]
            extended_prediction_calories = extended_predicted_calories[date_difference:]
            plt.plot(extended_prediction_dates, extended_prediction_calories, color='green', label='Extended Prediction')

            # Formatting the x-axis to display dates
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=max(len(extended_dates)//10, 1)))
            plt.gcf().autofmt_xdate()  # Rotation for readability

            plt.xlabel('Date')
            plt.ylabel('Total Calories')
            plt.title('Calorie Consumption Over Time with Future Prediction')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.savefig('linear_regression_with_prediction.png')
            plt.close()

            # Display the plot in the Tkinter frame
            img = Image.open('linear_regression_with_prediction.png')
            img = img.resize((550, 300))  # Resize the image to fit in the frame
            chart_img = ImageTk.PhotoImage(img)
            chart_label = tk.Label(self.additional_info_frame, image=chart_img, bg='#FFF8F4')
            chart_label.image = chart_img  # Keep a reference to prevent garbage-collection
            chart_label.grid(row=row_index, column=0, padx=10, pady=10, sticky='nsew')

        else:
            # If no food information found, display a message
            no_food_label = tk.Label(self.additional_info_frame, text="No food searches found.", font=("Helvetica", 12), bg='#FFF8F4')
            no_food_label.grid(row=0, column=0, padx=10, pady=10)

    def create_bar_graph(self, frame, totals):
            # Define the nutritional values
            nutrients = ['Protein', 'Fat', 'Carbs', 'Fibre']
            values = [totals['protein'], totals['fat'], totals['carb'], totals['fibre']]

            # Create the bar chart
            fig, ax = plt.subplots(figsize=(8, 5))  # Adjust the figure size as needed
            bars = ax.bar(nutrients, values, color=['blue', 'green', 'red', 'orange'])

            # Add labels and title
            ax.set_xlabel('Nutrients')
            ax.set_ylabel('Intake')
            ax.set_title('Daily Nutritional Intake')

            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)

            # Add text labels on top of each bar
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2.0, height, f'{value:.1f}', ha='center', va='bottom')

            # Display the plot
            plt.tight_layout()  # Adjust layout to prevent clipping of labels
            plt.savefig('bar_chart.png')  # Save the plot as an image
            plt.close()

            # Display the plot in the graph frame
            img = Image.open('bar_chart.png')
            img = img.resize((550, 300))  # Resize the image to fit the frame
            chart_img = ImageTk.PhotoImage(img)
            chart_label = tk.Label(frame, image=chart_img)
            chart_label.image = chart_img
            chart_label.pack()

    def create_pie_chart(self, frame, totals):
            # Define the nutritional values
            nutrients = ['Protein', 'Fat', 'Carbs', 'Fibre']
            values = [totals['protein'], totals['fat'], totals['carb'], totals['fibre']]

            # Create the pie chart
            sizes = values[:]
            labels = nutrients[:]
            colors = ['gold', 'lightcoral', 'lightskyblue', 'lightgreen']

            # Check if all sizes are zero
            if all(size == 0 for size in sizes):
                # If all sizes are zero, display a label indicating that the data is not available
                error_label = tk.Label(frame, text="Data not available for the Graphs", font=("Arial", 12), bg='#FFF8F4')
                error_label.pack()
            else:
                plt.figure(figsize=(6, 4))
                plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
                plt.axis('equal')
                plt.title('Macro-Nutritional Composition')

                # Display the pie chart
                plt.tight_layout()
                plt.savefig('pie_chart.png')
                plt.close()

                pie_img = Image.open('pie_chart.png')
                pie_img = pie_img.resize((550, 300))  # Resize the image to fit the frame
                pie_chart_img = ImageTk.PhotoImage(pie_img)
                pie_chart_label = tk.Label(frame, image=pie_chart_img)
                pie_chart_label.image = pie_chart_img
                pie_chart_label.pack()
                
    # def analyze_calorie_consumption(self, frame):
    #     db = Database()
    #     try:
    #         food_info = db.display_food_log_by_date_range(LoginPage.username, self.start_date, self.end_date)
    #     except AttributeError:
    #         food_info = db.display_food_log_by_date_range(SignupWindow.username, self.start_date, self.end_date)

    #     if food_info:
    #         # Convert start_date and end_date from string to datetime objects
    #         start_date_dt = datetime.strptime(self.start_date, '%Y-%m-%d')
    #         end_date_dt = datetime.strptime(self.end_date, '%Y-%m-%d')

    #         food_by_date = {}
    #         for food in food_info:
    #             date_str = food[1].split()[0]  # Assuming the date is in the first part of a datetime string
    #             date_dt = datetime.strptime(date_str, '%Y-%m-%d')
    #             if date_str not in food_by_date:
    #                 food_by_date[date_str] = {'totals': {'calories': 0}}
    #             food_by_date[date_str]['totals']['calories'] += int(food[4])

    #         # Sort dates to ensure order
    #         sorted_dates = sorted(food_by_date.keys(), key=lambda x: datetime.strptime(x, '%Y-%m-%d'))

    #         # Calculate the difference in days from the start_date for each date
    #         days_from_start = [(datetime.strptime(date, '%Y-%m-%d') - start_date_dt).days for date in sorted_dates]
    #         total_calories = [food_by_date[date]['totals']['calories'] for date in sorted_dates]

    #         # Perform linear regression
    #         days_from_start_np = np.array(days_from_start).reshape(-1, 1)  # Convert to numpy array and reshape for sklearn
    #         total_calories_np = np.array(total_calories)

    #         model = LinearRegression()
    #         model.fit(days_from_start_np, total_calories_np)
    #         predicted_calories = model.predict(days_from_start_np)

    #         # Plotting
    #         plt.figure(figsize=(10, 6))
    #         plt.scatter(days_from_start, total_calories, color='blue', label='Actual Calories')
    #         plt.plot(days_from_start, predicted_calories, color='red', label='Predicted Calories')
    #         plt.xlabel('Days from Start Date')
    #         plt.ylabel('Total Calories')
    #         plt.title('Calorie Consumption Over Time')
    #         plt.legend()
    #         plt.grid(True)
    #         plt.savefig('linear_regression_overall.png')
    #         plt.close()

    #         # Display in Tkinter frame
    #         img = Image.open('linear_regression_overall.png')
    #         img = img.resize((550, 300))
    #         chart_img = ImageTk.PhotoImage(img)
    #         chart_label = tk.Label(frame, image=chart_img)
    #         chart_label.image = chart_img
    #         chart_label.pack()

    #     else:
    #         print("No food information found.")
            
    def back(self):
        self.food_analysis_window.destroy()

class AnalysisWindow:
    def __init__(self, parent):
        self.parent = parent
        self.analysis_window = tk.Toplevel(parent)
        self.analysis_window.title("Analysis")
        self.analysis_window.geometry('1166x718')
        self.center_window(self.analysis_window)
        self.set_background("images/background2.jpg")
        self.create_analysis_content()

    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x_coordinate = (window.winfo_screenwidth() // 2) - (width // 2)
        y_coordinate = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'+{x_coordinate}+{y_coordinate}')


    def set_background(self, image_path):
        bg_image = Image.open(image_path)
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self.analysis_window, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def verify_dates(self):
        start_date_str = self.start_entry.get()
        end_date_str = self.end_entry.get()

        # Get current date
        current_date = dt.datetime.now().strftime("%Y-%m-%d")

        # Check if start date is in the correct format
        try:
            start_date = dt.datetime.strptime(start_date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid start date format. Please use YYYY-MM-DD.")
            return

        # Check if end date is in the correct format
        try:
            end_date = dt.datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid end date format. Please use YYYY-MM-DD.")
            return

        # Check if end date is not before start date
        if end_date < start_date:
            messagebox.showerror("Error", "End date cannot be before start date.")
            return

        # Check if start date or end date is in the future
        if start_date_str > current_date or end_date_str > current_date:
            messagebox.showerror("Error", "Dates cannot be in the future.")
            return

        # If dates are verified successfully, disable entry fields and replace Finalize Dates button with Edit Dates button
        self.start_entry.config(state='disabled')
        self.end_entry.config(state='disabled')
        self.finalize_button.grid_forget()  # Remove Finalize Dates button
        self.edit_button.grid(row=2, column=0, columnspan=2, padx=10, pady=20)  # Show Edit Dates button
        for button in self.option_buttons:
            button.config(state='normal')  # Disable analysis option buttons

    def edit_dates(self):
        self.start_entry.config(state='normal')
        self.end_entry.config(state='normal')
        self.edit_button.grid_forget()  # Remove Edit Dates button
        self.finalize_button.grid(row=2, column=0, columnspan=2, padx=10, pady=20)  # Show Finalize Dates button
        for button in self.option_buttons:
            button.config(state='disabled')  # Disable analysis option buttons

    def create_analysis_content(self):
        additional_info_frame = tk.Frame(self.analysis_window, bg='#FFF8F4', width=950, height=600)
        additional_info_frame.place(x=90, y=50)

        # Consistent Font Family and Size
        font_settings = ("Helvetica", 12)
    
        # Style Buttons
        button_style = {'bd': 0, 'font': ("yu gothic ui", 13, "bold"), 'width': 15, 'fg': 'white'}

        self.finalize_button = tk.Button(additional_info_frame, text="Finalize Dates", bg='#53c200', **button_style, command=self.verify_dates)
        self.finalize_button.grid(row=2, column=0, columnspan=2, padx=10, pady=20)

        self.edit_button = tk.Button(additional_info_frame, text="Edit Dates", bg='#53c200', **button_style, command=self.edit_dates)
        self.edit_button.grid(row=2, column=0, columnspan=2, padx=10, pady=20)
        self.edit_button.grid_forget()  # Hide Edit Dates button initially

        analysis_buttons_frame = tk.Frame(additional_info_frame, bg='#FFF8F4')
        analysis_buttons_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=20, sticky="nsew")

        # Create analysis option buttons with state='disabled' by default
        option_buttons = []
        option_buttons.append(self.create_button(button_label="Personalised RDA Analysis", frame=analysis_buttons_frame, image_path="images/RDAC.PNG", row=0, column=0, command=self.analysis_option_1))
        option_buttons.append(self.create_button(button_label="Food Analysis", frame=analysis_buttons_frame, image_path="images/FoodC.PNG", row=0, column=1, command=self.analysis_option_2))
        option_buttons.append(self.create_button(button_label="Hydration Analysis", frame=analysis_buttons_frame, image_path="images/LiquidA.png", row=0, column=2, command=self.analysis_option_3))
        option_buttons.append(self.create_button(button_label="Weight Analysis", frame=analysis_buttons_frame, image_path="images/WeightC.PNG", row=0, column=3, command=self.analysis_option_4))

        # Get today's date
        today_date = dt.datetime.now().strftime("%Y-%m-%d")

        # Calculate yesterday's date
        yesterday_date = (dt.datetime.now() - dt.timedelta(days=1)).strftime("%Y-%m-%d")

        # Entry labels for start date and end date
        start_label = tk.Label(additional_info_frame, text="Start Date:", font=font_settings, bg='#FFF8F4')
        start_label.grid(row=0, column=0, padx=200, pady=10, sticky="e")
        self.start_entry = tk.Entry(additional_info_frame, font=font_settings)
        self.start_entry.insert(0, yesterday_date)  # Set default value as yesterday's date
        self.start_entry.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        end_label = tk.Label(additional_info_frame, text="End Date:", font=font_settings, bg='#FFF8F4')
        end_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.end_entry = tk.Entry(additional_info_frame, font=font_settings)
        self.end_entry.insert(0, today_date)  # Set default value as today's date
        self.end_entry.grid(row=0, column=1, padx=90, pady=10, sticky="w")

        back_button = tk.Button(additional_info_frame, text="Back", bg='#3047ff', **button_style, command=self.back)
        back_button.grid(row=5, column=0,columnspan=2, padx=10, pady=40)

         # Store analysis option buttons and entries for later use
        self.option_buttons = option_buttons
        self.entries = [self.start_entry, self.end_entry]
    
    def create_button(self, button_label, frame, image_path, row, column, command):
        label_frame = ttk.LabelFrame(frame, text=button_label)
        label_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        img = Image.open(image_path)
        img = img.resize((200, 150))
        photo = ImageTk.PhotoImage(img)
        button = tk.Button(label_frame, image=photo, command=command, state='disabled')  # Set state as disabled
        button.image = photo
        button.pack(padx=10, pady=10)
        return button

    def analysis_option_1(self):
        RDAWindow(self.analysis_window)

    def analysis_option_2(self):
        start_date = self.start_entry.get()
        end_date = self.end_entry.get()
        FoodAnalysis(self.analysis_window, start_date, end_date)

    def analysis_option_3(self):
        start_date = self.start_entry.get()
        end_date = self.end_entry.get()
        HydrationAnalysis(self.analysis_window, start_date, end_date)

    def analysis_option_4(self):
        start_date = self.start_entry.get()
        end_date = self.end_entry.get()
        WeightAnalysis(self.analysis_window, start_date, end_date)

    def back(self):
        self.analysis_window.destroy()

class HomePage:
    def __init__(self):
        self.home_root = tk.Toplevel()
        #self.db = Database()  # Create a Database instance
        self.home_root.title("Home Page")
        self.home_root.geometry('1166x718')
        self.home_root.config(bg="#FFF8F4")  # Peachy color
        self.center_window(self.home_root)  # Center the window
        self.set_background("images\\background2.jpg")  # Set background image
        self.create_navigation_boxes()
        self.home_root.protocol("WM_DELETE_WINDOW", self.close_application)  # Intercept window close event
    def center_window(self, window):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x_coordinate = (screen_width - 1166) // 2  # Adjusted for window width
        y_coordinate = (screen_height - 718) // 2  # Adjusted for window height
        window.geometry(f'1166x718+{x_coordinate}+{y_coordinate}')

    def set_background(self, image_path):
        bg_image = Image.open(image_path)
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self.home_root, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def close_application(self):
        sys.exit()  # Exit the entire application

    def open_food_log(self):  
        # Pass the existing database instance to DailyJournal
        DailyJournal(self.home_root)

    def open_meal_planner(self):  # Add self parameter
        MealPlanner(self.home_root)

    def open_recipe_searcher(self):  # Add self parameter
        RecipeSearchWindow(self.home_root)
    
    def open_reports(self):  # Add self parameter
        AnalysisWindow(self.home_root)

    def open_settings(self):  
        SettingsPage(self.home_root)

    def open_about(self):  
        AboutUsWindow(self.home_root)

    def create_navigation_boxes(self):
        background_frame = tk.Frame(self.home_root, bg='#FFF8F4', width=950, height=600)
        background_frame.place(x=200, y=70)

        # Navigation boxes
        self.create_navigation_box(background_frame, "Daily Food Log", "images\\daily.jpg", 0, 0, self.open_food_log)
        self.create_navigation_box(background_frame, "Meal Planner", "images\\planner.png", 0, 1, self.open_meal_planner)
        self.create_navigation_box(background_frame, "Recipe Finder", "images\\recipe_finder.png", 0, 2, self.open_recipe_searcher)
        self.create_navigation_box(background_frame, "Analysis", "images\\analysis.png", 1, 0, self.open_reports)
        self.create_navigation_box(background_frame, "Settings", "images\\Settings.png", 1, 1, self.open_settings)
        self.create_navigation_box(background_frame, "About Us/Info", "images/logo.png", 1, 2, self.open_about)

        # Center the navigation boxes
        for i in range(3):
            background_frame.grid_columnconfigure(i, weight=1)

        # Exit button
        btn_exit = tk.Button(background_frame, text="EXIT", font=("yu gothic ui", 13, "bold"), width=15, bd=0,
                           cursor='hand2', fg='white', command=self.close_application, bg='#53c200')
        btn_exit.grid(row=2, column=1, pady=10)  # Adjust row and column as needed


    def create_navigation_box(self, parent, text, image_path, row, column, command):
        box = ttk.LabelFrame(parent, text=text)
        box.grid(row=row, column=column, padx=20, pady=10, sticky="nsew")
        img = ImageTk.PhotoImage(Image.open(image_path).resize((200, 200)))
        label = ttk.Button(box, image=img,command=command)
        label.image = img
        label.pack()
        # Bind double-click event to the label
    
if __name__ == '__main__':
    window = tk.Tk()
    LoginPage(window)
    window.mainloop()
