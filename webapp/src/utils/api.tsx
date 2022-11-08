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
        const data = await response.json();
        return data;
    }
    return [];
}

export const getStats = async () => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/stats`);
    if (response) {
        const data = await response.json();
        return data;
    }
    return [];
}

export const postToService = async (serviceName: string, body: BodyInit | null | undefined) => {
    try {
        const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/services/${serviceName}`, {
            method: 'POST',
            body,
        });

        if (response) {
            const data = await response.json();
            return data;
        }
        return false;
    } catch (error) {
        return error;
    }
}

export const postToServiceAsFormData = async (serviceName: string, parts: {field: string; value: string | Blob}[]) => {
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
            const data = await response.json();
            return data;
        }
        return false;
    } catch (error) {
        return error;
    }
}
