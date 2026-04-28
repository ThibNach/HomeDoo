import { serviceRegistry } from "http://127.0.0.1:3000/js/service_registry.js";

const API_URL = "http://127.0.0.1:5000";

export async function render() {
    const auth = serviceRegistry.get("auth");

    if (!document.getElementById("persons-manager-css")) {
        const link = document.createElement("link");
        link.id = "persons-manager-css";
        link.rel = "stylesheet";
        link.href = `${API_URL}/addons/auth/styles/auth.css`;
        document.head.appendChild(link);
    }

    const app = document.getElementById("app");
    app.innerHTML = `
        <div class="persons-manager">
            <div class="header">
                <h2>Persons Management</h2>
                <button id="add-person-btn">+ Add Person</button>
            </div>
            <div id="persons-list"></div>
        </div>
        <div id="person-modal" class="modal hidden">
            <div class="modal-content">
                <h3>Add Person</h3>
                <input type="text" id="person-name" placeholder="Name" />
                <div class="modal-actions">
                    <button id="cancel-add">Cancel</button>
                    <button id="confirm-add">Add</button>
                </div>
            </div>
        </div>
    `;

    await loadPersons(auth);

    document.getElementById("add-person-btn").addEventListener("click", () => {
        document.getElementById("person-modal").classList.remove("hidden");
    });
    document.getElementById("cancel-add").addEventListener("click", closeModal);
    document.getElementById("confirm-add").addEventListener("click", () => addPerson(auth));
}

async function loadPersons(auth) {
    const response = await fetch(`${API_URL}/auth/persons`, {
        headers: auth.authHeaders()
    });
    const persons = await response.json();
    const currentPerson = auth.getPerson();

    const list = document.getElementById("persons-list");
    list.innerHTML = "";

    if (persons.length === 0) {
        list.innerHTML = "<p>No persons yet.</p>";
        return;
    }

    persons.forEach(person => {
        const item = document.createElement("div");
        item.className = "person-item";
        const isCurrentUser = person.id === currentPerson.id;
        item.innerHTML = `
            <span><strong>${person.name}</strong>${isCurrentUser ? ' (you)' : ''}</span>
            ${isCurrentUser ? '' : `<button class="delete-btn" data-id="${person.id}">Delete</button>`}
        `;
        list.appendChild(item);
    });

    document.querySelectorAll(".delete-btn").forEach(btn => {
        btn.addEventListener("click", () => deletePerson(auth, btn.dataset.id));
    });
}

async function addPerson(auth) {
    const name = document.getElementById("person-name").value.trim();
    if (!name) return alert("Please enter a name");

    try {
        const response = await fetch(`${API_URL}/auth/create_person`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...auth.authHeaders()
            },
            body: JSON.stringify({ name })
        });
        const data = await response.json();

        if (data.success) {
            closeModal();
            await loadPersons(auth);
        } else {
            alert(`Failed: ${data.error}`);
        }
    } catch (e) {
        alert(`Error: ${e.message}`);
    }
}

async function deletePerson(auth, id) {
    if (!confirm("Delete this person?")) return;

    try {
        const response = await fetch(`${API_URL}/auth/delete_person`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...auth.authHeaders()
            },
            body: JSON.stringify({ id: parseInt(id) })
        });
        const data = await response.json();

        if (data.success) {
            await loadPersons(auth);
        } else {
            alert(`Failed: ${data.error}`);
        }
    } catch (e) {
        alert(`Error: ${e.message}`);
    }
}

function closeModal() {
    document.getElementById("person-modal").classList.add("hidden");
    document.getElementById("person-name").value = "";
}