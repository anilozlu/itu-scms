from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from passlib.hash import pbkdf2_sha256 as hasher
import mysql.connector
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

mydb = mysql.connector.connect(
    host="anilozlu.mysql.pythonanywhere-services.com",
    user="anilozlu",
    password="1a2a3a4a"
)
mycursor = mydb.cursor(buffered=True)

mycursor.execute("CREATE DATABASE IF NOT EXISTS anilozlu$scms")
mycursor.execute("USE anilozlu$scms")
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
mycursor.execute("""CREATE TABLE IF NOT EXISTS Student_clubs(
    user_id BIGINT UNSIGNED,
    club_id BIGINT UNSIGNED,
    role VARCHAR(30),
    visible TINYINT,
    PRIMARY KEY (user_id, club_id),
    FOREIGN KEY (user_id) REFERENCES Students(user_id) ON DELETE CASCADE,
    FOREIGN KEY (club_id) REFERENCES Clubs(club_id) ON DELETE CASCADE);""")
mycursor.execute("""CREATE TABLE IF NOT EXISTS Club_students(
    club_id BIGINT UNSIGNED,
    user_id BIGINT UNSIGNED,
    PRIMARY KEY (user_id, club_id),
    FOREIGN KEY (club_id) REFERENCES Clubs(club_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Students(user_id) ON DELETE CASCADE);""")
mycursor.execute("""CREATE TABLE IF NOT EXISTS Club_events(
    club_id BIGINT UNSIGNED,
    event_id BIGINT UNSIGNED,
    user_id BIGINT UNSIGNED,
    PRIMARY KEY (club_id, event_id),
    FOREIGN KEY (club_id) REFERENCES Clubs(club_id),
    FOREIGN KEY (event_id) REFERENCES Events(event_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Students(user_id) ON DELETE CASCADE);""")
mydb.commit()
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
    mycursor.execute("SELECT password FROM Students WHERE user_id = '" + str(user_id) + "';")
    password = list(mycursor)
    if password:
        password = password[0][0]
        user = User(user_id, password) if password else None
        return user
    else:
        return None

def home_page():
    mycursor.execute("SELECT COUNT(user_id) FROM Students;")
    count = list(mycursor)[0][0]
    return render_template("home.html", count=count)

@login_required
def clubs_page():
    mycursor.execute("SELECT COUNT(club_id) FROM Clubs;")
    count = list(mycursor)[0][0]
    mycursor.execute("SELECT * FROM Clubs")
    clubs = list(mycursor)
    if clubs:
        length = len(clubs)
    else:
        length = 0
    return render_template("clubs.html", len = length, clubs = clubs, count=count)
@login_required
def logout_page():
    logout_user()
    flash("You have logged out.")
    return redirect(url_for("home_page"))

