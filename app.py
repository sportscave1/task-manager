from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Initialize Flask App
app = Flask(__name__, static_url_path="/static")  # Ensure Flask serves static files
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")  # Secure this in production

# Database Config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
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
        """ Hashes and stores the user's password """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """ Checks if the provided password matches the stored hash """
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
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
def home():
    """ Public homepage - Shows login/register buttons if user is not logged in. """
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))  # Redirect logged-in users to their dashboard
    return render_template("index.html")  # Public homepage

@app.route("/dashboard")
@login_required
def dashboard():
    """ Protected user dashboard - Shows tasks dynamically via JavaScript """
    return render_template("dashboard.html")  # Ensure dashboard.html exists!

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        
        flash("Invalid username or password", "danger")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            flash("Username already exists. Choose a different one.", "warning")
            return redirect(url_for("register"))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

# ------------------
# TASK API ROUTES (Protected)
# ------------------

@app.route("/tasks", methods=["GET"])
@login_required
def get_tasks():
    """ Fetch tasks and return JSON (used by frontend JavaScript) """
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify([
        {
            "id": t.id,
            "task": t.task,
            "due_date": t.due_date,
            "priority": t.priority,
            "category": t.category,
            "completed": t.completed
        } for t in tasks
    ])

@app.route("/add", methods=["POST"])
@login_required
def add_task():
    """ Add a new task """
    task_text = request.form.get("task")
    due_date = request.form.get("due_date")
    priority = request.form.get("priority", "Medium")

    if not task_text:
        return jsonify({"error": "Task description is required"}), 400

    task = Task(user_id=current_user.id, task=task_text, due_date=due_date, priority=priority)
    db.session.add(task)
    db.session.commit()

    return jsonify({"message": "Task added successfully!", "id": task.id})

@app.route("/edit/<int:task_id>", methods=["POST"])
@login_required
def edit_task(task_id):
    """ Edit an existing task """
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({"error": "Task not found or unauthorized"}), 403

    task_text = request.form.get("task")
    task.due_date = request.form.get("due_date")
    task.priority = request.form.get("priority")

    if task_text:
        task.task = task_text

    db.session.commit()
    return jsonify({"message": "Task updated successfully!"})

@app.route("/remove/<int:task_id>", methods=["POST"])
@login_required
def remove_task(task_id):
    """ Remove a task """
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({"error": "Task not found or unauthorized"}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task removed successfully!"})

@app.route("/complete/<int:task_id>", methods=["POST"])
@login_required
def complete_task(task_id):
    """ Toggle task completion status """
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({"error": "Task not found or unauthorized"}), 403

    task.completed = not task.completed
    db.session.commit()
    return jsonify({"message": "Task status updated!", "completed": task.completed})

# ------------------
# INIT DB + RUN
# ------------------

# Ensure Database is Created
with app.app_context():
    if not os.path.exists("tasks.db"):
        db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
