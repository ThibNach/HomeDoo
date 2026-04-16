const API_URL = "http://127.0.0.1:5000";

async function loadModules() {
    const response = await fetch(`${API_URL}/modules`);
    const modules = await response.json();

    const nav = document.getElementById("nav");
    modules.forEach(module => {
        const link = document.createElement("a");
        link.href = `#${module.name}`;
        link.textContent = module.name;
        nav.appendChild(link);
    });
}

loadModules();