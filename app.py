from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Use PostgreSQL in Render (or fallback to SQLite locally for development)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///health_tracker.db"
).replace("postgres://", "postgresql://")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------- Models ----------
class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(50))
    date = db.Column(db.String(20))

class Water(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    date = db.Column(db.String(20))

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicine = db.Column(db.String(100))
    time = db.Column(db.String(10))

class EmergencyContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return render_template("health.html")

@app.route("/emergency")
def emergency():
    return render_template("emergency.html")

# ----- Mood Tracker -----
@app.route("/save_mood", methods=["POST"])
def save_mood():
    mood_data = request.json.get("mood")
    today = datetime.now().strftime("%Y-%m-%d")
    mood_entry = Mood.query.filter_by(date=today).first()
    if mood_entry:
        mood_entry.mood = mood_data
    else:
        db.session.add(Mood(mood=mood_data, date=today))
    db.session.commit()
    return jsonify({"status": "saved"})

@app.route("/get_mood")
def get_mood():
    today = datetime.now().strftime("%Y-%m-%d")
    mood_entry = Mood.query.filter_by(date=today).first()
    return jsonify({"mood": mood_entry.mood if mood_entry else ""})

# ----- Water Tracker -----
@app.route("/save_water", methods=["POST"])
def save_water():
    count = request.json.get("count", 0)
    today = datetime.now().strftime("%Y-%m-%d")
    entry = Water.query.filter_by(date=today).first()
    if entry:
        entry.count = count
    else:
        db.session.add(Water(count=count, date=today))
    db.session.commit()
    return jsonify({"status": "saved"})

@app.route("/get_water")
def get_water():
    today = datetime.now().strftime("%Y-%m-%d")
    entry = Water.query.filter_by(date=today).first()
    return jsonify({"count": entry.count if entry else 0})

# ----- Medicine Reminders -----
@app.route("/add_reminder", methods=["POST"])
def add_reminder():
    data = request.json
    db.session.add(Reminder(medicine=data["medicine"], time=data["time"]))
    db.session.commit()
    return jsonify({"status": "added"})

@app.route("/get_reminders")
def get_reminders():
    reminders = Reminder.query.all()
    return jsonify([{"id": r.id, "medicine": r.medicine, "time": r.time} for r in reminders])

@app.route("/delete_reminder/<int:id>", methods=["DELETE"])
def delete_reminder(id):
    reminder = Reminder.query.get(id)
    if reminder:
        db.session.delete(reminder)
        db.session.commit()
    return jsonify({"status": "deleted"})

# ----- Emergency Contacts -----
@app.route("/add_contact", methods=["POST"])
def add_contact():
    data = request.json
    db.session.add(EmergencyContact(name=data["name"], phone=data["phone"]))
    db.session.commit()
    return jsonify({"status": "success"})

@app.route("/get_contacts")
def get_contacts():
    contacts = EmergencyContact.query.all()
    return jsonify([{"id": c.id, "name": c.name, "phone": c.phone} for c in contacts])

@app.route("/delete_contact/<int:id>", methods=["DELETE"])
def delete_contact(id):
    contact = EmergencyContact.query.get(id)
    if contact:
        db.session.delete(contact)
        db.session.commit()
        return jsonify({"status": "deleted"})
    return jsonify({"status": "not found"}), 404

# ---------- Run ----------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
