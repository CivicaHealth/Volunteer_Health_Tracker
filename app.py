from flask import Flask, render_template, request, redirect, url_for
import threading
import time
import datetime
import json
import os
from cryptography.fernet import Fernet

app = Flask(__name__)

# -----------------------------
# ENCRYPTED JSON PERSISTENCE
# -----------------------------
DATA_FILE = "data.json.enc"
# Generate a key once with Fernet.generate_key() and keep it safe
SECRET_KEY = b'NKDQg_XiWgmZntejdwGG_prcARNyjcjb51Q4xfB2jyA='
fernet = Fernet(SECRET_KEY)

def save_data_encrypted(shots, medical_history, volunteers, settings):
    data = json.dumps({
        "shots": shots,
        "medical_history": medical_history,
        "volunteers": volunteers,
        "settings": settings
    }).encode()
    encrypted = fernet.encrypt(data)
    with open(DATA_FILE, "wb") as f:
        f.write(encrypted)

def load_data_encrypted():
    if not os.path.exists(DATA_FILE):
        return [], [], [], {"admin_email": "admin@email.com"}
    with open(DATA_FILE, "rb") as f:
        encrypted = f.read()
    data = fernet.decrypt(encrypted)
    obj = json.loads(data)
    return obj.get("shots", []), obj.get("medical_history", []), obj.get("volunteers", []), obj.get("settings", {"admin_email": "admin@email.com"})

# -----------------------------
# LOAD DATA
# -----------------------------
shots, medical_history, volunteers, settings = load_data_encrypted()

# -----------------------------
# AUTOMATIC SHOT REMINDER SYSTEM
# -----------------------------
def automatic_scheduler():
    while True:
        today = datetime.date.today()
        for v in volunteers:
            for shot in shots:
                last_date_str = v["shots"].get(shot["id"])
                if last_date_str:
                    last_date = datetime.datetime.strptime(last_date_str, "%Y-%m-%d").date()
                    next_due = last_date + datetime.timedelta(days=shot["frequency"])
                    if next_due <= today:
                        print(f"Would send email to {v['email']} and {settings['admin_email']} for {shot['name']} overdue on {next_due}")
                        print(f"""
Subject: Reminder: {shot['name']} due for {v['name']}
To: {v['email']} and {settings['admin_email']}

Dear {v['name']},
You are due for your {shot['name']} since {next_due}. Please take this shot as soon as possible.
                        """)
        time.sleep(10)  # Check every 10 seconds for demo

# -----------------------------
# DASHBOARD
# -----------------------------
@app.route('/')
def dashboard():
    today = datetime.date.today()
    for v in volunteers:
        v['next_due'] = {}
        for shot in shots:
            last_date_str = v["shots"].get(shot["id"])
            if last_date_str:
                last_date = datetime.datetime.strptime(last_date_str, "%Y-%m-%d").date()
                next_due = last_date + datetime.timedelta(days=shot["frequency"])
                v['next_due'][shot["id"]] = next_due.strftime("%Y-%m-%d")
            else:
                v['next_due'][shot["id"]] = "No record"
    return render_template('dashboard.html', volunteers=volunteers, shots=shots, medical_history=medical_history)

# -----------------------------
# SETTINGS PAGE
# -----------------------------
@app.route('/settings', methods=["GET", "POST"])
def settings_page():
    global shots, medical_history, settings
    if request.method == "POST":
        email = request.form.get("admin_email")
        if email:
            settings["admin_email"] = email

        # --- Add / Remove / Update Shots ---
        if "add_shot" in request.form:
            name = request.form.get("new_shot_name")
            freq = request.form.get("new_shot_frequency")
            if name and freq:
                shots.append({"id": len(shots) + 1, "name": name, "frequency": int(freq)})

        elif "remove_shot" in request.form:
            remove_id = int(request.form.get("remove_shot"))
            shots = [s for s in shots if s["id"] != remove_id]

        # --- Add / Remove / Update Medical History ---
        elif "add_medical" in request.form:
            name = request.form.get("new_medical_name")
            if name:
                medical_history.append({"id": len(medical_history) + 1, "name": name})

        elif "remove_medical" in request.form:
            remove_id = int(request.form.get("remove_medical"))
            medical_history = [m for m in medical_history if m["id"] != remove_id]

        else:
            # Update all shot and medical names/frequencies
            for shot in shots:
                new_name = request.form.get(f"shot_name_{shot['id']}")
                new_freq = request.form.get(f"shot_frequency_{shot['id']}")
                if new_name is not None and new_freq is not None:
                    shot["name"] = new_name
                    shot["frequency"] = int(new_freq)
            for medical in medical_history:
                new_name = request.form.get(f"medical_name_{medical['id']}")
                if new_name is not None:
                    medical["name"] = new_name

        save_data_encrypted(shots, medical_history, volunteers, settings)
        return redirect(url_for('settings_page'))

    return render_template('settings.html', shots=shots, medical_history=medical_history, settings=settings)

# -----------------------------
# ADD VOLUNTEER
# -----------------------------
@app.route('/add_volunteer', methods=["GET", "POST"])
def add_reminder():
    global volunteers
    if request.method == "POST":
        name = request.form.get("volunteer")
        email = request.form.get("email")

        # Shots
        shot_records = {}
        for shot in shots:
            last_date = request.form.get(f"last_date_{shot['id']}")
            if last_date:
                shot_records[shot["id"]] = last_date

        # Medical History Notes
        medical_records = {}
        for med in medical_history:
            note = request.form.get(f"medical_note_{med['id']}")
            if note:
                medical_records[med["id"]] = note

        volunteers.append({
            "name": name,
            "email": email,
            "shots": shot_records,
            "medical_history": medical_records
        })

        save_data_encrypted(shots, medical_history, volunteers, settings)
        return redirect(url_for('dashboard'))

    return render_template('reminder_form.html', shots=shots, medical_history=medical_history,
                           volunteer=None, edit_mode=False)

# -----------------------------
# EDIT VOLUNTEER
# -----------------------------
@app.route('/edit_volunteer/<volunteer_name>', methods=["GET", "POST"])
def edit_volunteer(volunteer_name):
    v = next((vol for vol in volunteers if vol["name"] == volunteer_name), None)
    if not v:
        return "Volunteer not found", 404

    if request.method == "POST":
        v["email"] = request.form.get("email")

        # Update shots
        for shot in shots:
            last_date = request.form.get(f"last_date_{shot['id']}")
            if last_date:
                v["shots"][shot["id"]] = last_date
            elif shot["id"] in v["shots"]:
                del v["shots"][shot["id"]]

        # Update medical history notes
        for med in medical_history:
            note = request.form.get(f"medical_note_{med['id']}")
            if note:
                v["medical_history"][med["id"]] = note
            elif med["id"] in v["medical_history"]:
                del v["medical_history"][med["id"]]

        save_data_encrypted(shots, medical_history, volunteers, settings)
        return redirect(url_for("dashboard"))

    return render_template("reminder_form.html", volunteer=v, shots=shots,
                           medical_history=medical_history, edit_mode=True)

# -----------------------------
# REMOVE VOLUNTEER
# -----------------------------
@app.route('/remove_volunteer/<volunteer_name>', methods=["GET", "POST"])
def remove_volunteer(volunteer_name):
    global volunteers
    volunteers = [vol for vol in volunteers if vol["name"] != volunteer_name]
    save_data_encrypted(shots, medical_history, volunteers, settings)
    return redirect(url_for("dashboard"))

# -----------------------------
# START BACKGROUND THREAD
# -----------------------------
threading.Thread(target=automatic_scheduler, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)
