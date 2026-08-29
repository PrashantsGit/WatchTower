/*
 * WatchTower
 * Task Details Page
 *
 * Responsible for:
 * - Loading task information
 * - Loading monitoring rules
 * - Rendering task state
 * - Creating, editing, enabling/disabling and deleting rules
 * - Navigating between task pages
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


        if (response.status === 401) {

            handleUnauthorized();

            return;

        }


        if (response.status === 404) {

            alert("Monitoring task not found.");

            window.location.href = "dashboard.html";

            return;

        }


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

        const url =
            task.target_url || "";

        taskUrl.textContent =
            url || "-";

        taskUrl.href =
            url || "#";

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

    const toggleTaskButton =
    document.getElementById(
        "toggle-task-button"
    );


if (toggleTaskButton) {

    toggleTaskButton.textContent =
        task.is_active
            ? "Pause Monitoring"
            : "Resume Monitoring";

    toggleTaskButton.classList.toggle(
        "task-resume-button",
        !task.is_active
    );

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


        if (response.status === 401) {

            handleUnauthorized();

            return;

        }


        if (response.status === 404) {

            container.innerHTML = `
                <div class="empty-state">
                    Monitoring task not found.
                </div>
            `;

            return;

        }


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
        rules.map(renderRuleCard).join("");

}


/* ============================================================
   RENDER SINGLE RULE CARD
   ============================================================ */

function renderRuleCard(rule) {

    const enabled =
        Boolean(rule.is_enabled);


    const statusText =
        enabled
            ? "Enabled"
            : "Disabled";


    const toggleText =
        enabled
            ? "Disable"
            : "Enable";


    const toggleClass =
        enabled
            ? "rule-action-secondary"
            : "rule-action-enable";


    return `
        <article
            class="rule-card ${enabled
                ? "rule-card-enabled"
                : "rule-card-disabled"}"
            data-rule-id="${rule.id}"
        >

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
                        ${enabled
                            ? "rule-status-enabled"
                            : "rule-status-disabled"}
                    "
                >

                    <span class="rule-status-dot"></span>

                    ${statusText}

                </div>

            </div>


            <div class="rule-card-actions">

                <button
                    type="button"
                    class="rule-action-button ${toggleClass}"
                    onclick="toggleRule(${rule.id}, ${enabled})"
                >
                    ${toggleText}
                </button>


                <button
                    type="button"
                    class="rule-action-button rule-action-secondary"
                    onclick="editRule(${rule.id})"
                >
                    Edit
                </button>


                <button
                    type="button"
                    class="rule-action-button rule-action-danger"
                    onclick="deleteRule(${rule.id})"
                >
                    Delete
                </button>

            </div>

        </article>
    `;

}


/* ============================================================
   ENABLE / DISABLE RULE
   ============================================================ */

async function toggleRule(ruleId, currentState) {

    const confirmedState =
        !currentState;


    const action =
        confirmedState
            ? "enable"
            : "disable";


    try {

        const rule =
            await getRule(ruleId);


        if (!rule) {

            return;

        }


        const response =
            await fetch(
                `${API_BASE_URL}/tasks/${taskId}/rules/${ruleId}`,
                {
                    method: "PUT",

                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        rule_type: rule.rule_type,
                        operator: rule.operator,
                        target_value: rule.target_value,
                        is_enabled: confirmedState
                    })
                }
            );


        if (response.status === 401) {

            handleUnauthorized();

            return;

        }


        if (!response.ok) {

            throw new Error(
                `Failed to ${action} rule (${response.status})`
            );

        }


        await loadRules();

    }

    catch (error) {

        console.error(
            `WatchTower: Failed to ${action} rule:`,
            error
        );

        alert(
            `Unable to ${action} monitoring rule.`
        );

    }

}


/* ============================================================
   EDIT RULE
   ============================================================ */

async function editRule(ruleId) {

    try {

        const rule =
            await getRule(ruleId);


        if (!rule) {

            return;

        }


        const modal =
            document.getElementById("edit-rule-modal");

        const ruleIdInput =
            document.getElementById("edit-rule-id");

        const ruleTypeInput =
            document.getElementById("edit-rule-type");

        const operatorInput =
            document.getElementById("edit-rule-operator");

        const targetInput =
            document.getElementById("edit-rule-target");

        const errorElement =
            document.getElementById("edit-rule-error");


        if (
            !modal ||
            !ruleIdInput ||
            !ruleTypeInput ||
            !operatorInput ||
            !targetInput
        ) {

            console.error(
                "WatchTower: Edit rule modal elements not found."
            );

            return;

        }


        ruleIdInput.value =
            rule.id;

        ruleTypeInput.value =
            rule.rule_type || "";

        operatorInput.value =
            rule.operator || "";

        targetInput.value =
            rule.target_value || "";


        if (errorElement) {

            errorElement.hidden = true;

            errorElement.textContent = "";

        }


        modal.hidden = false;

        document.body.classList.add(
            "modal-open"
        );


        targetInput.focus();

    }

    catch (error) {

        console.error(
            "WatchTower: Failed to open edit rule:",
            error
        );

        alert(
            "Unable to open monitoring rule."
        );

    }

}