def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.data["username"]
        mycursor.execute("SELECT user_id FROM Students WHERE mail = '" + username + "';")
        user_id = list(mycursor)
        if not user_id:
            flash("You have entered wrong email or password.")
            return redirect(url_for("login_page"))
        user_id = user_id[0][0]
        user = get_user(user_id)
        if user is not None:
            password = form.data["password"]
            if hasher.verify(password, user.password):
                login_user(user)
                flash("You have logged in.")
                next_page = request.args.get("next", url_for("home_page"))
                return redirect(next_page)
        flash("You have entered wrong email or password.")
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
        mydb.commit()
        user_id = current_user.username
        mycursor.execute("SELECT club_id FROM Clubs WHERE name = '" + club_name + "';")
        club_id = list(mycursor)[0][0]
        mycursor.execute("INSERT INTO Student_clubs (user_id, club_id, role, visible) VALUES ('" + str(user_id) + "','" + str(club_id) + "', 'Creator', 1);")
        mycursor.execute("INSERT INTO Club_students (club_id, user_id) VALUES ('" + str(club_id) + "', '" + str(user_id) +"');")
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
@login_required
def club_page(club_id):
    mycursor.execute("""SELECT COUNT(Club_students.club_id)
                        FROM Club_students
                        INNER JOIN Student_clubs
                        ON Club_students.user_id=Student_clubs.user_id AND Club_students.club_id=Student_clubs.club_id
                        WHERE Club_students.club_id = """ + str(club_id) + " GROUP BY Club_students.club_id;")
    count = list(mycursor)[0][0]
    mycursor.execute("SELECT name, description FROM Clubs WHERE club_id = '" + str(club_id) + "';")
    club = list(mycursor)
    mycursor.execute("SELECT user_id FROM Club_students WHERE club_id = '" + str(club_id) + "';")
    member_ids = list(mycursor)
    user_id = current_user.username
    if member_ids:
        member_id = "("
        for member in member_ids:
            member_id += str(member[0]) + ", "
        member_id = member_id[:-2] + ")"
        mycursor.execute("SELECT user_id, full_name, mail FROM Students WHERE user_id IN " + member_id + ";")
        members = list(mycursor)
        mycursor.execute("SELECT role FROM Student_clubs WHERE user_id = '" + str(user_id) + "' AND club_id = '" + str(club_id) + "';")
        try:
            role = mycursor.next()
            admin = role[0] == "Creator"
        except StopIteration:
            admin = False
        member_of = str(user_id) in member_id
    else:
        members = None
        member_of = False
        admin = False
    mycursor.execute("SELECT * FROM Events INNER JOIN Club_events ON Events.event_id=Club_events.event_id WHERE Club_events.club_id={};".format(club_id))
    events = list(mycursor)
    if events:
        events = events
    else:
        events = None
    if request.form:
        if "club_join" in request.form:
            if request.form["club_join"] == "edit":
                return redirect(url_for("edit_club", club_id = club_id))
            elif request.form["club_join"] == "join":
                mycursor.execute("INSERT INTO Club_students (user_id, club_id) VALUES ('" + str(user_id) + "', '" + str(club_id) +"');")
                mycursor.execute("INSERT INTO Student_clubs (user_id, club_id, role, visible) VALUES ('" + str(user_id) + "', '" + str(club_id) + "', 'Member', 1);")
                mydb.commit()
                flash("You have joined this club.")
            elif request.form["club_join"] == "leave":
                mycursor.execute("DELETE Club_students,Student_clubs FROM Club_students INNER JOIN Student_clubs ON Club_students.user_id=Student_clubs.user_id AND Club_students.club_id=Student_clubs.club_id INNER JOIN Students ON Students.user_id=Club_students.user_id WHERE Students.user_id = " + str(user_id) + " AND Club_students.club_id = " + str(club_id) + ";")
                mydb.commit()
                flash("You have left this club.")
        elif "member_kick" in request.form:
            kick_id = request.form["member_kick"]
            mycursor.execute("DELETE Club_students,Student_clubs FROM Club_students INNER JOIN Student_clubs ON Club_students.user_id=Student_clubs.user_id AND Club_students.club_id=Student_clubs.club_id INNER JOIN Students ON Students.user_id=Club_students.user_id WHERE Students.user_id = " + str(kick_id) + " AND Club_students.club_id = " + str(club_id) + ";")
        elif "create_event" in request.form:
            return redirect(url_for("create_event", club_id=club_id))
        return redirect(url_for("club_page", club_id = club_id))
    return render_template("club.html", club=club[0], members=members, member_of=member_of, admin=admin, count=count, events=events)
@login_required
def student_page(member_id):
    mycursor.execute("""SELECT COUNT(Club_students.user_id)
                        FROM Club_students
                        INNER JOIN Student_clubs
                        ON Club_students.user_id=Student_clubs.user_id AND Club_students.club_id=Student_clubs.club_id
                        WHERE Club_students.user_id = """ + str(member_id) + " GROUP BY Club_students.user_id;")
    count = list(mycursor)
    count = count[0][0] if count else 0
    mycursor.execute("SELECT full_name, mail FROM Students WHERE user_id = '" + str(member_id) + "';")
    student = list(mycursor)
    mycursor.execute("SELECT club_id FROM Student_clubs WHERE user_id = '" + str(member_id) + "';")
    club_ids = list(mycursor)
    if club_ids:
        club_id = "("
        for club in club_ids:
            for c_id in club:
                club_id += str(c_id) + ", "
        club_id = club_id[:-2] + ")"
        mycursor.execute("SELECT club_id, name FROM Clubs WHERE club_id IN " + club_id + ";")
        clubs = list(mycursor)
    else:
        clubs = None
    return render_template("student.html", member=student, clubs=clubs, count=count)
