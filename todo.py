from flask import Flask, request, jsonify
import os

app = Flask(__name__)
TASKS_FILE = "tasks.txt"

def load_tasks():
    """Load tasks from a file."""
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as file:
        return [line.strip() for line in file.readlines()]

def save_tasks(tasks):
    """Save tasks to a file."""
    with open(TASKS_FILE, "w") as file:
        for task in tasks:
            file.write(task + "\n")

tasks = load_tasks()

@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Retrieve tasks."""
    return jsonify(tasks)

@app.route("/add_task", methods=["POST"])
def add_task():
    """Add a new task."""
    data = request.json
    task = data.get("task")
    if not task:
        return jsonify({"error": "Task cannot be empty"}), 400
    tasks.append(task)
    save_tasks(tasks)
    return jsonify({"message": "Task added!", "tasks": tasks})

@app.route("/remove_task", methods=["POST"])
def remove_task():
    """Remove a task by index."""
    data = request.json
    try:
        task_index = int(data.get("task_index")) - 1
        if 0 <= task_index < len(tasks):
            removed_task = tasks.pop(task_index)
            save_tasks(tasks)
            return jsonify({"message": f"Task '{removed_task}' removed!", "tasks": tasks})
        return jsonify({"error": "Invalid task number"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input"}), 400

@app.route("/save_tasks", methods=["POST"])
def save_tasks_api():
    """Save tasks manually."""
    save_tasks(tasks)
    return jsonify({"message": "Tasks saved!"})

@app.route("/load_tasks", methods=["POST"])
def load_tasks_api():
    """Reload tasks from file."""
    global tasks
    tasks = load_tasks()
    return jsonify({"message": "Tasks loaded!", "tasks": tasks})

@app.route("/")
def home():
    return "Task Manager API is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
