from flask import Flask, render_template, request, redirect, session, url_for
import joblib
import os
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Load model
model = joblib.load("model/model.pkl")

# Load feature names
with open("model/feature_names.json", "r") as f:
    feature_names = json.load(f)

USER_FILE = "data/users.json"
LOG_FILE = "data/logs.json"

os.makedirs("data", exist_ok=True)

# ---------------------------
# Helper Functions
# ---------------------------

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def save_log(entry):
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        except:
            logs = []
    logs.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

def load_accuracy():
    try:
        with open("model/metrics.json", "r") as f:
            data = json.load(f)
            return round(data["accuracy"] * 100, 2)
    except:
        return 0

# ---------------------------
# Routes
# ---------------------------

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        users = load_users()

        if username in users:
            return "User already exists!"

        users[username] = password
        save_users(users)

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username in users and check_password_hash(users[username], password):
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Credentials!"

    return render_template("login.html")
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html",
                           user=session["user"],
                           feature_names=feature_names)
@app.route("/analyze", methods=["POST"])
def analyze():
    if "user" not in session:
        return redirect(url_for("login"))

    input_data = []

    for feature in feature_names:
        value = request.form.get(feature)
        if value:
            input_data.append(1)
        else:
            input_data.append(0)

    prediction = model.predict([input_data])
    probability = model.predict_proba([input_data])

    result = "Malicious Extension" if prediction[0] == 1 else "Safe Extension"
    confidence = round(max(probability[0]) * 100, 2)

    accuracy = load_accuracy()

    save_log({
        "user": session["user"],
        "result": result
    })

    return render_template("result.html",
                           result=result,
                           confidence=confidence,
                           accuracy=accuracy)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
