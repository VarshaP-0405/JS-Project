from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# PostgreSQL connection from environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "postgresql://medical_app_db_user:Xe7GZUcwOBofWtgX9lf5UvVzRAZVoiE0@dpg-d1gf17emcj7s73cmobpg-a/medical_app_db").replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --------------------- MODELS ---------------------

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicine_name = db.Column(db.String(100))
    time = db.Column(db.String(20))

class MoodWater(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(100))
    water = db.Column(db.Integer)

class EmergencyContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    phone = db.Column(db.String(20))

# --------------------- ROUTES ---------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health_page():
    return render_template("health.html")

@app.route("/emergency")
def emergency():
    contacts = EmergencyContact.query.all()
    return render_template("emergency.html", contacts=contacts)

# ---------- Mood and Water Intake ----------

@app.route("/submit_mood_water", methods=["POST"])
def submit_mood_water():
    mood = request.form["mood"]
    water = request.form["water"]
    entry = MoodWater(mood=mood, water=water)
    db.session.add(entry)
    db.session.commit()
    return redirect("/health")

# ---------- Reminders ----------

@app.route("/add_reminder", methods=["POST"])
def add_reminder():
    medicine_name = request.form["medicine"]
    time = request.form["time"]
    reminder = Reminder(medicine_name=medicine_name, time=time)
    db.session.add(reminder)
    db.session.commit()
    return redirect("/health")

@app.route("/get_reminders")
def get_reminders():
    reminders = Reminder.query.all()
    return jsonify([
        {"id": r.id, "medicine_name": r.medicine_name, "time": r.time}
        for r in reminders
    ])

@app.route("/delete_reminder/<int:id>", methods=["DELETE"])
def delete_reminder(id):
    reminder = Reminder.query.get_or_404(id)
    db.session.delete(reminder)
    db.session.commit()
    return jsonify({"success": True})

# ---------- Emergency Contacts ----------

@app.route("/add_contact", methods=["POST"])
def add_contact():
    name = request.form["name"]
    phone = request.form["phone"]
    contact = EmergencyContact(name=name, phone=phone)
    db.session.add(contact)
    db.session.commit()
    return redirect("/emergency")

@app.route("/delete_contact/<int:id>", methods=["POST"])
def delete_contact(id):
    contact = EmergencyContact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    return redirect("/emergency")

# --------------------- MAIN ---------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
