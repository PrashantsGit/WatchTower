const API_BASE_URL = "http://127.0.0.1:8000/api";

const loginForm = document.getElementById("login-form");
const loginError = document.getElementById("login-error");

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    loginError.textContent = "";

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                email: email,
                password: password,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            loginError.textContent =
                data.detail || "Login failed. Please check your credentials.";

            return;
        }

        localStorage.setItem("access_token", data.access_token);

        window.location.href = "pages/dashboard.html";

    } catch (error) {
        console.error("Login error:", error);

        loginError.textContent =
            "Unable to connect to WatchTower.";
    }
});