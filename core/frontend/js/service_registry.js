class ServiceRegistry {
    constructor() {
        this.services = {};
    }

    register(name, service) {
        if (this.services[name]) {
            console.warn(`Service "${name}" is being overwritten`);
        }
        this.services[name] = service;
    }

    get(name) {
        if (!this.services[name]) {
            throw new Error(`Service "${name}" is not registered`);
        }
        return this.services[name];
    }

    has(name) {
        return name in this.services;
    }
}

export const serviceRegistry = new ServiceRegistry();