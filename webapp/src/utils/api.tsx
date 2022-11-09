export const getServices = async (type: string = 'service') => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/services`);
    if (response) {
        const data = await response.json();
        return data.filter((pipeline: any) => pipeline.type === type);
    }
    return [];
}

export const getServiceDescription = async (name: string) => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/services/` + name);
    if (response) {
        return await response.json();
    }
    return [];
}

export const getStats = async () => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/stats`);
    if (response) {
        return await response.json();
    }
    return [];
}

export const getTaskStatus = async (jobId: string) => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/tasks/${jobId}/status`);
    if (response) {
        return await response.json();
    }
    return [];
}

export const getResult = async (jobId: string) => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/tasks/${jobId}`);
    if (response) {
        return response.blob();
    }
    return "";
}

export const postToService = async (serviceName: string, parts: {field: string; value: string | Blob}[]) => {
    try {
        const body = new FormData();

        for (const item of parts) {
            body.append(item.field, item.value);
        }

        const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/services/${serviceName}`, {
            method: 'POST',
            body,
        });

        if (response) {
            return await response.json();
        }
        return false;
    } catch (error) {
        return error;
    }
}
