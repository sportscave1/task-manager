document.addEventListener("DOMContentLoaded", function () {
    function fetchTasks() {
        fetch("/tasks")  // Corrected API endpoint
            .then(response => response.json())
            .then(data => {
                const taskList = document.getElementById("task-list");
                taskList.innerHTML = ""; // Clear existing tasks
                
                data.forEach(task => {
                    let row = document.createElement("tr");
                    row.dataset.id = task.id;

                    row.innerHTML = `
                        <td class="task-text ${task.completed ? "completed" : ""}">${task.task}</td>
                        <td>${task.due_date || "No due date"}</td>
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

                    // Attach event listeners
                    row.querySelector(".mark-done").addEventListener("change", () => toggleTaskCompletion(task.id));
                    row.querySelector(".remove-task").addEventListener("click", () => removeTask(task.id));
                });
            })
            .catch(error => console.error("Error loading tasks:", error));
    }

    function toggleTaskCompletion(taskId) {
        fetch(`/complete/${taskId}`, { method: "POST" })
            .then(response => response.json())
            .then(() => fetchTasks());  // Reload tasks after update
    }

    function removeTask(taskId) {
        fetch(`/remove/${taskId}`, { method: "POST" })
            .then(response => response.json())
            .then(() => fetchTasks());  // Reload tasks after deletion
    }

    fetchTasks(); // Load tasks when page loads
});
