from flask import Flask, render_template
from flask_login import LoginManager
import views

lm=LoginManager()

@lm.user_loader
def load_user(user_id):
    return views.get_user(user_id)

def create_app():
    app = Flask(__name__)
    app.config.from_object("settings")
    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/clubs", view_func=views.clubs_page)
    app.add_url_rule("/clubs/<int:club_id>", view_func=views.club_page, methods=["GET", "POST"])
    app.add_url_rule("/create_club", view_func=views.create_club, methods=["GET", "POST"])
    app.add_url_rule("/login", view_func=views.login_page, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=views.logout_page)
    app.add_url_rule("/register", view_func=views.register_page, methods=["GET", "POST"])
    app.add_url_rule("/students", view_func=views.students_page)
    app.add_url_rule("/students/<int:member_id>", view_func=views.student_page)
    app.add_url_rule("/clubs/edit/<int:club_id>", view_func=views.edit_club, methods=["GET", "POST"])

    lm.init_app(app)
    lm.login_view = "login_page"

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port = 8080, debug = True)