/* ============================================================
   CLOSE EDIT MODAL
   ============================================================ */

function closeEditRuleModal() {

    const modal =
        document.getElementById("edit-rule-modal");


    if (!modal) {

        return;

    }


    modal.hidden = true;

    document.body.classList.remove(
        "modal-open"
    );


    const form =
        document.getElementById("edit-rule-form");


    if (form) {

        form.reset();

    }


    const errorElement =
        document.getElementById("edit-rule-error");


    if (errorElement) {

        errorElement.hidden = true;

        errorElement.textContent = "";

    }

}


/* ============================================================
   SAVE EDITED RULE
   ============================================================ */

async function saveEditedRule(event) {

    event.preventDefault();


    const ruleId =
        document.getElementById("edit-rule-id").value;

    const ruleType =
        document.getElementById("edit-rule-type").value.trim();

    const operator =
        document.getElementById("edit-rule-operator").value.trim();

    const targetValue =
        document.getElementById("edit-rule-target").value.trim();

    const saveButton =
        document.getElementById("save-rule-button");

    const errorElement =
        document.getElementById("edit-rule-error");


    if (
        !ruleId ||
        !ruleType ||
        !operator ||
        !targetValue
    ) {

        showEditRuleError(
            "All rule fields are required."
        );

        return;

    }


    try {

        /*
         * Get the current rule first so that we preserve
         * its enabled/disabled state.
         */

        const currentRule =
            await getRule(ruleId);


        if (!currentRule) {

            return;

        }


        if (saveButton) {

            saveButton.disabled = true;

            saveButton.textContent =
                "Saving...";

        }


        if (errorElement) {

            errorElement.hidden = true;

            errorElement.textContent = "";

        }


        const response =
            await fetch(
                `${API_BASE_URL}/tasks/${taskId}/rules/${ruleId}`,
                {
                    method: "PUT",

                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        rule_type: ruleType,
                        operator: operator,
                        target_value: targetValue,
                        is_enabled:
                            Boolean(currentRule.is_enabled)
                    })
                }
            );


        if (response.status === 401) {

            handleUnauthorized();

            return;

        }


        if (response.status === 404) {

            showEditRuleError(
                "This monitoring rule no longer exists."
            );

            await loadRules();

            return;

        }


        if (!response.ok) {

            let message =
                "Unable to update monitoring rule.";


            try {

                const errorData =
                    await response.json();


                if (errorData.detail) {

                    message =
                        typeof errorData.detail === "string"
                            ? errorData.detail
                            : "Invalid rule data.";

                }

            }

            catch (_) {

                /*
                 * Keep the generic message if the API
                 * does not return JSON.
                 */

            }


            throw new Error(message);

        }


        closeEditRuleModal();

        await loadRules();

    }

    catch (error) {

        console.error(
            "WatchTower: Failed to update rule:",
            error
        );


        showEditRuleError(
            error.message ||
            "Unable to update monitoring rule."
        );

    }

    finally {

        if (saveButton) {

            saveButton.disabled = false;

            saveButton.textContent =
                "Save Changes";

        }

    }

}


/* ============================================================
   EDIT MODAL ERROR
   ============================================================ */

function showEditRuleError(message) {

    const errorElement =
        document.getElementById("edit-rule-error");


    if (!errorElement) {

        return;

    }


    errorElement.textContent =
        message;

    errorElement.hidden = false;

}


/* ============================================================
   GET SINGLE RULE
   ============================================================ */

async function getRule(ruleId) {

    const response =
        await fetch(
            `${API_BASE_URL}/tasks/${taskId}/rules/${ruleId}`,
            {
                method: "GET",

                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Accept": "application/json"
                }
            }
        );


    if (response.status === 401) {

        handleUnauthorized();

        return null;

    }


    if (response.status === 404) {

        alert(
            "Monitoring rule not found."
        );

        await loadRules();

        return null;

    }


    if (!response.ok) {

        throw new Error(
            `Failed to load rule (${response.status})`
        );

    }


    return await response.json();

}


