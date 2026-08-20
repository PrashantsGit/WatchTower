const API_BASE_URL = "http://127.0.0.1:8000/api";

const token = localStorage.getItem("access_token");

const params = new URLSearchParams(window.location.search);
const taskId = params.get("id");


if (!token) {
    window.location.href = "../index.html";
}


if (!taskId) {
    window.location.href = "dashboard.html";
}


function goBack() {
    window.location.href = "dashboard.html";
}


async function loadTask() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/tasks/${taskId}`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
            }
        );


        if (response.status === 401) {
            localStorage.removeItem("access_token");
            window.location.href = "../index.html";
            return;
        }


        if (response.status === 404) {
            alert("Monitoring task not found.");
            window.location.href = "dashboard.html";
            return;
        }


        if (!response.ok) {
            throw new Error("Failed to load monitoring task.");
        }


        const task = await response.json();

        renderTask(task);

    } catch (error) {

        console.error("Task loading error:", error);

        document.getElementById("task-name").textContent =
            "Unable to load task.";

    }
}


function renderTask(task) {

    document.getElementById("task-name").textContent =
        task.name;

    document.getElementById("task-url").textContent =
        task.target_url;

    document.getElementById("task-status").textContent =
        task.is_active ? "Active" : "Paused";

    document.getElementById("task-interval").textContent =
        formatInterval(task.check_interval);

    document.getElementById("task-last-checked").textContent =
        task.last_checked_at
            ? formatDate(task.last_checked_at)
            : "Never";

    document.getElementById("task-next-check").textContent =
        task.next_execution_at
            ? formatDate(task.next_execution_at)
            : "-";
}


function formatInterval(minutes) {

    if (minutes < 60) {
        return `${minutes} minutes`;
    }

    if (minutes % 60 === 0) {

        const hours = minutes / 60;

        if (hours === 1) {
            return "1 hour";
        }

        return `${hours} hours`;
    }

    return `${minutes} minutes`;
}


function formatDate(value) {

    const date = new Date(value);

    return date.toLocaleString();
}


async function loadRules() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/tasks/${taskId}/rules`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
            }
        );


        if (response.status === 401) {
            localStorage.removeItem("access_token");
            window.location.href = "../index.html";
            return;
        }


        if (response.status === 404) {
            document.getElementById("rules-container").innerHTML = `
                <div class="empty-state">
                    Monitoring task not found.
                </div>
            `;

            return;
        }


        if (!response.ok) {
            throw new Error("Failed to load monitoring rules.");
        }


        const rules = await response.json();

        renderRules(rules);

    } catch (error) {

        console.error("Rule loading error:", error);

        document.getElementById("rules-container").innerHTML = `
            <div class="empty-state">
                Unable to load monitoring rules.
            </div>
        `;

    }
}


function renderRules(rules) {

    const container =
        document.getElementById("rules-container");


    if (rules.length === 0) {

        container.innerHTML = `
            <div class="empty-state">
                No monitoring rules configured yet.
                Add your first rule to start monitoring.
            </div>
        `;

        return;
    }


    container.innerHTML = rules.map(rule => {

        const statusText =
            rule.is_enabled ? "Enabled" : "Disabled";


        return `
            <article class="rule-card">

                <div class="rule-card-header">

                    <div>

                        <div class="rule-type">
                            ${escapeHtml(rule.rule_type)}
                        </div>

                        <div class="rule-condition">
                            ${escapeHtml(rule.operator)}
                            ${escapeHtml(rule.target_value)}
                        </div>

                    </div>

                    <div class="rule-status">
                        ${statusText}
                    </div>

                </div>

            </article>
        `;

    }).join("");
}


function escapeHtml(value) {

    const div = document.createElement("div");

    div.textContent = value;

    return div.innerHTML;
}


function showCreateRule() {

    window.location.href = `create-rule.html?task_id=${taskId}`;

}


loadTask();
loadRules();