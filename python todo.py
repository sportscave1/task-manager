import sqlite3
from datetime import datetime

# Database Setup
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
                priority TEXT NOT NULL,
                category TEXT NOT NULL,
                completed INTEGER DEFAULT 0
            )
        """)
        conn.commit()

def show_menu():
    print("\n📌 TO-DO LIST 📌")
    print("1. View tasks (Sorted by Due Date, Priority & Status)")
    print("2. Add task")
    print("3. Mark task as completed")
    print("4. Remove task")
    print("5. Exit")

def get_tasks():
    """Retrieve tasks from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY completed, due_date, priority")
        return cursor.fetchall()

def view_tasks():
    tasks = get_tasks()
    if not tasks:
        print("\n✅ No tasks found! Add some tasks.")
        return

    print("\n📝 Your Tasks (Sorted by Due Date, Priority & Status):")
    for i, task in enumerate(tasks, 1):
        status = "✅ Done" if task[5] else "⏳ Pending"
        print(f"{i}. {task[1]} (Due: {task[2]}, Priority: {task[3]}, Category: {task[4]}, Status: {status})")

def add_task():
    task_name = input("\nEnter new task: ")
    due_date = input("Enter due date (YYYY-MM-DD): ")
    priority = input("Set priority (High, Medium, Low): ").capitalize()
    category = input("Set category (Meeting, Order, Follow-up, Urgent, etc.): ").capitalize()

    if priority not in ["High", "Medium", "Low"]:
        print("⚠️ Invalid priority! Defaulting to Medium.")
        priority = "Medium"

    try:
        datetime.strptime(due_date, "%Y-%m-%d")  # Validate date format
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (task, due_date, priority, category) VALUES (?, ?, ?, ?)", 
                           (task_name, due_date, priority, category))
            conn.commit()
        print("✅ Task added!")
    except ValueError:
        print("⚠️ Invalid date format! Use YYYY-MM-DD.")

def mark_task_completed():
    view_tasks()
    try:
        task_num = int(input("\nEnter task number to mark as completed: ")) - 1
        tasks = get_tasks()
        if 0 <= task_num < len(tasks):
            task_id = tasks[task_num][0]
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
                conn.commit()
            print(f"✅ Task '{tasks[task_num][1]}' marked as completed.")
        else:
            print("⚠️ Invalid task number.")
    except ValueError:
        print("⚠️ Please enter a valid number.")

def remove_task():
    view_tasks()
    try:
        task_num = int(input("\nEnter task number to remove: ")) - 1
        tasks = get_tasks()
        if 0 <= task_num < len(tasks):
            task_id = tasks[task_num][0]
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
            print(f"❌ Task '{tasks[task_num][1]}' removed.")
        else:
            print("⚠️ Invalid task number.")
    except ValueError:
        print("⚠️ Please enter a valid number.")

# Initialize database
initialize_db()

# Main Loop
while True:
    show_menu()
    choice = input("\nChoose an option (1-5): ")

    if choice == "1":
        view_tasks()
    elif choice == "2":
        add_task()
    elif choice == "3":
        mark_task_completed()
    elif choice == "4":
        remove_task()
    elif choice == "5":
        print("\n👋 Goodbye! See you next time.")
        break
    else:
        print("⚠️ Invalid choice! Enter a number between 1-5.")
