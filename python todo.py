import sqlite3
import os
import sys
from datetime import datetime

# Database File
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

def show_menu():
    print("\n📌 TO-DO LIST 📌")
    print("1. View tasks (Sorted by Due Date, Priority & Status)")
    print("2. Add task")
    print("3. Mark task as completed")
    print("4. Remove task")
    print("5. Exit")

def get_tasks():
    """Retrieve tasks from the database, sorted by completion, priority, and due date."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM tasks
            ORDER BY completed,
                     CASE priority 
                        WHEN 'High' THEN 1
                        WHEN 'Medium' THEN 2
                        ELSE 3 END,
                     due_date
        """)
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
    try:
        task_name = input("\nEnter new task: ") or "Unnamed Task"
        due_date = input("Enter due date (YYYY-MM-DD): ")
        priority = input("Set priority (High, Medium, Low): ").capitalize()
        category = input("Set category (Meeting, Order, Follow-up, Urgent, etc.): ").capitalize()

        # Validate priority
        if priority not in ["High", "Medium", "Low"]:
            print("⚠️ Invalid priority! Defaulting to Medium.")
            priority = "Medium"

        # Validate date format
        datetime.strptime(due_date, "%Y-%m-%d")

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (task, due_date, priority, category) VALUES (?, ?, ?, ?)", 
                           (task_name, due_date, priority, category))
            conn.commit()
        print("✅ Task added!")
    except ValueError as e:
        print(f"⚠️ Invalid input: {e}")

def mark_task_completed():
    view_tasks()
    try:
        task_num = input("\nEnter task number to mark as completed: ")
        if not task_num.isdigit():
            raise ValueError("Invalid input. Enter a number.")

        task_num = int(task_num) - 1
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
    except ValueError as e:
        print(f"⚠️ {e}")

def remove_task():
    view_tasks()
    try:
        task_num = input("\nEnter task number to remove: ")
        if not task_num.isdigit():
            raise ValueError("Invalid input. Enter a number.")

        task_num = int(task_num) - 1
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
    except ValueError as e:
        print(f"⚠️ {e}")

def main():
    # Initialize the database
    initialize_db()

    # Non-interactive mode fix for Render (if running in an environment without a terminal)
    if not sys.stdin.isatty():
        print("\n🚀 Running in non-interactive mode! Exiting.")
        return

    # Main Loop
    while True:
        show_menu()
        choice = input("\nChoose an option (1-5): ").strip()

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

# Run main function
if __name__ == "__main__":
    main()
