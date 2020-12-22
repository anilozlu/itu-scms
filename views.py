from flask import render_template, request, redirect, url_for
from passlib.hash import pbkdf2_sha256 as hasher
import mysql.connector
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
def home_page():
    return render_template("home.html")

def clubs_page():
    mycursor.execute("SELECT * FROM Clubs")
    clubs = list(mycursor)
    if clubs:
        length = len(clubs)
    else:
        length = 0
    return render_template("clubs.html", len = length, clubs = clubs)

def login_page():
    return render_template("login.html")

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

def students_page():
    mycursor.execute("SELECT * FROM Students")
    students = list(mycursor)
    if students:
        length = len(students)
    else:
        length = 0
    return render_template("students.html", len = length, students = students)