/* ============================================================
   DELETE RULE
   ============================================================ */

async function deleteRule(ruleId) {

    const confirmed =
        window.confirm(
            "Delete this monitoring rule?\n\nThis action cannot be undone."
        );


    if (!confirmed) {

        return;

    }


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/tasks/${taskId}/rules/${ruleId}`,
                {
                    method: "DELETE",

                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Accept": "application/json"
                    }
                }
            );


        if (response.status === 401) {

            handleUnauthorized();

            return;

        }


        if (response.status === 404) {

            alert(
                "Monitoring rule not found."
            );

            await loadRules();

            return;

        }


        if (!response.ok) {

            throw new Error(
                `Failed to delete rule (${response.status})`
            );

        }


        await loadRules();

    }

    catch (error) {

        console.error(
            "WatchTower: Failed to delete rule:",
            error
        );

        alert(
            "Unable to delete monitoring rule."
        );

    }

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
   AUTH HANDLER
   ============================================================ */

function handleUnauthorized() {

    localStorage.removeItem("access_token");

    window.location.href =
        "../index.html";

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

        const editRuleForm =
        document.getElementById("edit-rule-form");


    if (editRuleForm) {

        editRuleForm.addEventListener(
            "submit",
            saveEditedRule
        );

    }


    document
        .querySelectorAll("[data-close-edit-modal]")
        .forEach(element => {

            element.addEventListener(
                "click",
                closeEditRuleModal
            );

        });
    
        
    const toggleTaskButton =
    document.getElementById(
        "toggle-task-button"
    );


if (toggleTaskButton) {

    toggleTaskButton.addEventListener(
        "click",
        toggleTaskStatus
    );

}

const editTaskButton =
    document.getElementById(
        "edit-task-button"
    );


if (editTaskButton) {

    editTaskButton.addEventListener(
        "click",
        showEditTask
    );

}


const editTaskForm =
    document.getElementById(
        "edit-task-form"
    );


if (editTaskForm) {

    editTaskForm.addEventListener(
        "submit",
        saveEditedTask
    );

}


document
    .querySelectorAll(
        "[data-close-edit-task-modal]"
    )
    .forEach(element => {

        element.addEventListener(
            "click",
            closeEditTaskModal
        );

    });

    const deleteTaskButton =
    document.getElementById(
        "delete-task-button"
    );


if (deleteTaskButton) {

    deleteTaskButton.addEventListener(
        "click",
        showDeleteTask
    );

}


const confirmDeleteTaskButton =
    document.getElementById(
        "confirm-delete-task-button"
    );


if (confirmDeleteTaskButton) {

    confirmDeleteTaskButton.addEventListener(
        "click",
        deleteTask
    );

}


document
    .querySelectorAll(
        "[data-close-delete-task-modal]"
    )
    .forEach(element => {

        element.addEventListener(
            "click",
            closeDeleteTaskModal
        );

    });

    
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


/* ============================================================
   TOGGLE TASK STATUS
   ============================================================ */

async function toggleTaskStatus() {

    const button =
        document.getElementById("toggle-task-button");

    const statusElement =
        document.getElementById("task-status");


    if (!button || !statusElement) {

        return;

    }


    const isCurrentlyActive =
        statusElement.textContent.trim() === "Active";


    const action =
        isCurrentlyActive
            ? "pause"
            : "resume";


    try {

        button.disabled = true;

        button.textContent =
            isCurrentlyActive
                ? "Pausing..."
                : "Resuming...";


        const response =
            await fetch(
                `${API_BASE_URL}/tasks/${taskId}/${action}`,
                {
                    method: "POST",

                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Accept": "application/json"
                    }
                }
            );


        if (response.status === 401) {

            handleUnauthorized();

            return;

        }


        if (response.status === 404) {

            alert(
                "Monitoring task not found."
            );

            window.location.href =
                "dashboard.html";

            return;

        }


        if (!response.ok) {

            let message =
                isCurrentlyActive
                    ? "Unable to pause monitoring task."
                    : "Unable to resume monitoring task.";


            try {

                const errorData =
                    await response.json();


                if (errorData.detail) {

                    message =
                        typeof errorData.detail === "string"
                            ? errorData.detail
                            : message;

                }

            }

            catch (_) {

                /*
                 * Keep the default message if
                 * the API response is not JSON.
                 */

            }


            throw new Error(message);

        }


        const result =
            await response.json();


        /*
         * The API returns:
         *
         * {
         *     "message": "...",
         *     "is_active": true/false
         * }
         */

        if (typeof result.is_active === "boolean") {

            statusElement.textContent =
                result.is_active
                    ? "Active"
                    : "Paused";


            button.textContent =
                result.is_active
                    ? "Pause Monitoring"
                    : "Resume Monitoring";


            button.classList.toggle(
                "task-resume-button",
                !result.is_active
            );

        }

    }

    catch (error) {

        console.error(
            "WatchTower: Failed to toggle task status:",
            error
        );


        alert(
            error.message ||
            "Unable to update task status."
        );


        /*
         * Restore the correct button label
         * after a failed request.
         */

        button.textContent =
            isCurrentlyActive
                ? "Pause Monitoring"
                : "Resume Monitoring";

    }

    finally {

        button.disabled = false;

    }

}

/* ============================================================
   OPEN EDIT TASK MODAL
   ============================================================ */

function showEditTask() {

    const modal =
        document.getElementById("edit-task-modal");


    const nameInput =
        document.getElementById("edit-task-name");


    const urlInput =
        document.getElementById("edit-task-url");


    const intervalInput =
        document.getElementById("edit-task-interval");


    const errorElement =
        document.getElementById("edit-task-error");


    if (
        !modal ||
        !nameInput ||
        !urlInput ||
        !intervalInput
    ) {

        console.error(
            "WatchTower: Edit task modal elements not found."
        );

        return;

    }


    /*
     * Use the values currently displayed on the page.
     */

    nameInput.value =
        document.getElementById("task-name").textContent.trim();


    urlInput.value =
        document.getElementById("task-url").textContent.trim();


    /*
     * The displayed interval may be "64 minutes",
     * "1 hour", etc., so we'll get the actual value
     * from the task API instead.
     */

    loadTaskForEditing();

}

/* ============================================================
   LOAD TASK FOR EDITING
   ============================================================ */

async function loadTaskForEditing() {

    const modal =
        document.getElementById("edit-task-modal");


    const nameInput =
        document.getElementById("edit-task-name");


    const urlInput =
        document.getElementById("edit-task-url");


    const intervalInput =
        document.getElementById("edit-task-interval");


    const errorElement =
        document.getElementById("edit-task-error");


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/tasks/${taskId}`,
                {
                    method: "GET",

                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Accept": "application/json"
                    }
                }
            );


        if (response.status === 401) {

            handleUnauthorized();

            return;

        }


        if (!response.ok) {

            throw new Error(
                "Unable to load task information."
            );

        }


        const task =
            await response.json();


        nameInput.value =
            task.name || "";


        urlInput.value =
            task.target_url || "";


        intervalInput.value =
            task.check_interval || "";


        if (errorElement) {

            errorElement.hidden = true;

            errorElement.textContent = "";

        }


        modal.hidden = false;

        document.body.classList.add(
            "modal-open"
        );


        nameInput.focus();

    }

    catch (error) {

        console.error(
            "WatchTower: Failed to load task for editing:",
            error
        );


        if (errorElement) {

            errorElement.textContent =
                error.message ||
                "Unable to load task information.";

            errorElement.hidden = false;

        }

    }

}

