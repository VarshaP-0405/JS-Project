from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# PostgreSQL config - Render will auto-inject DATABASE_URL env variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///fallback.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Water(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicine = db.Column(db.String(100))
    time = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return render_template("health.html")

@app.route("/emergency")
def emergency():
    return render_template("emergency.html")

@app.route("/save_mood", methods=["POST"])
def save_mood():
    data = request.json
    mood = Mood(mood=data.get("mood"))
    db.session.add(mood)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route("/get_mood")
def get_mood():
    latest = Mood.query.order_by(Mood.timestamp.desc()).first()
    return jsonify({"mood": latest.mood if latest else ""})

@app.route("/save_water", methods=["POST"])
def save_water():
    data = request.json
    water = Water(count=data.get("count"))
    db.session.add(water)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route("/get_water")
def get_water():
    latest = Water.query.order_by(Water.timestamp.desc()).first()
    return jsonify({"count": latest.count if latest else 0})

@app.route("/add_reminder", methods=["POST"])
def add_reminder():
    data = request.json
    reminder = Reminder(medicine=data["medicine"], time=data["time"])
    db.session.add(reminder)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route("/get_reminders")
def get_reminders():
    reminders = Reminder.query.all()
    return jsonify([{"id": r.id, "medicine": r.medicine, "time": r.time} for r in reminders])

@app.route("/delete_reminder/<int:reminder_id>", methods=["DELETE"])
def delete_reminder(reminder_id):
    reminder = Reminder.query.get(reminder_id)
    if reminder:
        db.session.delete(reminder)
        db.session.commit()
    return jsonify({"status": "deleted"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
