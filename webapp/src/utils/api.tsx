import { FieldDescriptionWithSetAndValue } from '../models/Service';

export const getServices = async () => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/services`);
    if (response.status === 200) {
        const json = await response.json();
        return json.filter((item: any) => item.status === 'available');
    }
    return [];
}

export const getPipelines = async () => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/pipelines`);
    if (response.status === 200) {
        const json = await response.json();
        return json.filter((item: any) => item.status === 'available');
    }
    return [];
}

export const getServiceDescription = async (id: string) => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/services/` + id);
    if (response.status === 200) {
        return await response.json();
    }
    return null;
}

export const getPipelineDescription = async (id: string) => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/pipelines/` + id);
    if (response.status === 200) {
        return await response.json();
    }
    return null;
}

export const getStats = async () => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/stats`);
    if (response.status === 200) {
        return await response.json();
    }
    return [];
}

export const getTask = async (id: string) => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/tasks/${id}`);
    if (response.status === 200) {
        return await response.json();
    }
    return [];
}

export const getResult = async (id: string) => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/storage/${id}`);
    if (response.status === 200) {
        return response.blob();
    }
    return "";
}

export const postToService = async (serviceSlug: string, parts: FieldDescriptionWithSetAndValue[]) => {
    try {
        const body = new FormData();

        for (const item of parts) {
            if (item.isSet) {
                body.append(item.name, item.value);
            }
        }

        const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/${serviceSlug}`, {
            method: 'POST',
            body,
        });

        if (response.status === 200) {
            return await response.json();
        }
        return false;
    } catch (error) {
        return error;
    }
}