/* ============================================================
   SAVE EDITED TASK
   ============================================================ */

async function saveEditedTask(event) {

    event.preventDefault();


    const name =
        document.getElementById(
            "edit-task-name"
        ).value.trim();


    const targetUrl =
        document.getElementById(
            "edit-task-url"
        ).value.trim();


    const checkInterval =
        Number(
            document.getElementById(
                "edit-task-interval"
            ).value
        );


    const saveButton =
        document.getElementById(
            "save-task-button"
        );


    const errorElement =
        document.getElementById(
            "edit-task-error"
        );


    if (
        !name ||
        !targetUrl ||
        !checkInterval ||
        checkInterval < 1
    ) {

        showEditTaskError(
            "Please provide valid task information."
        );

        return;

    }


    try {

        saveButton.disabled = true;

        saveButton.textContent =
            "Saving...";


        if (errorElement) {

            errorElement.hidden = true;

            errorElement.textContent = "";

        }


        const response =
            await fetch(
                `${API_BASE_URL}/tasks/${taskId}`,
                {
                    method: "PUT",

                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        name: name,
                        target_url: targetUrl,
                        check_interval: checkInterval
                    })
                }
            );


        if (response.status === 401) {

            handleUnauthorized();

            return;

        }


        if (response.status === 404) {

            showEditTaskError(
                "Monitoring task not found."
            );

            return;

        }


        if (!response.ok) {

            let message =
                "Unable to update monitoring task.";


            try {

                const errorData =
                    await response.json();


                if (errorData.detail) {

                    message =
                        typeof errorData.detail === "string"
                            ? errorData.detail
                            : message;

                }

            }

            catch (_) {}


            throw new Error(message);

        }


        closeEditTaskModal();

        await loadTask();

    }

    catch (error) {

        console.error(
            "WatchTower: Failed to update task:",
            error
        );


        showEditTaskError(
            error.message ||
            "Unable to update monitoring task."
        );

    }

    finally {

        saveButton.disabled = false;

        saveButton.textContent =
            "Save Changes";

    }

}

