import {eventBus} from "http://127.0.0.1:3000/js/event_bus.js";
import {serviceRegistry} from "http://127.0.0.1:3000/js/service_registry.js";

const API_URL = "http://127.0.0.1:5000";
const TOKEN_KEY = "homedoo_token";
const PERSON_KEY = "homedoo_person";

// === Helpers exposés via service registry ===

function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function getPerson() {
    const data = localStorage.getItem(PERSON_KEY);
    return data ? JSON.parse(data) : null;
}

function isLoggedIn() {
    return getToken() !== null;
}

function authHeaders() {
    const token = getToken();
    return token ? {"Authorization": `Bearer ${token}`} : {};
}

function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(PERSON_KEY);
    window.location.reload();
}

// === Logique d'authentification ===

async function login(email, password) {
    const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email, password})
    });
    const data = await response.json();

    if (data.success) {
        localStorage.setItem(TOKEN_KEY, data.token);
        localStorage.setItem(PERSON_KEY, JSON.stringify(data.person));
        return {success: true};
    }
    return {success: false, error: data.error};
}

async function register(name, email, password) {
    const response = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({name, email, password})
    });
    const data = await response.json();
    return data;
}

// === UI Login/Register ===

function showLoginAndWait() {
    return new Promise((resolve) => {
        renderLoginScreen(resolve);
    });
}

function renderLoginScreen(onSuccess) {
    const app = document.getElementById("app");
    app.innerHTML = `
        <div class="login-container">
            <div class="login-box">
                <h2>Login</h2>
                <input type="email" id="login-email" placeholder="Email" />
                <input type="password" id="login-password" placeholder="Password" />
                <button id="login-btn">Login</button>
                <p class="register-link">No account? <a href="#" id="show-register">Register</a></p>
                <div id="login-error" class="error hidden"></div>
            </div>
        </div>
    `;

    document.getElementById("login-btn").addEventListener("click", () => handleLogin(onSuccess));
    document.getElementById("show-register").addEventListener("click", (e) => {
        e.preventDefault();
        renderRegisterScreen(onSuccess);
    });
    const inputs = ["login-email", "login-password"];
    inputs.forEach(id => {
        document.getElementById(id).addEventListener("keydown", (e) => {
            if (e.key === "Enter") handleLogin(onSuccess);
        });
    });
}

function renderRegisterScreen(onSuccess) {
    const app = document.getElementById("app");
    app.innerHTML = `
        <div class="login-container">
            <div class="login-box">
                <h2>Register</h2>
                <input type="text" id="register-name" placeholder="Name" />
                <input type="email" id="register-email" placeholder="Email" />
                <input type="password" id="register-password" placeholder="Password" />
                <button id="register-btn">Register</button>
                <p class="register-link">Already have an account? <a href="#" id="show-login">Login</a></p>
                <div id="register-error" class="error hidden"></div>
            </div>
        </div>
    `;

    document.getElementById("register-btn").addEventListener("click", () => handleRegister(onSuccess));
    document.getElementById("show-login").addEventListener("click", (e) => {
        e.preventDefault();
        renderLoginScreen(onSuccess);
    });
    const inputs = ["register-email", "register-password", "register-name"];
    inputs.forEach(id => {
        document.getElementById(id).addEventListener("keydown", (e) => {
            if (e.key === "Enter") handleRegister(onSuccess);
        });
    });
}

async function handleLogin(onSuccess) {
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;

    if (!email || !password) {
        showError("login-error", "Please fill in all fields");
        return;
    }

    const result = await login(email, password);
    if (result.success) {
        onSuccess();
    } else {
        showError("login-error", result.error || "Login failed");
    }
}

async function handleRegister(onSuccess) {
    const name = document.getElementById("register-name").value.trim();
    const email = document.getElementById("register-email").value.trim();
    const password = document.getElementById("register-password").value;

    if (!name || !email || !password) {
        showError("register-error", "Please fill in all fields");
        return;
    }

    const result = await register(name, email, password);
    if (result.success) {
        const loginResult = await login(email, password);
        if (loginResult.success) {
            onSuccess();
        }
    } else {
        showError("register-error", result.error || "Registration failed");
    }
}

function showError(elementId, message) {
    const el = document.getElementById(elementId);
    el.textContent = message;
    el.classList.remove("hidden");
}

// === Enregistrement du service auth ===

serviceRegistry.register("auth", {
    getToken,
    getPerson,
    isLoggedIn,
    authHeaders,
    logout
});

// === Subscription à l'event d'init ===

eventBus.on("app:starting", async () => {
    if (!isLoggedIn()) {
        await showLoginAndWait();
    }
});