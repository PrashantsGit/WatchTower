const API_BASE_URL = "http://127.0.0.1:8000/api";

const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "index.html";
}


async function loadCurrentUser() {

    try {

        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });

        if (response.status === 401) {
            localStorage.removeItem("access_token");
            window.location.href = "index.html";
            return;
        }

        if (!response.ok) {
            return;
        }

        const user = await response.json();

        document.getElementById("user-name").textContent =
            user.full_name;

    } catch (error) {

        console.error(
            "Unable to load user profile:",
            error
        );

    }
}


function showMessage(message, type) {

    const messageElement =
        document.getElementById("form-message");

    messageElement.textContent = message;

    messageElement.className =
        `form-message ${type}`;
}


function clearMessage() {

    const messageElement =
        document.getElementById("form-message");

    messageElement.textContent = "";

    messageElement.className =
        "form-message";
}


async function createTask(event) {

    event.preventDefault();

    clearMessage();

    const createButton =
        document.getElementById("create-button");

    const name =
        document.getElementById("task-name").value.trim();

    const description =
        document.getElementById("task-description").value.trim();

    const targetUrl =
        document.getElementById("target-url").value.trim();

    const checkInterval =
        Number(
            document.getElementById("check-interval").value
        );


    if (!name) {
        showMessage(
            "Task name is required.",
            "error"
        );
        return;
    }


    if (!targetUrl) {
        showMessage(
            "Target URL is required.",
            "error"
        );
        return;
    }


    if (!checkInterval || checkInterval < 1) {
        showMessage(
            "Check interval must be at least 1 minute.",
            "error"
        );
        return;
    }


    const payload = {
        name: name,
        description: description || null,
        target_url: targetUrl,
        check_interval: checkInterval,
    };


    createButton.disabled = true;
    createButton.textContent = "Creating...";


    try {

        const response = await fetch(
            `${API_BASE_URL}/tasks`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`,
                },

                body: JSON.stringify(payload),
            }
        );


        if (response.status === 401) {

            localStorage.removeItem("access_token");

            window.location.href = "index.html";

            return;
        }


        const data = await response.json();


        if (!response.ok) {

            const errorMessage =
                data.detail ||
                "Unable to create monitoring task.";

            throw new Error(errorMessage);
        }


        showMessage(
            "Monitoring task created successfully.",
            "success"
        );


        setTimeout(() => {

            window.location.href =
                "dashboard.html";

        }, 800);


    } catch (error) {

        console.error(
            "Create task error:",
            error
        );

        showMessage(
            error.message ||
            "Unable to create monitoring task.",
            "error"
        );

    } finally {

        createButton.disabled = false;
        createButton.textContent = "Create Task";

    }
}


document
    .getElementById("create-task-form")
    .addEventListener(
        "submit",
        createTask
    );


document
    .getElementById("cancel-button")
    .addEventListener(
        "click",
        () => {
            window.location.href = "dashboard.html";
        }
    );


document
    .getElementById("logout-button")
    .addEventListener(
        "click",
        () => {

            localStorage.removeItem(
                "access_token"
            );

            window.location.href =
                "index.html";
        }
    );


loadCurrentUser();