/* ============================================================
   WATCHTOWER — DASHBOARD
   ============================================================ */


/* ============================================================
   CONFIGURATION
   ============================================================ */

const API_BASE_URL =
    "http://127.0.0.1:8000/api";

const ACCESS_TOKEN_KEY =
    "access_token";


/* ============================================================
   SESSION
   ============================================================ */

const token =
    localStorage.getItem(ACCESS_TOKEN_KEY);


if (!token) {

    window.location.href =
        "login.html";

}


/* ============================================================
   DASHBOARD INITIALIZATION
   ============================================================ */

async function initializeDashboard() {

    /*
     * Wait until the shared WatchTower shell has finished
     * loading before accessing header/sidebar elements.
     */

    if (window.watchTowerComponentsReady) {

        await window.watchTowerComponentsReady;

    }


    setupDashboardActions();

    await Promise.all([
        loadDashboard(),
        loadRecentActivity()
    ]);

}


/* ============================================================
   DASHBOARD DATA
   ============================================================ */

async function loadDashboard() {

    const container =
        document.getElementById("tasks-container");


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/tasks`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        /* -----------------------------------------------
           Session expired / invalid
           ----------------------------------------------- */

        if (response.status === 401) {

            localStorage.removeItem(
                ACCESS_TOKEN_KEY
            );

            window.location.href =
                "login.html";

            return;
        }


        /* -----------------------------------------------
           Other API failure
           ----------------------------------------------- */

        if (!response.ok) {

            throw new Error(
                "Failed to load monitoring tasks."
            );

        }


        const tasks =
            await response.json();


        /* -----------------------------------------------
           Render dashboard
           ----------------------------------------------- */

        renderStatistics(tasks);

        renderTasks(tasks);


        /* -----------------------------------------------
           User information
           ----------------------------------------------- */

        await loadCurrentUser();


    } catch (error) {

        console.error(
            "WatchTower dashboard error:",
            error
        );


        if (container) {

            container.innerHTML = `
                <div class="error-message-dashboard">
                    Unable to load monitoring tasks.
                </div>
            `;

        }

    }

}


/* ============================================================
   STATISTICS
   ============================================================ */

function renderStatistics(tasks) {

    const totalTasks =
        tasks.length;


    const activeTasks =
        tasks.filter(
            task => task.is_active
        ).length;


    const pausedTasks =
        totalTasks - activeTasks;


    const totalElement =
        document.getElementById(
            "total-tasks"
        );


    const activeElement =
        document.getElementById(
            "active-tasks"
        );


    const pausedElement =
        document.getElementById(
            "paused-tasks"
        );


    if (totalElement) {

        totalElement.textContent =
            totalTasks;

    }


    if (activeElement) {

        activeElement.textContent =
            activeTasks;

    }


    if (pausedElement) {

        pausedElement.textContent =
            pausedTasks;

    }

}


/* ============================================================
   TASKS
   ============================================================ */

function renderTasks(tasks) {

    const container =
        document.getElementById(
            "tasks-container"
        );


    if (!container) {

        console.error(
            "WatchTower: tasks-container not found."
        );

        return;

    }


    if (tasks.length === 0) {

        container.innerHTML = `
            <div class="empty-message">
                No monitoring tasks yet.
                Create your first task to get started.
            </div>
        `;

        return;

    }


    container.innerHTML =
        tasks.map(task => {

            const statusClass =
                task.is_active
                    ? ""
                    : "paused";


            const statusText =
                task.is_active
                    ? "Active"
                    : "Paused";


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


                        <div
                            class="task-status ${statusClass}"
                        >

                            <span
                                class="status-dot"
                            ></span>

                            ${statusText}

                        </div>

                    </div>


                    <div class="task-details">

                        <span>
                            Check every
                            ${escapeHtml(
                                String(
                                    task.check_interval
                                )
                            )}
                            minute(s)
                        </span>


                        <span>
                            ${formatLastChecked(
                                task.last_checked_at
                            )}
                        </span>

                    </div>


                    <div class="task-actions">

                        <button
                            type="button"
                            class="view-task-button"
                            data-task-id="${task.id}"
                        >
                            View Details
                        </button>

                    </div>

                </article>
            `;

        }).join("");


    /*
     * Attach actions after the cards exist.
     */

    container
        .querySelectorAll(
            ".view-task-button"
        )
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    const taskId =
                        button.dataset.taskId;

                    openTask(taskId);

                }
            );

        });

}

/* ============================================================
   RECENT ACTIVITY
   ============================================================ */

