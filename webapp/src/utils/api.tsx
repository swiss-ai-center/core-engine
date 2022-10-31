const SERVER_URL = 'http://localhost:8080';

export const getServices = async () => {
    const response = await fetch(SERVER_URL + '/services');
    if (response) {
        const data = await response.json();
        return data.filter((service: any) => service.type === 'service');
    }
    return [];
}

export const getPipelines = async () => {
    const response = await fetch(SERVER_URL + '/services');
    if (response) {
        const data = await response.json();
        return data.filter((pipeline: any) => pipeline.type === 'pipeline');
    }
    return [];
}

export const getDescription = async (name: string) => {
    const response = await fetch(SERVER_URL + '/services/' + name);
    if (response) {
        const data = await response.json();
        return data;
    }
    return [];
}
