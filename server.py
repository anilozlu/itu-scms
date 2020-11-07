from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home_page():
    return render_template("home.html")

@app.route("/clubs")
def clubs_page():
    return render_template("clubs.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 8080, debug = True)