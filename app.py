from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

app = Flask(__name__)

# Health Tracker DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://health_wo8z_user:Sq4WNAfXtfsWRJpG8F1oqgD5TLKlHPgI@dpg-d1h46gfgi27c73c99mng-a.oregon-postgres.render.com/health_wo8z'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Emergency DB (loaded separately using SQLAlchemy core)
EMERGENCY_DB_URL = 'postgresql://medical_app_db_user:Xe7GZUcwOBofWtgX9lf5UvVzRAZVoiE0@dpg-d1gf17emcj7s73cmobpg-a/medical_app_db'
EmergencyBase = declarative_base()
emergency_engine = create_engine(EMERGENCY_DB_URL)
EmergencySession = sessionmaker(bind=emergency_engine)
emergency_session = EmergencySession()

# ---------------- Health Tracker Models ----------------

class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Water(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicine = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(5), nullable=False)  # HH:MM format

# ---------------- Routes ----------------

@app.route('/')
def home():
    return "Health Tracker Backend Running"

@app.route('/health')
def health():
    return render_template('health.html')

@app.route('/save_mood', methods=['POST'])
def save_mood():
    data = request.get_json()
    mood = data.get("mood")
    if mood:
        entry = Mood(mood=mood)
        db.session.add(entry)
        db.session.commit()
    return jsonify({"status": "success"})

@app.route('/save_water', methods=['POST'])
def save_water():
    data = request.get_json()
    count = data.get("count", 0)
    water = Water.query.first()
    if not water:
        water = Water(count=count)
        db.session.add(water)
    else:
        water.count = count
    db.session.commit()
    return jsonify({"status": "saved"})

@app.route('/get_water', methods=['GET'])
def get_water():
    water = Water.query.first()
    return jsonify({"count": water.count if water else 0})

@app.route('/add_reminder', methods=['POST'])
def add_reminder():
    data = request.get_json()
    med = data.get("medicine")
    time = data.get("time")
    if med and time:
        reminder = Reminder(medicine=med, time=time)
        db.session.add(reminder)
        db.session.commit()
    return jsonify({"status": "added"})

@app.route('/get_reminders', methods=['GET'])
def get_reminders():
    reminders = Reminder.query.all()
    result = [{"id": r.id, "medicine": r.medicine, "time": r.time} for r in reminders]
    return jsonify(result)

@app.route('/delete_reminder/<int:id>', methods=['DELETE'])
def delete_reminder(id):
    reminder = Reminder.query.get(id)
    if reminder:
        db.session.delete(reminder)
        db.session.commit()
    return jsonify({"status": "deleted"})

# ---------------- Run App ----------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
