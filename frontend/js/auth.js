/* ============================================================
   WATCHTOWER — AUTHENTICATION
   Login and session handling
   ============================================================ */


/* ============================================================
   CONFIGURATION
   ============================================================ */

const API_BASE_URL = "http://127.0.0.1:8000/api";

const ACCESS_TOKEN_KEY = "access_token";


/* ============================================================
   ELEMENTS
   ============================================================ */

const loginForm =
    document.getElementById("login-form");

const emailInput =
    document.getElementById("email");

const passwordInput =
    document.getElementById("password");

const loginButton =
    document.getElementById("login-button");

const loginError =
    document.getElementById("login-error");


/* ============================================================
   ERROR DISPLAY
   ============================================================ */

function showLoginError(message) {

    if (!loginError) {
        return;
    }

    loginError.textContent = message;
    loginError.hidden = false;
}


function clearLoginError() {

    if (!loginError) {
        return;
    }

    loginError.textContent = "";
    loginError.hidden = true;
}


/* ============================================================
   BUTTON STATE
   ============================================================ */

function setLoginLoading(isLoading) {

    if (!loginButton) {
        return;
    }

    loginButton.disabled = isLoading;

    loginButton.textContent =
        isLoading
            ? "Signing In..."
            : "Sign In";
}


/* ============================================================
   LOGIN REQUEST
   ============================================================ */

async function authenticate(email, password) {

    const response = await fetch(
        `${API_BASE_URL}/auth/login`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email,
                password
            })
        }
    );


    let data = null;

    try {

        data = await response.json();

    } catch {

        data = null;

    }


    if (!response.ok) {

        if (response.status === 401) {

            throw new Error(
                "Invalid email or password."
            );
        }


        if (response.status === 422) {

            throw new Error(
                "Please enter a valid email and password."
            );
        }


        throw new Error(
            data?.detail ||
            data?.error?.message ||
            "Login failed. Please try again."
        );
    }


    if (!data?.access_token) {

        throw new Error(
            "WatchTower returned an invalid login response."
        );
    }


    return data;
}


/* ============================================================
   LOGIN FORM
   ============================================================ */

if (loginForm) {

    loginForm.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();

            clearLoginError();


            const email =
                emailInput.value.trim();

            const password =
                passwordInput.value;


            /* -----------------------------------------------
               Client-side validation
               ----------------------------------------------- */

            if (!email) {

                showLoginError(
                    "Please enter your email address."
                );

                emailInput.focus();

                return;
            }


            if (!password) {

                showLoginError(
                    "Please enter your password."
                );

                passwordInput.focus();

                return;
            }


            /* -----------------------------------------------
               Submit
               ----------------------------------------------- */

            setLoginLoading(true);


            try {

                const data =
                    await authenticate(
                        email,
                        password
                    );


                /* -------------------------------------------
                   Store access token
                   ------------------------------------------- */

                localStorage.setItem(
                    ACCESS_TOKEN_KEY,
                    data.access_token
                );


                /* -------------------------------------------
                   Continue to application
                   ------------------------------------------- */

                window.location.href = "pages/dashboard.html";


            } catch (error) {

                console.error(
                    "WatchTower login error:",
                    error
                );


                showLoginError(
                    error.message ||
                    "Unable to sign in. Please try again."
                );


                setLoginLoading(false);

            }

        }
    );

}