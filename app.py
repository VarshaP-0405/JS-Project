from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import webbrowser
import threading


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medical_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ------------------ Models ------------------
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

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

# ------------------ Routes ------------------

@app.route("/", methods=["GET", "HEAD"])
def index():
    return render_template("index.html")

@app.route("/health", methods=["GET", "HEAD"])
def health():
    return render_template("health.html")

@app.route("/emergency",methods=["GET", "HEAD"])
def emergency():
    return render_template("emergency.html")

# ------------------ Mood Tracker ------------------

@app.route("/save_mood", methods=["POST"])
def save_mood():
    mood_data = request.json.get("mood")
    today = datetime.now().strftime("%Y-%m-%d")
    mood_entry = Mood.query.filter_by(date=today).first()
    if mood_entry:
        mood_entry.mood = mood_data
    else:
        mood_entry = Mood(mood=mood_data, date=today)
        db.session.add(mood_entry)
    db.session.commit()
    return jsonify({"status": "saved"})

@app.route("/get_mood")
def get_mood():
    today = datetime.now().strftime("%Y-%m-%d")
    mood_entry = Mood.query.filter_by(date=today).first()
    return jsonify({"mood": mood_entry.mood if mood_entry else ""})

# ------------------ Water Tracker ------------------

@app.route("/save_water", methods=["POST"])
def save_water():
    data = request.json
    today = datetime.now().strftime("%Y-%m-%d")
    water_entry = Water.query.filter_by(date=today).first()
    if water_entry:
        water_entry.count = data.get("count", 0)
    else:
        water_entry = Water(count=data.get("count", 0), date=today)
        db.session.add(water_entry)
    db.session.commit()
    return jsonify({"status": "saved"})

@app.route("/get_water")
def get_water():
    today = datetime.now().strftime("%Y-%m-%d")
    water_entry = Water.query.filter_by(date=today).first()
    return jsonify({"count": water_entry.count if water_entry else 0})

# ------------------ Medicine Reminders ------------------

@app.route("/add_reminder", methods=["POST"])
def add_reminder():
    data = request.json
    reminder = Reminder(medicine=data["medicine"], time=data["time"])
    db.session.add(reminder)
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

# ------------------ Emergency Contacts ------------------

@app.route("/add_contact", methods=["POST"])
def add_contact():
    data = request.get_json()
    new_contact = EmergencyContact(name=data['name'], phone=data['phone'])
    db.session.add(new_contact)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route("/get_contacts")
def get_contacts():
    contacts = EmergencyContact.query.all()
    result = [{"id": c.id, "name": c.name, "phone": c.phone} for c in contacts]
    return jsonify(result)

@app.route("/delete_contact/<int:id>", methods=["DELETE"])
def delete_contact(id):
    contact = EmergencyContact.query.get(id)
    if contact:
        db.session.delete(contact)
        db.session.commit()
        return jsonify({"status": "deleted"})
    return jsonify({"status": "not found"}), 404

# ------------------ Start App ------------------

if __name__ == "__main__":
    threading.Timer(1.5, open_browser).start()
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000)) 
    app.run(host="0.0.0.0", port=port)
    
   
