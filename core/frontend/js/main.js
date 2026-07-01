import {eventBus} from "./event_bus.js";
import {serviceRegistry} from "./service_registry.js";

const API_URL = "http://127.0.0.1:5000";

async function init() {
    await loadFrontendInits();

    await eventBus.emit("app:starting");

    await renderApp();
}

async function loadFrontendInits() {
    const response = await fetch(`${API_URL}/modules`);
    const modules = await response.json();

    for (const module of modules) {
        if (module.frontend_init) {
            await import(`${API_URL}/addons/${module.name.toLowerCase()}/js/${getFilename(module.frontend_init)}`);
        }
    }
}

async function renderApp() {
    document.getElementById("app").innerHTML = "";

    const auth = serviceRegistry.get("auth");

    const response = await fetch(`${API_URL}/modules`, {
        headers: auth.authHeaders()
    });
    const modules = await response.json();

    const nav = document.getElementById("nav");
    nav.innerHTML = "<img id='homelink' src='./public/logo.png' alt='#' width='50*1.8' height='50'>";
    const homeLink = document.getElementById('homelink');
    homeLink.addEventListener("click", async (e) => {
        e.preventDefault();
        await renderApp();
    });

    // Modules normaux dans la navbar
    modules.forEach(module => {
        if (module.core_module) return;
        if (!module.frontend_path) return;

        const link = document.createElement("a");
        link.href = `#${module.name}`;
        link.textContent = module.display_name || module.name;
        link.addEventListener("click", async (e) => {
            e.preventDefault();
            await loadAndRender(module);
        });
        nav.appendChild(link);
    });

    renderUserBar(auth, modules);
    render();
}

function renderUserBar(auth, modules) {
    const nav = document.getElementById("nav");
    const userBar = document.createElement("div");
    userBar.className = "user-bar";

    const person = auth.getPerson();

    // Burger menu pour les core_modules avec frontend_path
    const coreModules = modules.filter(m => m.core_module && m.frontend_path);

    userBar.innerHTML = `
        <div class="burger-menu">
            <button id="burger-btn">⚙</button>
            <div id="burger-dropdown" class="burger-dropdown hidden">
                ${coreModules.map(m => `<a href="#" data-module="${m.name}">${m.display_name || m.name}</a>`).join('')}
            </div>
        </div>
        <span>Logged in as <strong>${person.name}</strong></span>
        <button id="logout-btn">Logout</button>
    `;
    nav.appendChild(userBar);

    document.getElementById("burger-btn").addEventListener("click", () => {
        document.getElementById("burger-dropdown").classList.toggle("hidden");
    });

    document.querySelectorAll("#burger-dropdown a").forEach(a => {
        a.addEventListener("click", async (e) => {
            e.preventDefault();
            const moduleName = a.dataset.module;
            const module = modules.find(m => m.name === moduleName);
            await loadAndRender(module);
            document.getElementById("burger-dropdown").classList.add("hidden");
        });
    });

    document.getElementById("logout-btn").addEventListener("click", auth.logout);
    document.addEventListener("click", (e) => {
        const dropdown = document.getElementById("burger-dropdown");
        const burgerBtn = document.getElementById("burger-btn");
        if (!dropdown.contains(e.target) && e.target !== burgerBtn) {
            dropdown.classList.add("hidden");
        }
    });
}

async function loadAndRender(module) {
    const filename = getFilename(module.frontend_path);
    const moduleJs = await import(`${API_URL}/addons/${module.name.toLowerCase()}/js/${filename}`);
    if (typeof moduleJs.render === 'function') {
        moduleJs.render();
    }
}

function getFilename(path) {
    return path.split('/').pop();
}

export async function render() {
    const homePage = document.getElementById("app");
    const homeImage = document.createElement("img");
    homeImage.src = "./public/logo.png";
    homeImage.alt = "#";
    homeImage.width=550;
    homeImage.height=300;
    homeImage.style.display="block";
    homeImage.style.margin="0 auto";

    homePage.appendChild(homeImage);
}

init();