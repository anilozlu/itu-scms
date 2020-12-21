from flask import Flask, render_template
from flaskext.mysql import MySQL
import views

def create_app():
    app = Flask(__name__)
    app.config.from_object("settings")
    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/clubs", view_func=views.clubs_page)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port = 8080, debug = True)