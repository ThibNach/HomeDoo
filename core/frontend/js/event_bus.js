class EventBus {
    constructor() {
        this.listeners = {};
    }

    on(event, handler) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(handler);
    }

    async emit(event, data) {
        const handlers = this.listeners[event] || [];
        const promises = handlers.map(h => h(data));
        await Promise.all(promises);
    }

    off(event, handler) {
        if (!this.listeners[event]) return;
        this.listeners[event] = this.listeners[event].filter(h => h !== handler);
    }
}

export const eventBus = new EventBus();