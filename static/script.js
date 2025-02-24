document.addEventListener("DOMContentLoaded", function () {
    // Fetch tasks from the server
    fetch("/api/tasks")  // Adjust API endpoint as needed
        .then(response => response.json())
        .then(data => {
            const taskList = document.getElementById("task-list");
            taskList.innerHTML = ""; // Clear existing tasks
            
            data.forEach(task => {
                let row = document.createElement("tr");
                row.dataset.id = task.id;

                row.innerHTML = `
                    <td class="task-text ${task.completed ? "completed" : ""}">${task.task}</td>
                    <td>${task.due_date}</td>
                    <td>
                        <span class="badge ${task.priority === "High" ? "priority-high" : task.priority === "Medium" ? "priority-medium" : "priority-low"}">
                            ${task.priority}
                        </span>
                    </td>
                    <td><input type="checkbox" class="mark-done" ${task.completed ? "checked" : ""}></td>
                    <td>
                        <button class="btn btn-warning btn-sm edit-task">✏️ Edit</button>
                        <button class="btn btn-danger btn-sm remove-task">❌ Remove</button>
                    </td>
                `;

                taskList.appendChild(row);
            });
        })
        .catch(error => console.error("Error loading tasks:", error));
});