/* ============================================================
   CLOSE EDIT TASK MODAL
   ============================================================ */

function closeEditTaskModal() {

    const modal =
        document.getElementById(
            "edit-task-modal"
        );


    if (!modal) {

        return;

    }


    modal.hidden = true;

    document.body.classList.remove(
        "modal-open"
    );


    const form =
        document.getElementById(
            "edit-task-form"
        );


    if (form) {

        form.reset();

    }


    const errorElement =
        document.getElementById(
            "edit-task-error"
        );


    if (errorElement) {

        errorElement.hidden = true;

        errorElement.textContent = "";

    }

}


function showEditTaskError(message) {

    const errorElement =
        document.getElementById(
            "edit-task-error"
        );


    if (!errorElement) {

        return;

    }


    errorElement.textContent =
        message;

    errorElement.hidden = false;

}

/* ============================================================
   DELETE TASK
   ============================================================ */

function showDeleteTask() {

    const modal =
        document.getElementById(
            "delete-task-modal"
        );


    const nameElement =
        document.getElementById(
            "delete-task-name"
        );


    const taskNameElement =
        document.getElementById(
            "task-name"
        );


    const errorElement =
        document.getElementById(
            "delete-task-error"
        );


    if (!modal) {

        return;

    }


    if (nameElement && taskNameElement) {

        nameElement.textContent =
            taskNameElement.textContent.trim();

    }


    if (errorElement) {

        errorElement.hidden = true;

        errorElement.textContent = "";

    }


    modal.hidden = false;

    document.body.classList.add(
        "modal-open"
    );

}

/* ============================================================
   CLOSE DELETE TASK MODAL
   ============================================================ */

function closeDeleteTaskModal() {

    const modal =
        document.getElementById(
            "delete-task-modal"
        );


    if (!modal) {

        return;

    }


    modal.hidden = true;

    document.body.classList.remove(
        "modal-open"
    );


    const errorElement =
        document.getElementById(
            "delete-task-error"
        );


    if (errorElement) {

        errorElement.hidden = true;

        errorElement.textContent = "";

    }

}

/* ============================================================
   CONFIRM DELETE TASK
   ============================================================ */

async function deleteTask() {

    const button =
        document.getElementById(
            "confirm-delete-task-button"
        );


    const errorElement =
        document.getElementById(
            "delete-task-error"
        );


    try {

        button.disabled = true;

        button.textContent =
            "Deleting...";


        if (errorElement) {

            errorElement.hidden = true;

            errorElement.textContent = "";

        }


        const response =
            await fetch(
                `${API_BASE_URL}/tasks/${taskId}`,
                {
                    method: "DELETE",

                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Accept": "application/json"
                    }
                }
            );


        if (response.status === 401) {

            handleUnauthorized();

            return;

        }


        if (response.status === 404) {

            if (errorElement) {

                errorElement.textContent =
                    "Monitoring task not found.";

                errorElement.hidden = false;

            }

            return;

        }


        if (!response.ok) {

            let message =
                "Unable to delete monitoring task.";


            try {

                const errorData =
                    await response.json();


                if (errorData.detail) {

                    message =
                        typeof errorData.detail === "string"
                            ? errorData.detail
                            : message;

                }

            }

            catch (_) {}


            throw new Error(message);

        }


        /*
         * Deletion succeeded.
         *
         * Return to the Dashboard rather than
         * leaving the user on a deleted resource.
         */

        window.location.href =
            "dashboard.html";

    }

    catch (error) {

        console.error(
            "WatchTower: Failed to delete task:",
            error
        );


        if (errorElement) {

            errorElement.textContent =
                error.message ||
                "Unable to delete monitoring task.";

            errorElement.hidden = false;

        }

    }

    finally {

        button.disabled = false;

        button.textContent =
            "Delete Task";

    }

}