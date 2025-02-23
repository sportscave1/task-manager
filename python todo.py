from flask import Flask, request, jsonify
import sqlite3
import sys

app = Flask(__name__)
DB_FILE = "tasks.db"

def initialize_db():
    """Creates the tasks table if it doesn't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                due_date TEXT NOT NULL,
                priority TEXT NOT NULL CHECK(priority IN ('High', 'Medium', 'Low')),
                category TEXT NOT NULL,
                completed INTEGER DEFAULT 0
            )
        """)
        conn.commit()

@app.route("/")
def home():
    return "Task Manager API is running!"

@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Retrieve tasks from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY completed, priority, due_date")
        tasks = cursor.fetchall()
    return jsonify(tasks)

@app.route("/add_task", methods=["POST"])
def add_task():
    """Add a new task from JSON data."""
    data = request.json
    task_name = data.get("task", "Unnamed Task")
    due_date = data.get("due_date", "2025-12-31")
    priority = data.get("priority", "Medium")
    category = data.get("category", "General")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (task, due_date, priority, category) VALUES (?, ?, ?, ?)",
                       (task_name, due_date, priority, category))
        conn.commit()
    return jsonify({"message": "Task added!"}), 201

@app.route("/mark_completed", methods=["POST"])
def mark_task_completed():
    """Mark a task as completed."""
    data = request.json
    task_id = data.get("task_id")
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        conn.commit()
    return jsonify({"message": "Task marked as completed!"})

@app.route("/remove_task", methods=["POST"])
def remove_task():
    """Remove a task by ID."""
    data = request.json
    task_id = data.get("task_id")
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    return jsonify({"message": "Task removed!"})

if __name__ == "__main__":
    initialize_db()
    app.run(host="0.0.0.0", port=10000)