@login_required
def edit_club(club_id):
    mycursor.execute("SELECT role FROM Student_clubs WHERE user_id = '" + str(current_user.username) + "' AND club_id = '" + str(club_id) + "';")
    role = list(mycursor)[0]
    admin = role[0] == "Creator"
    if not admin:
        abort(401)
    mycursor.execute("SELECT * FROM Clubs WHERE club_id = '" + str(club_id) + "';")
    club=list(mycursor)[0]
    if request.method == "GET":
        return render_template("edit_club.html", club=club)
    else:
        club_name = request.form["name"]
        club_description = request.form["description"]
        mycursor.execute("UPDATE Clubs SET name = '" + club_name + "', description = '" + club_description + "' WHERE club_id = '" + str(club_id) + "';")
        mydb.commit()
        flash("You have successfully editted your club's information.")
        return redirect(url_for("club_page", club_id = club_id))
@login_required
def create_event(club_id):
    mycursor.execute("SELECT role FROM Student_clubs WHERE user_id = '" + str(current_user.username) + "' AND club_id = '" + str(club_id) + "';")
    role = list(mycursor)[0]
    admin = role[0] == "Creator"
    if not admin:
        abort(401)
    mycursor.execute("SELECT * FROM Clubs WHERE club_id = '" + str(club_id) + "';")
    club=list(mycursor)[0]
    if request.method == "GET":
        return render_template("create_event.html", club=club)
    else:
        event_name = request.form["name"]
        event_description = request.form["description"]
        mycursor.execute("INSERT INTO Events (name, description) VALUES ('" + event_name + "', '" + event_description +"');")
        mycursor.execute("SELECT LAST_INSERT_ID()")
        event_id = mycursor.next()[0]
        mycursor.execute("INSERT INTO Club_events (club_id, event_id) VALUES ('{}', '{}');".format(club_id, event_id))
        mydb.commit()
        return redirect(url_for("club_page", club_id=club[0]))
@login_required
def delete_event(event_id):
    mycursor.execute("SELECT club_id FROM Club_events INNER JOIN Events ON Club_events.event_id=Events.event_id WHERE Club_events.event_id = {}".format(event_id))
    club_id = list(mycursor)[0][0]
    mycursor.execute("DELETE Club_events, Events from Club_events INNER JOIN Events ON Club_events.event_id=Events.event_id WHERE Events.event_id = {}".format(event_id))
    mydb.commit()
    return redirect(url_for("club_page", club_id=club_id))
@login_required
def event_page(event_id):
    mycursor.execute("SELECT club_id FROM Club_events INNER JOIN Events ON Club_events.event_id=Events.event_id WHERE Club_events.event_id = {}".format(event_id))
    club_id = list(mycursor)[0][0]
    mycursor.execute("SELECT role FROM Student_clubs WHERE user_id = '" + str(current_user.username) + "' AND club_id = '" + str(club_id) + "';")
    role = list(mycursor)[0]
    admin = role[0] == "Creator"
    if request.method == "GET":
        mycursor.execute("SELECT * FROM Events WHERE event_id = {}".format(event_id))
        event = list(mycursor)[0]
        return render_template("event.html", event=event, club_id=club_id, admin=admin)
    else:
        if "edit_event" in request.form:
            return redirect(url_for("edit_event", event_id=event_id))
        elif "view_event" in request.form:
            mycursor.execute("SELECT * FROM Events WHERE event_id = {}".format(event_id))
            event = list(mycursor)[0]
            return render_template("event.html", event=event, club_id=club_id, admin=admin)
        elif "delete_event" in request.form:
            mycursor.execute("DELETE FROM Events WHERE event_id = {}".format(event_id))
            mydb.commit()
            flash("Event deleted.")
            return redirect(url_for("club_page", club_id=club_id))
@login_required
def edit_event(event_id):
    if request.method == "GET":
        mycursor.execute("SELECT * FROM Events WHERE event_id = {}".format(event_id))
        event = list(mycursor)[0]
        mycursor.execute("SELECT club_id FROM Club_events INNER JOIN Events ON Club_events.event_id=Events.event_id WHERE Club_events.event_id = {}".format(event_id))
        club_id = list(mycursor)[0][0]
        return render_template("edit_event.html", event=event, club_id=club_id)
    else:
        name = request.form["name"]
        description = request.form["description"]
        mycursor.execute("UPDATE Events SET name = '{}', description = '{}' WHERE event_id={};".format(name, description, event_id))
        mydb.commit()
        return redirect(url_for("event_page", event_id = event_id))