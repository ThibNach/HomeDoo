const API_URL = "http://127.0.0.1:5000";

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
    const response = await fetch(`${API_URL}/modules`);
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

function openModal() {
    document.getElementById("modal").classList.remove("hidden");
}

function closeModal() {
    document.getElementById("modal").classList.add("hidden");
    document.getElementById("module-url").value = "";
}

async function installModule() {
    const url = document.getElementById("module-url").value.trim();
    if (!url) return alert("Please enter a URL");

    try {
        const response = await fetch(`${API_URL}/modules/install`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
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
        const response = await fetch(`${API_URL}/modules/uninstall`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, keep_data: false })
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