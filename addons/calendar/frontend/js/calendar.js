const API_URL = "http://127.0.0.1:5000";

export async function render() {
    const response = await fetch(`${API_URL}/calendar/entries`);
    const entries = await response.json();
    
    const app = document.getElementById('app');
    app.innerHTML = ``;
    
    entries.forEach(entry => {
        const div = document.createElement('div');
        div.textContent = `${entry[1]} -- ${entry[2]}`;
        app.appendChild(div);
    })
}