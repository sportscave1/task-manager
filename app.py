from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Initialize Flask App
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # In production, set a real secret key (env var, etc.)

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ------------------
# MODELS
# ------------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.String(50))
    priority = db.Column(db.String(20))
    category = db.Column(db.String(50))
    completed = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------
# ROUTES
# ------------------

@app.route("/")
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", tasks=tasks)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid username or password")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Choose a different one.")
            return redirect(url_for("register"))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# Add Task Route
@app.route("/add", methods=["POST"])
@login_required
def add_task():
    task_text = request.form.get("task")
    due_date = request.form.get("due_date")
    priority = request.form.get("priority")

    if not task_text:
        return jsonify({"error": "Task description is required"}), 400

    task = Task(user_id=current_user.id, task=task_text, due_date=due_date, priority=priority)
    db.session.add(task)
    db.session.commit()

    return jsonify({"message": "Task added successfully!", "id": task.id})

# Edit Task Route
@app.route("/edit/<int:task_id>", methods=["POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get(task_id)
    if not task or task.user_id != current_user.id:
        return jsonify({"error": "Task not found or unauthorized"}), 403

    # If you want to ONLY update the 'task' field:
    new_task_text = request.form.get("task")
    if new_task_text:
        task.task = new_task_text

    # If you want to update due_date and priority too (only if provided):
    new_due_date = request.form.get("due_date")
    new_priority = request.form.get("priority")
    if new_due_date:
        task.due_date = new_due_date
    if new_priority:
        task.priority = new_priority

    db.session.commit()
    return jsonify({"message": "Task updated successfully!"})

# Remove Task Route
@app.route("/remove/<int:task_id>", methods=["POST"])
@login_required
def remove_task(task_id):
    task = Task.query.get(task_id)
    if not task or task.user_id != current_user.id:
        return jsonify({"error": "Task not found or unauthorized"}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task removed successfully!"})

# Mark Task as Completed
@app.route("/complete/<int:task_id>", methods=["POST"])
@login_required
def complete_task(task_id):
    task = Task.query.get(task_id)
    if not task or task.user_id != current_user.id:
        return jsonify({"error": "Task not found or unauthorized"}), 403

    task.completed = not task.completed
    db.session.commit()
    return jsonify({"message": "Task status updated!", "completed": task.completed})

# API to Get All Tasks (For Mobile App, optional)
@app.route("/api/tasks", methods=["GET"])
@login_required
def api_get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        "id": t.id,
        "task": t.task,
        "due_date": t.due_date,
        "priority": t.priority,
        "completed": t.completed
    } for t in tasks])

# ------------------
# INIT DB + RUN
# ------------------

# Create DB tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # For local testing:
    # app.run(debug=True, host="0.0.0.0", port=5000)
    # On Render, the gunicorn command will run your app instead.
    app.run(debug=True)
