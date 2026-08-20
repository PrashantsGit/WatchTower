const API_BASE_URL = "http://127.0.0.1:8000/api";

const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "../index.html";
}


async function loadDashboard() {

    try {
        const response = await fetch(`${API_BASE_URL}/tasks`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });

        if (response.status === 401) {
            localStorage.removeItem("access_token");
            window.location.href = "../index.html";
            return;
        }

        if (!response.ok) {
            throw new Error("Failed to load monitoring tasks.");
        }

        const tasks = await response.json();

        renderStatistics(tasks);
        renderTasks(tasks);

        loadCurrentUser();

    } catch (error) {
        console.error("Dashboard error:", error);

        document.getElementById("tasks-container").innerHTML = `
            <div class="error-message-dashboard">
                Unable to load monitoring tasks.
            </div>
        `;
    }
}


function renderStatistics(tasks) {

    const totalTasks = tasks.length;

    const activeTasks = tasks.filter(
        task => task.is_active
    ).length;

    const pausedTasks = totalTasks - activeTasks;

    document.getElementById("total-tasks").textContent = totalTasks;
    document.getElementById("active-tasks").textContent = activeTasks;
    document.getElementById("paused-tasks").textContent = pausedTasks;
}


function renderTasks(tasks) {

    const container = document.getElementById("tasks-container");

    if (tasks.length === 0) {
        container.innerHTML = `
            <div class="empty-message">
                No monitoring tasks yet.
                Create your first task to get started.
            </div>
        `;

        return;
    }

    container.innerHTML = tasks.map(task => {

        const statusClass = task.is_active ? "" : "paused";
        const statusText = task.is_active ? "Active" : "Paused";

        return `
            <article class="task-card">

                <div class="task-card-header">

                    <div>
                        <div class="task-name">
                            ${escapeHtml(task.name)}
                        </div>

                        <div class="task-url">
                            ${escapeHtml(task.target_url)}
                        </div>
                    </div>

                    <div class="task-status ${statusClass}">
                        <span class="status-dot"></span>
                        ${statusText}
                    </div>

                </div>

                <div class="task-details">

                    <span>
                        Check every ${task.check_interval} minute(s)
                    </span>

                    <span>
                        ${formatLastChecked(task.last_checked_at)}
                    </span>

                </div>

                <div class="task-actions">

                    <button
                        class="view-task-button"
                        onclick="openTask(${task.id})"
                    >
                        View Details
                    </button>

                </div>

            </article>
        `;

    }).join("");
}


function formatLastChecked(value) {

    if (!value) {
        return "Not checked yet";
    }

    const date = new Date(value);

    return `Last checked: ${date.toLocaleString()}`;
}


function escapeHtml(value) {

    const div = document.createElement("div");
    div.textContent = value;

    return div.innerHTML;
}


function openTask(taskId) {

    window.location.href = `task.html?id=${taskId}`;
}


async function loadCurrentUser() {

    try {

        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            return;
        }

        const user = await response.json();

        document.getElementById("user-name").textContent =
            user.full_name;

    } catch (error) {

        console.error("Unable to load user profile:", error);

    }
}


document
    .getElementById("logout-button")
    .addEventListener("click", () => {

        localStorage.removeItem("access_token");

        window.location.href = "../index.html";
    });


document
    .getElementById("add-task-button")
    .addEventListener("click", () => {

        window.location.href = "create-task.html";
    });


loadDashboard();
