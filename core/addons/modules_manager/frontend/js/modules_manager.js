const API_URL = "http://127.0.0.1:5000";
import { serviceRegistry } from "http://127.0.0.1:3000/js/service_registry.js";


export async function render() {
    
    if (!document.getElementById("modules-manager-css")) {
        const link = document.createElement("link");
        link.id = "modules-manager-css";
        link.rel = "stylesheet";
        link.href = `${API_URL}/addons/modules_manager/styles/modules_manager.css`;
        document.head.appendChild(link);
    }
    
    const app = document.getElementById("app");
    app.innerHTML = `
        <div class="modules-manager">
            <div class="header">
                <h2>Installed Modules</h2>
                <button id="add-module-btn">+ Add Module</button>
            </div>
            <div id="modules-list"></div>
        </div>
        <div id="modal" class="modal hidden">
            <div class="modal-content">
                <h3>Install a Module</h3>
                <div id="catalog-section">
                    <h4>From catalog</h4>
                    <div id="catalog-list">Loading...</div>
                </div>
                
                <div class="separator">Or install from custom URL</div>
                
                <input type="text" id="module-url" placeholder="GitHub repository URL" />
                <div class="modal-actions">
                    <button id="cancel-install">Cancel</button>
                    <button id="confirm-install">Install</button>
                </div>
            </div>
        </div>
        <div id="restart-overlay" class="overlay hidden">
            <div class="overlay-content">
                <h2 id="overlay-title">Module installed successfully</h2>
                <p>Please restart the server to activate the module.</p>
            </div>
        </div>
    `;

    await loadModules();

    document.getElementById("add-module-btn").addEventListener("click", openModal);
    document.getElementById("cancel-install").addEventListener("click", closeModal);
    document.getElementById("confirm-install").addEventListener("click", installModule);
}

async function loadModules() {
    const auth = serviceRegistry.get("auth");
    const response = await fetch(`${API_URL}/modules`, {
        headers: auth.authHeaders()
    });
    const modules = await response.json();
    const installables = modules.filter(m => !m.core_module);

    const list = document.getElementById("modules-list");
    list.innerHTML = "";

    if (installables.length === 0) {
        list.innerHTML = "<p>No modules installed yet.</p>";
        return;
    }

    installables.forEach(module => {
        const item = document.createElement("div");
        item.className = "module-item";
        item.innerHTML = `
            <div>
                <strong>${module.name}</strong>
                <span class="version">v${module.version || "?"}</span>
            </div>
            <button class="uninstall-btn" data-name="${module.name}">Uninstall</button>
        `;
        list.appendChild(item);
    });

    document.querySelectorAll(".uninstall-btn").forEach(btn => {
        btn.addEventListener("click", () => uninstallModule(btn.dataset.name));
    });
}

async function openModal() {
    document.getElementById("modal").classList.remove("hidden");
    await loadCatalog();
}

function closeModal() {
    document.getElementById("modal").classList.add("hidden");
    document.getElementById("module-url").value = "";
}

async function installModule() {
    const url = document.getElementById("module-url").value.trim();
    if (!url) return alert("Please enter a URL");
    await installFromUrl(url);
}

async function installFromUrl(url, name = null) {
    try {
        const body = name ? {url,name} : {url};
        const auth = serviceRegistry.get("auth");
        const response = await fetch(`${API_URL}/modules/install`, {
            method: "POST",
            headers: { "Content-Type": "application/json" , ...auth.authHeaders() },
            body: JSON.stringify(body )
        });
        const data = await response.json();

        if (data.success) {
            closeModal();
            document.getElementById("overlay-title").textContent = "Module installed successfully";
            document.getElementById("restart-overlay").classList.remove("hidden");
        } else {
            alert(`Installation failed: ${data.error}`);
        }
    } catch (e) {
        alert(`Error: ${e.message}`);
    }
}

async function uninstallModule(name) {
    if (!confirm(`Uninstall ${name}?`)) return;

    try {
        const auth = serviceRegistry.get("auth");
        const response = await fetch(`${API_URL}/modules/uninstall`, {
            method: "POST",
            headers: { "Content-Type": "application/json", ...auth.authHeaders() },
            body: JSON.stringify({ name, keep_data: true })
        });
        const data = await response.json();

        if (data.success) {
            document.getElementById("overlay-title").textContent = "Module uninstalled successfully";
            document.getElementById("restart-overlay").classList.remove("hidden");
        } else {
            alert(`Uninstall failed: ${data.error}`);
        }
    } catch (e) {
        alert(`Error: ${e.message}`);
    }
}

async function loadCatalog() {
    try {
        const [catalogResponse, modulesResponse] = await Promise.all([
            fetch(`${API_URL}/modules/catalog`),
            fetch(`${API_URL}/modules`)
        ]);
        const catalogData = await catalogResponse.json();
        const installedModules = await modulesResponse.json();

        const installedNames = new Set(
            installedModules.map(m => m.name.toLowerCase())
        );

        const list = document.getElementById("catalog-list");
        list.innerHTML = "";

        if (!catalogData.modules || catalogData.modules.length === 0) {
            list.innerHTML = "<p>No modules available in catalog.</p>";
            return;
        }

        catalogData.modules.forEach(module => {
            const isInstalled = installedNames.has(module.name.toLowerCase());
            const item = document.createElement("div");
            item.className = "catalog-item";
            item.innerHTML = `
                <div>
                    <strong>${module.name}</strong>
                    <span class="version">v${module.version}</span>
                    <p class="description">${module.description}</p>
                </div>
                <button 
                    class="${isInstalled ? 'installed-btn' : 'catalog-install-btn'}" 
                    data-url="${module.url}"
                    data-name="${module.name}"
                    ${isInstalled ? 'disabled' : ''}>
                    ${isInstalled ? 'Installed' : 'Install'}
                </button>
            `;
            list.appendChild(item);
        });

        document.querySelectorAll(".catalog-install-btn").forEach(btn => {
            btn.addEventListener("click", () => installFromUrl(btn.dataset.url, btn.dataset.name));
        });
    } catch (e) {
        document.getElementById("catalog-list").innerHTML =
            `<p>Failed to load catalog: ${e.message}</p>`;
    }
}