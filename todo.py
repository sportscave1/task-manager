# Simple To-Do List App
tasks = []  # Empty list to store tasks

def show_menu():
    print("\n📌 TO-DO LIST 📌")
    print("1. View tasks")
    print("2. Add task")
    print("3. Remove task")
    print("4. Save tasks to file")
    print("5. Load tasks from file")
    print("6. Exit")

def view_tasks():
    if not tasks:
        print("\n✅ No tasks found! Add some tasks.")
    else:
        print("\n📝 Your Tasks:")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task}")

def add_task():
    task = input("\nEnter new task: ")
    tasks.append(task)
    print("✅ Task added!")

def remove_task():
    view_tasks()
    try:
        task_num = int(input("\nEnter task number to remove: "))
        if 1 <= task_num <= len(tasks):
            removed = tasks.pop(task_num - 1)
            print(f"❌ Task '{removed}' removed.")
        else:
            print("⚠️ Invalid task number.")
    except ValueError:
        print("⚠️ Please enter a number.")

def save_tasks():
    with open("tasks.txt", "w") as file:
        for task in tasks:
            file.write(task + "\n")
    print("💾 Tasks saved to 'tasks.txt'!")

def load_tasks():
    try:
        with open("tasks.txt", "r") as file:
            global tasks
            tasks = [line.strip() for line in file.readlines()]
        print("📂 Tasks loaded from 'tasks.txt'!")
    except FileNotFoundError:
        print("⚠️ No saved tasks found.")

# Main Loop
while True:
    show_menu()
    choice = input("\nChoose an option (1-6): ")

    if choice == "1":
        view_tasks()
    elif choice == "2":
        add_task()
    elif choice == "3":
        remove_task()
    elif choice == "4":
        save_tasks()
    elif choice == "5":
        load_tasks()
    elif choice == "6":
        print("\n👋 Goodbye! See you next time.")
        break
    else:
        print("⚠️ Invalid choice! Enter a number between 1-6.")
