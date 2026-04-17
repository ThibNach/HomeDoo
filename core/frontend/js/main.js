const API_URL = "http://127.0.0.1:5000";

async function loadModules() {
    const response = await fetch(`${API_URL}/modules`);
    const modules = await response.json();

    const nav = document.getElementById("nav");
    modules.forEach(module => {
        const link = document.createElement("a");
        link.href = `#${module.name}`;
        link.textContent = module.name;
        link.addEventListener("click", async (e) => {
            e.preventDefault();
            /** @type {{ render: () => Promise<void> }} */
            const module_js = await import(`${API_URL}/addons/${module.name.toLowerCase()}/js/${module.name.toLowerCase()}.js`);
            await module_js.render();
        })
        nav.appendChild(link);
    });
}

loadModules();