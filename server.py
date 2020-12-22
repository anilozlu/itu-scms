from flask import Flask, render_template
import mysql.connector
import views

def create_app():
    app = Flask(__name__)
    app.config.from_object("settings")
    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/clubs", view_func=views.clubs_page)
    app.add_url_rule("/create_club", view_func=views.create_club)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port = 8080, debug = True)