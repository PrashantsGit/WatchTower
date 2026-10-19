
/* ============================================================
   WATCHTOWER — ALL TASKS
   ============================================================ */

const API_BASE_URL = "http://127.0.0.1:8000/api";
const ACCESS_TOKEN_KEY = "access_token";
const token = localStorage.getItem(ACCESS_TOKEN_KEY);

let allTasks = [];

if (!token) {
    window.location.href = "login.html";
}

async function initializeTasksPage() {
    if (window.watchTowerComponentsReady) {
        await window.watchTowerComponentsReady;
    }

    setupTasksActions();
    await loadTasks();
}

function setupTasksActions() {
    document.getElementById("add-task-button")
        ?.addEventListener("click", () => {
            window.location.href = "create-task.html";
        });

    document.getElementById("task-search")
        ?.addEventListener("input", renderTasks);

    document.getElementById("task-filter")
        ?.addEventListener("change", renderTasks);

    document.getElementById("logout-button")
        ?.addEventListener("click", () => {
            localStorage.removeItem(ACCESS_TOKEN_KEY);
            window.location.href = "login.html";
        });
}

async function loadTasks() {
    const container = document.getElementById("tasks-container");

    try {
        const response = await fetch(`${API_BASE_URL}/tasks`, {
            headers: {
                Authorization: `Bearer ${token}`,
                Accept: "application/json"
            }
        });

        if (response.status === 401) {
            localStorage.removeItem(ACCESS_TOKEN_KEY);
            window.location.href = "login.html";
            return;
        }

        if (!response.ok) {
            throw new Error("Unable to load monitoring tasks.");
        }

        const data = await response.json();

        if (!Array.isArray(data)) {
            throw new Error("Unexpected response from the tasks API.");
        }

        allTasks = data;
        renderTasks();

        await loadCurrentUser();
    } catch (error) {
        console.error("WatchTower tasks page error:", error);

        container.innerHTML = `
            <div class="error-message">
                Unable to load monitoring tasks.
                Please refresh the page and try again.
            </div>
        `;

        document.getElementById("task-count").textContent = "Unavailable";
    }
}

function renderTasks() {
    const container = document.getElementById("tasks-container");
    const search = document.getElementById("task-search")
        .value.trim().toLowerCase();
    const filter = document.getElementById("task-filter").value;

    const filteredTasks = allTasks.filter(task => {
        const matchesSearch =
            String(task.name || "").toLowerCase().includes(search) ||
            String(task.target_url || "").toLowerCase().includes(search);

        const matchesStatus =
            filter === "all" ||
            (filter === "active" && task.is_active) ||
            (filter === "paused" && !task.is_active);

        return matchesSearch && matchesStatus;
    });

    document.getElementById("task-count").textContent =
        `${filteredTasks.length} of ${allTasks.length} task${allTasks.length === 1 ? "" : "s"}`;

    if (filteredTasks.length === 0) {
        const noTasks = allTasks.length === 0;

        container.innerHTML = `
            <div class="empty-message">
                ${noTasks
                    ? "No monitoring tasks yet. Create your first monitor to get started."
                    : "No tasks match your search or selected status."}
            </div>
        `;
        return;
    }

    container.innerHTML = filteredTasks.map(task => {
        const active = Boolean(task.is_active);
        const status = active ? "Active" : "Paused";
        const statusClass = active ? "" : "paused";

        return `
            <article class="task-card">
                <div class="task-card-header">
                    <div class="task-card-main">
                        <div class="task-name">
                            ${escapeHtml(task.name || "Untitled monitor")}
                        </div>

                        <a
                            class="task-url"
                            href="${escapeHtml(task.target_url || "#")}"
                            target="_blank"
                            rel="noopener noreferrer"
                            title="${escapeHtml(task.target_url || "")}"
                        >${escapeHtml(task.target_url || "No target URL")}</a>
                    </div>

                    <span class="task-status ${statusClass}">
                        <span class="status-dot"></span>
                        ${status}
                    </span>
                </div>

                <div class="task-details">
                    <span>Check every ${escapeHtml(String(task.check_interval))} minute(s)</span>
                    <span>${escapeHtml(formatLastChecked(task.last_checked_at))}</span>
                </div>

                <div class="task-actions">
                    <button
                        type="button"
                        class="view-task-button"
                        data-task-id="${Number(task.id)}"
                    >View Details</button>
                </div>
            </article>
        `;
    }).join("");

    container.querySelectorAll(".view-task-button").forEach(button => {
        button.addEventListener("click", () => {
            window.location.href =
                `task.html?id=${encodeURIComponent(button.dataset.taskId)}`;
        });
    });
}

function formatLastChecked(value) {
    if (!value) {
        return "Not checked yet";
    }

    const date = new Date(value);

    return Number.isNaN(date.getTime())
        ? "Last check unavailable"
        : `Last checked: ${date.toLocaleString()}`;
}

function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = String(value ?? "");
    return element.innerHTML;
}

async function loadCurrentUser() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            localStorage.removeItem(ACCESS_TOKEN_KEY);
            window.location.href = "login.html";
            return;
        }

        if (!response.ok) return;

        const user = await response.json();
        const userName = document.getElementById("user-name");

        if (userName) {
            userName.textContent = user.full_name || "User";
        }
    } catch (error) {
        console.error("Unable to load user profile:", error);
    }
}

initializeTasksPage();
