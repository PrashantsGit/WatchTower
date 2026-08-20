const API_BASE_URL = "http://127.0.0.1:8000/api";

const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "../index.html";
}


// Get task ID from URL
const params = new URLSearchParams(window.location.search);
const taskId = params.get("task_id");


// Make sure we know which task this rule belongs to
if (!taskId) {
    window.location.href = "dashboard.html";
}


// Back to task
document
    .getElementById("back-button")
    .addEventListener("click", (event) => {

        event.preventDefault();

        window.location.href = `task.html?id=${taskId}`;
    });


// Form elements
const ruleTypeSelect = document.getElementById("rule-type");
const operatorSelect = document.getElementById("operator");
const targetValueInput = document.getElementById("target-value");
const targetHint = document.getElementById("target-hint");
const ruleForm = document.getElementById("rule-form");
const errorMessage = document.getElementById("rule-error");
const createButton = document.getElementById("create-rule-button");


// Available conditions
const ruleOptions = {

    PRICE: {
        operators: [
            { value: "<", label: "Less than" },
            { value: "<=", label: "Less than or equal to" },
            { value: "=", label: "Equal to" },
            { value: ">=", label: "Greater than or equal to" },
            { value: ">", label: "Greater than" }
        ],
        placeholder: "e.g. 50000",
        hint: "Enter the target price."
    },

    STOCK: {
        operators: [
            { value: "=", label: "Available" }
        ],
        placeholder: "true",
        hint: "Enter true when the product should be in stock."
    },

    KEYWORD: {
        operators: [
            { value: "contains", label: "Contains" }
        ],
        placeholder: "e.g. discount",
        hint: "Enter the keyword to monitor."
    }

};


// Update operators when rule type changes
ruleTypeSelect.addEventListener("change", () => {

    const selectedType = ruleTypeSelect.value;

    operatorSelect.innerHTML = `
        <option value="">
            Select condition
        </option>
    `;

    targetValueInput.value = "";
    targetValueInput.placeholder = "Enter target value";
    targetHint.textContent = "Choose a rule type first.";

    if (!selectedType) {
        return;
    }

    const configuration = ruleOptions[selectedType];

    configuration.operators.forEach(operator => {

        const option = document.createElement("option");

        option.value = operator.value;
        option.textContent = operator.label;

        operatorSelect.appendChild(option);

    });

    targetValueInput.placeholder = configuration.placeholder;
    targetHint.textContent = configuration.hint;
});


// Display an error
function showError(message) {

    errorMessage.textContent = message;
    errorMessage.style.display = "block";
}


// Hide error
function hideError() {

    errorMessage.textContent = "";
    errorMessage.style.display = "none";
}


// Create rule
ruleForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    hideError();

    const ruleType = ruleTypeSelect.value;
    const operator = operatorSelect.value;
    const targetValue = targetValueInput.value.trim();

    if (!ruleType || !operator || !targetValue) {

        showError("Please complete all fields.");

        return;
    }


    createButton.disabled = true;
    createButton.textContent = "Creating...";


    try {

        const response = await fetch(
            `${API_BASE_URL}/tasks/${taskId}/rules`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`,
                },

                body: JSON.stringify({
                    rule_type: ruleType,
                    operator: operator,
                    target_value: targetValue,
                }),
            }
        );


        if (response.status === 401) {

            localStorage.removeItem("access_token");

            window.location.href = "../index.html";

            return;
        }


        if (!response.ok) {

            let message = "Failed to create monitoring rule.";

            try {

                const errorData = await response.json();

                if (errorData.detail) {
                    message = errorData.detail;
                }

            } catch {
                // Keep default error message
            }

            throw new Error(message);
        }


        // Rule created successfully
        window.location.href = `task.html?id=${taskId}`;


    } catch (error) {

        console.error("Create rule error:", error);

        showError(error.message);

        createButton.disabled = false;
        createButton.textContent = "Create Rule";
    }
});