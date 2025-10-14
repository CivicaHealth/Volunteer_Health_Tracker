from flask import Flask, render_template, request, redirect, url_for
import threading
import time
import datetime

app = Flask(__name__)

shots = [
    {"id": 1, "name": "Flu shot", "frequency": 365},
    {"id": 2, "name": "Tetanus", "frequency": 3650}
]
volunteers = [
    # {"name": "Test Volunteer", "email": "voltest@email.com", "shots": {1: "2022-06-01", 2: "2022-01-01"}}
]
settings = {
    "admin_email": "admin@email.com"
}

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
    return render_template('dashboard.html', volunteers=volunteers, shots=shots)

@app.route('/settings', methods=["GET", "POST"])
def settings_page():
    global shots, settings
    if request.method == "POST":
        email = request.form.get("admin_email")
        if email:
            settings["admin_email"] = email
        if "add_shot" in request.form:
            name = request.form.get("new_shot_name")
            freq = request.form.get("new_shot_frequency")
            if name and freq:
                shots.append({"id": len(shots)+1, "name": name, "frequency": int(freq)})
        elif "remove_shot" in request.form:
            remove_id = int(request.form.get("remove_shot"))
            shots = [s for s in shots if s["id"] != remove_id]
        else:
            for shot in shots:
                new_name = request.form.get(f"shot_name_{shot['id']}")
                new_freq = request.form.get(f"shot_frequency_{shot['id']}")
                if new_name is not None and new_freq is not None:
                    shot["name"] = new_name
                    shot["frequency"] = int(new_freq)
        return redirect(url_for('settings_page'))
    return render_template('settings.html', shots=shots, settings=settings)

@app.route('/add_volunteer', methods=["GET", "POST"])
def add_reminder():
    global volunteers
    if request.method == "POST":
        name = request.form.get("volunteer")
        email = request.form.get("email")
        shot_records = {}
        for shot in shots:
            last_date = request.form.get(f"last_date_{shot['id']}")
            if last_date:
                shot_records[shot["id"]] = last_date
        volunteers.append({"name": name, "email": email, "shots": shot_records})
        return redirect(url_for('dashboard'))
    return render_template('reminder_form.html', shots=shots, volunteer=None, edit_mode=False)

@app.route('/edit_volunteer/<volunteer_name>', methods=["GET", "POST"])
def edit_volunteer(volunteer_name):
    v = next((vol for vol in volunteers if vol["name"] == volunteer_name), None)
    if not v:
        return "Volunteer not found", 404
    if request.method == "POST":
        v["email"] = request.form.get("email")
        for shot in shots:
            last_date = request.form.get(f"last_date_{shot['id']}")
            if last_date:
                v["shots"][shot["id"]] = last_date
            elif shot["id"] in v["shots"]:
                del v["shots"][shot["id"]]
        return redirect(url_for("dashboard"))
    return render_template("reminder_form.html", volunteer=v, shots=shots, edit_mode=True)

@app.route('/remove_volunteer/<volunteer_name>', methods=["GET", "POST"])
def remove_volunteer(volunteer_name):
    global volunteers
    volunteers = [vol for vol in volunteers if vol["name"] != volunteer_name]
    return redirect(url_for("dashboard"))

# --- START AUTOMATIC SCHEDULER THREAD ---
threading.Thread(target=automatic_scheduler, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)
