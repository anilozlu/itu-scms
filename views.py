from flask import render_template, request, redirect, url_for, flash
from flask_login import UserMixin, login_user, login_required, logout_user
from passlib.hash import pbkdf2_sha256 as hasher
import mysql.connector
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

mydb = mysql.connector.connect(
    host="localhost",
    user="anil",
    password="deneme"
)
mycursor = mydb.cursor(buffered=True)

mycursor.execute("CREATE DATABASE IF NOT EXISTS scms")
mycursor.execute("USE scms")
mycursor.execute("""CREATE TABLE IF NOT EXISTS Students(
    user_id SERIAL,
    mail VARCHAR(50),
    password VARCHAR(150),
    full_name VARCHAR(50),
    PRIMARY KEY (user_id));""")
mycursor.execute("""CREATE TABLE IF NOT EXISTS Clubs(
    club_id SERIAL,
    name VARCHAR(50),
    description TEXT,
    PRIMARY KEY (club_id));""")
mycursor.execute("""CREATE TABLE IF NOT EXISTS Events(
    event_id SERIAL,
    description TEXT,
    name VARCHAR(100),
    PRIMARY KEY (event_id));""")
#mycursor.execute("""CREATE TABLE IF NOT EXISTS Student_clubs(
#    user_id SERIAL,
#    club_id SERIAL,
#    role VARCHAR(30),
#    visible TINYINT,
#    PRIMARY KEY (user_id, club_id),
#    FOREIGN KEY (club_id) REFERENCES Clubs(club_id));""")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])

    password = PasswordField("Password", validators=[DataRequired()])

class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.active = True
    
    def get_id(self):
        return self.username

    @property
    def is_active(self):
        return self.active

def get_user(user_id):
    mycursor.execute("SELECT password FROM Students WHERE user_id = " + str(user_id) + ";")
    password = list(mycursor)[0][0]
    user = User(user_id, password) if password else None
    return user

def home_page():
    return render_template("home.html")

@login_required
def clubs_page():
    mycursor.execute("SELECT * FROM Clubs")
    clubs = list(mycursor)
    if clubs:
        length = len(clubs)
    else:
        length = 0
    return render_template("clubs.html", len = length, clubs = clubs)

def logout_page():
    logout_user()
    flash("You have logged out.")
    return redirect(url_for("home_page"))

def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.data["username"]
        mycursor.execute("SELECT user_id FROM Students WHERE mail = '" + username + "';")
        user_id = list(mycursor)[0][0]
        user = get_user(user_id)
        if user is not None:
            password = form.data["password"]
            if hasher.verify(password, user.password):
                login_user(user)
                flash("You have logged in.")
                next_page = request.args.get("next", url_for("home_page"))
                return redirect(next_page)
        flash("Invalid credentials.")
    return render_template("login.html", form=form)

def register_page():
    if request.method == "GET":
        return render_template("register.html")
    else:
        user_mail = request.form["mail"]
        user_name = request.form["name"]
        user_password = hasher.hash(request.form["password"])
        mycursor.execute("INSERT INTO Students (mail, full_name, password) VALUES (\""+ user_mail + "\", \""+ user_name +"\", \""+ user_password +"\");")
        mydb.commit()
        return redirect(url_for("home_page"))
@login_required
def create_club():
    if request.method == "GET":
        return render_template("create_club.html")
    else:
        club_name = request.form["name"]
        club_description = request.form["description"]
        mycursor.execute("INSERT INTO Clubs (name, description) VALUES (\""+club_name+"\", \""+club_description+"\");")
        mycursor.execute("SELECT * FROM Clubs;")
        mydb.commit()
        return redirect(url_for("create_club"))
@login_required
def students_page():
    mycursor.execute("SELECT * FROM Students")
    students = list(mycursor)
    if students:
        length = len(students)
    else:
        length = 0
    return render_template("students.html", len = length, students = students)
