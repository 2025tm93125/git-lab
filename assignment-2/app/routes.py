from datetime import date
import random

from flask import Blueprint, current_app, jsonify, request
from werkzeug.security import check_password_hash

from .database import get_db_connection

api = Blueprint("api", __name__)

PROGRAM_TEMPLATES = {
    "Strength": [
        "Full-body strength training, 3 days per week",
        "Upper/lower body split, 4 days per week"
    ],
    "Cardio": [
        "Cardio conditioning, 4 days per week",
        "Low-impact endurance training, 3 days per week"
    ],
    "Weight Management": [
        "Combined strength and cardio, 4 days per week"
    ]
}

def db():
    return get_db_connection(current_app.config["DATABASE"])

@api.get("/")
def home():
    return jsonify({
        "application": "ACEest Fitness & Gym",
        "status": "running"
    })

@api.get("/health")
def health():
    return jsonify({"status": "healthy"})

@api.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = db()
    user = conn.execute(
        "SELECT username, password, role FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "message": "Login successful",
        "username": user["username"],
        "role": user["role"]
    })

@api.post("/api/clients")
def add_client():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()

    if not name:
        return jsonify({"error": "Client name is required"}), 400

    conn = db()
    try:
        cur = conn.execute(
            """INSERT INTO clients
               (name, age, height, weight, target_weight,
                target_adherence, membership_status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                name, data.get("age"), data.get("height"),
                data.get("weight"), data.get("target_weight"),
                data.get("target_adherence"), "Active"
            )
        )
        conn.commit()
        client_id = cur.lastrowid
    except Exception as exc:
        conn.close()
        if "UNIQUE constraint failed" in str(exc):
            return jsonify({"error": "Client already exists"}), 409
        return jsonify({"error": "Unable to save client"}), 400

    conn.close()
    return jsonify({"message": "Client created", "id": client_id, "name": name}), 201

@api.get("/api/clients")
def list_clients():
    conn = db()
    rows = conn.execute(
        "SELECT * FROM clients ORDER BY name"
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@api.post("/api/clients/<int:client_id>/program")
def generate_program(client_id):
    conn = db()
    client = conn.execute(
        "SELECT id, name FROM clients WHERE id = ?", (client_id,)
    ).fetchone()

    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404

    program_type = request.args.get("type", "Strength")
    if program_type not in PROGRAM_TEMPLATES:
        conn.close()
        return jsonify({"error": "Unsupported program type"}), 400

    program = random.choice(PROGRAM_TEMPLATES[program_type])
    conn.execute(
        "UPDATE clients SET program = ? WHERE id = ?",
        (program, client_id)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "client": client["name"],
        "program_type": program_type,
        "program": program
    })

@api.get("/api/clients/<int:client_id>/membership")
def membership(client_id):
    conn = db()
    row = conn.execute(
        "SELECT name, membership_status, membership_end FROM clients WHERE id = ?",
        (client_id,)
    ).fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Client not found"}), 404

    return jsonify(dict(row))

@api.get("/api/clients/<int:client_id>/progress")
def progress(client_id):
    conn = db()
    client = conn.execute(
        "SELECT name FROM clients WHERE id = ?", (client_id,)
    ).fetchone()

    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404

    rows = conn.execute(
        """SELECT week, adherence FROM progress
           WHERE client_name = ? ORDER BY id""",
        (client["name"],)
    ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])

@api.post("/api/clients/<int:client_id>/workouts")
def add_workout(client_id):
    data = request.get_json(silent=True) or {}
    workout_type = str(data.get("workout_type", "")).strip()
    workout_date = data.get("date") or date.today().isoformat()
    duration = data.get("duration_min")

    if not workout_type or duration is None:
        return jsonify({
            "error": "workout_type and duration_min are required"
        }), 400

    try:
        duration = int(duration)
        date.fromisoformat(workout_date)
        if duration <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid date or workout duration"}), 400

    conn = db()
    client = conn.execute(
        "SELECT name FROM clients WHERE id = ?", (client_id,)
    ).fetchone()

    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404

    cur = conn.execute(
        """INSERT INTO workouts
           (client_name, date, workout_type, duration_min, notes)
           VALUES (?, ?, ?, ?, ?)""",
        (
            client["name"], workout_date, workout_type,
            duration, data.get("notes", "")
        )
    )
    conn.commit()
    workout_id = cur.lastrowid
    conn.close()

    return jsonify({"message": "Workout added", "id": workout_id}), 201

@api.get("/api/clients/<int:client_id>/workouts")
def list_workouts(client_id):
    conn = db()
    client = conn.execute(
        "SELECT name FROM clients WHERE id = ?", (client_id,)
    ).fetchone()

    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404

    rows = conn.execute(
        """SELECT date, workout_type, duration_min, notes
           FROM workouts WHERE client_name = ? ORDER BY date DESC""",
        (client["name"],)
    ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])