async function loadRecentActivity() {

    const container = document.getElementById(
        "recent-activity-container"
    );

    if (!container) {
        console.error(
            "WatchTower: recent-activity-container not found."
        );
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/history?limit=5`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (response.status === 401) {
            localStorage.removeItem(ACCESS_TOKEN_KEY);
            window.location.href = "login.html";
            return;
        }

        if (!response.ok) {
            throw new Error("Failed to load recent activity.");
        }

        const events = await response.json();

        renderRecentActivity(events, container);

    } catch (error) {
        console.error(
            "WatchTower recent activity error:",
            error
        );

        container.innerHTML = `
            <div class="activity-empty">
                <div class="activity-empty-title">
                    Unable to load recent activity
                </div>
                <div class="activity-empty-description">
                    Please refresh the page and try again.
                </div>
            </div>
        `;
    }
}


/* ============================================================
   RENDER RECENT ACTIVITY
   ============================================================ */

function renderRecentActivity(events, container) {

    if (!Array.isArray(events) || events.length === 0) {
        container.innerHTML = `
            <div class="activity-empty">
                <div
                    class="activity-placeholder-icon"
                    aria-hidden="true"
                >◌</div>

                <div>
                    <div class="activity-empty-title">
                        No recent activity
                    </div>

                    <div class="activity-empty-description">
                        Monitoring events will appear here.
                    </div>
                </div>
            </div>
        `;
        return;
    }

    container.innerHTML = events.map(event => {

        const eventType = String(
            event.event_type || "MONITORING_EVENT"
        );

        const eventTitle = eventType
            .replace(/_/g, " ")
            .toLowerCase()
            .replace(/\b\w/g, character => character.toUpperCase());

        const message = event.event_message
            ? escapeHtml(event.event_message)
            : (
                event.previous_value != null ||
                event.current_value != null
            )
                ? `${escapeHtml(event.previous_value ?? "—")} → ${escapeHtml(event.current_value ?? "—")}`
                : "A monitoring event was detected.";

        const detectedAt = event.detected_at
            ? new Date(event.detected_at)
            : null;

        const formattedDate =
            detectedAt && !Number.isNaN(detectedAt.getTime())
                ? detectedAt.toLocaleString()
                : "Time unavailable";

        return `
            <article class="activity-item">
                <div class="activity-item-content">
                    <div class="activity-item-title">
                        ${escapeHtml(eventTitle)}
                    </div>

                    <div class="activity-item-description">
                        ${message}
                    </div>

                    <div class="activity-item-meta">
                        Task #${escapeHtml(String(event.task_id))}
                        <span aria-hidden="true">·</span>
                        ${escapeHtml(formattedDate)}
                    </div>
                </div>
            </article>
        `;

    }).join("");
}

/* ============================================================
   LAST CHECKED
   ============================================================ */

function formatLastChecked(value) {

    if (!value) {

        return "Not checked yet";

    }


    const date =
        new Date(value);


    return `Last checked: ${date.toLocaleString()}`;

}


/* ============================================================
   HTML ESCAPING
   ============================================================ */

function escapeHtml(value) {

    const div =
        document.createElement("div");


    div.textContent =
        value;


    return div.innerHTML;

}


/* ============================================================
   TASK NAVIGATION
   ============================================================ */

function openTask(taskId) {

    window.location.href =
        `task.html?id=${taskId}`;

}


/* ============================================================
   CURRENT USER
   ============================================================ */

async function loadCurrentUser() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/auth/me`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        if (!response.ok) {

            return;

        }


        const user =
            await response.json();


        const userName =
            document.getElementById(
                "user-name"
            );


        if (userName) {

            userName.textContent =
                user.full_name;

        }


    } catch (error) {

        console.error(
            "Unable to load user profile:",
            error
        );

    }

}


/* ============================================================
   DASHBOARD ACTIONS
   ============================================================ */

function setupDashboardActions() {

    /* -----------------------------------------------
       Logout
       ----------------------------------------------- */

    const logoutButton =
        document.getElementById(
            "logout-button"
        );


    if (logoutButton) {

        logoutButton.addEventListener(
            "click",
            () => {

                localStorage.removeItem(
                    ACCESS_TOKEN_KEY
                );


                window.location.href =
                    "login.html";

            }
        );

    }


    /* -----------------------------------------------
       Add monitor
       ----------------------------------------------- */

    const addTaskButton =
        document.getElementById(
            "add-task-button"
        );


    if (addTaskButton) {

        addTaskButton.addEventListener(
            "click",
            () => {

                window.location.href =
                    "create-task.html";

            }
        );

    }

}


/* ============================================================
   START
   ============================================================ */

initializeDashboard();