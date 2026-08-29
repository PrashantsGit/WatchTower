/*
 * WatchTower
 * Task Details Page
 *
 * Responsible for:
 * - Loading task information
 * - Loading monitoring rules
 * - Rendering task state
 * - Navigating to create-rule
 *
 * Page structure and shared components are handled separately.
 */


/* ============================================================
   CONFIGURATION
   ============================================================ */

const API_BASE_URL = "http://127.0.0.1:8000/api";

const token = localStorage.getItem("access_token");

const params = new URLSearchParams(window.location.search);

const taskId = params.get("id");


/* ============================================================
   AUTHENTICATION / ROUTING GUARDS
   ============================================================ */

if (!token) {

    window.location.href = "../index.html";

}


if (!taskId) {

    window.location.href = "dashboard.html";

}


/* ============================================================
   NAVIGATION
   ============================================================ */

function goBack() {

    window.location.href = "dashboard.html";

}


function showCreateRule() {

    window.location.href =
        `create-rule.html?task_id=${encodeURIComponent(taskId)}`;

}


/* ============================================================
   LOAD TASK
   ============================================================ */

async function loadTask() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/tasks/${taskId}`,
            {
                method: "GET",

                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Accept": "application/json"
                }
            }
        );


        /* ----------------------------------------------------
           SESSION EXPIRED
           ---------------------------------------------------- */

        if (response.status === 401) {

            localStorage.removeItem("access_token");

            window.location.href = "../index.html";

            return;

        }


        /* ----------------------------------------------------
           TASK NOT FOUND
           ---------------------------------------------------- */

        if (response.status === 404) {

            alert("Monitoring task not found.");

            window.location.href = "dashboard.html";

            return;

        }


        /* ----------------------------------------------------
           OTHER API ERROR
           ---------------------------------------------------- */

        if (!response.ok) {

            throw new Error(
                `Failed to load monitoring task (${response.status})`
            );

        }


        const task = await response.json();

        renderTask(task);

    }

    catch (error) {

        console.error(
            "WatchTower: Task loading error:",
            error
        );


        const taskName =
            document.getElementById("task-name");


        if (taskName) {

            taskName.textContent =
                "Unable to load task.";

        }

    }

}


/* ============================================================
   RENDER TASK
   ============================================================ */

function renderTask(task) {

    const taskName =
        document.getElementById("task-name");

    const taskUrl =
        document.getElementById("task-url");

    const taskStatus =
        document.getElementById("task-status");

    const taskInterval =
        document.getElementById("task-interval");

    const taskLastChecked =
        document.getElementById("task-last-checked");

    const taskNextCheck =
        document.getElementById("task-next-check");


    if (taskName) {

        taskName.textContent =
            task.name || "Unnamed Task";

    }


    if (taskUrl) {

        taskUrl.textContent =
            task.target_url || "-";

    }


    if (taskStatus) {

        taskStatus.textContent =
            task.is_active
                ? "Active"
                : "Paused";


        taskStatus.classList.toggle(
            "status-active",
            Boolean(task.is_active)
        );

        taskStatus.classList.toggle(
            "status-paused",
            !task.is_active
        );

    }


    if (taskInterval) {

        taskInterval.textContent =
            formatInterval(task.check_interval);

    }


    if (taskLastChecked) {

        taskLastChecked.textContent =
            task.last_checked_at
                ? formatDate(task.last_checked_at)
                : "Never";

    }


    if (taskNextCheck) {

        taskNextCheck.textContent =
            task.next_execution_at
                ? formatDate(task.next_execution_at)
                : "-";

    }

}


/* ============================================================
   FORMAT INTERVAL
   ============================================================ */

function formatInterval(minutes) {

    if (
        minutes === null ||
        minutes === undefined ||
        Number.isNaN(Number(minutes))
    ) {

        return "-";

    }


    minutes = Number(minutes);


    if (minutes < 60) {

        return `${minutes} minute${minutes === 1 ? "" : "s"}`;

    }


    if (minutes % 60 === 0) {

        const hours =
            minutes / 60;


        return `${hours} hour${hours === 1 ? "" : "s"}`;

    }


    return `${minutes} minutes`;

}


/* ============================================================
   FORMAT DATE
   ============================================================ */

function formatDate(value) {

    const date =
        new Date(value);


    if (Number.isNaN(date.getTime())) {

        return "-";

    }


    return date.toLocaleString();

}


/* ============================================================
   LOAD MONITORING RULES
   ============================================================ */

async function loadRules() {

    const container =
        document.getElementById("rules-container");


    if (!container) {

        return;

    }


    try {

        const response = await fetch(
            `${API_BASE_URL}/tasks/${taskId}/rules`,
            {
                method: "GET",

                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Accept": "application/json"
                }
            }
        );


        /* ----------------------------------------------------
           SESSION EXPIRED
           ---------------------------------------------------- */

        if (response.status === 401) {

            localStorage.removeItem("access_token");

            window.location.href = "../index.html";

            return;

        }


        /* ----------------------------------------------------
           TASK NOT FOUND
           ---------------------------------------------------- */

        if (response.status === 404) {

            container.innerHTML = `
                <div class="empty-state">
                    Monitoring task not found.
                </div>
            `;

            return;

        }


        /* ----------------------------------------------------
           OTHER API ERROR
           ---------------------------------------------------- */

        if (!response.ok) {

            throw new Error(
                `Failed to load monitoring rules (${response.status})`
            );

        }


        const rules =
            await response.json();


        renderRules(rules);

    }

    catch (error) {

        console.error(
            "WatchTower: Rule loading error:",
            error
        );


        container.innerHTML = `
            <div class="empty-state">
                Unable to load monitoring rules.
            </div>
        `;

    }

}


/* ============================================================
   RENDER RULES
   ============================================================ */

function renderRules(rules) {

    const container =
        document.getElementById("rules-container");


    if (!container) {

        return;

    }


    if (
        !Array.isArray(rules) ||
        rules.length === 0
    ) {

        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-title">
                    No monitoring rules configured
                </div>

                <div class="empty-state-description">
                    Add your first rule to start monitoring.
                </div>
            </div>
        `;

        return;

    }


    container.innerHTML =
        rules.map(rule => {

            const statusText =
                rule.is_enabled
                    ? "Enabled"
                    : "Disabled";


            return `
                <article class="rule-card">

                    <div class="rule-card-header">

                        <div class="rule-card-main">

                            <div class="rule-type">
                                ${escapeHtml(
                                    rule.rule_type || "Rule"
                                )}
                            </div>

                            <div class="rule-condition">
                                ${escapeHtml(
                                    rule.operator || ""
                                )}
                                ${escapeHtml(
                                    rule.target_value || ""
                                )}
                            </div>

                        </div>

                        <div
                            class="
                                rule-status
                                ${rule.is_enabled
                                    ? "rule-status-enabled"
                                    : "rule-status-disabled"}
                            "
                        >
                            ${statusText}
                        </div>

                    </div>

                </article>
            `;

        }).join("");

}


/* ============================================================
   HTML ESCAPING
   ============================================================ */

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    const div =
        document.createElement("div");


    div.textContent =
        String(value);


    return div.innerHTML;

}


/* ============================================================
   EVENT WIRING
   ============================================================ */

function initializeTaskPage() {

    const backButton =
        document.getElementById(
            "back-dashboard-button"
        );


    const addRuleButton =
        document.getElementById(
            "add-rule-button"
        );


    if (backButton) {

        backButton.addEventListener(
            "click",
            goBack
        );

    }


    if (addRuleButton) {

        addRuleButton.addEventListener(
            "click",
            showCreateRule
        );

    }


    loadTask();

    loadRules();

}


/* ============================================================
   INITIALIZATION
   ============================================================ */

if (document.readyState === "loading") {

    document.addEventListener(
        "DOMContentLoaded",
        initializeTaskPage
    );

} else {

    initializeTaskPage();

}