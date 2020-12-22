from flask import render_template

def home_page():
    return render_template("home.html")

def clubs_page():
    return render_template("clubs.html")

def create_club():
    return render_template("create_club.html")