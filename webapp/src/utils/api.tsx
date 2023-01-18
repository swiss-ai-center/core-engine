import { FieldDescriptionWithSetAndValue } from '../models/Service';

export const getServices = async () => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/services`);
    if (response) {
        return await response.json();
    }
    return [];
}

export const getPipelines = async () => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/pipelines`);
    if (response) {
        return await response.json();
    }
    return [];
}

export const getServiceDescription = async (id: string) => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/services/` + id);
    if (response) {
        return await response.json();
    }
    return [];
}

export const getPipelineDescription = async (id: string) => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/pipelines/` + id);
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

export const getTask = async (id: string) => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/tasks/${id}`);
    if (response) {
        return await response.json();
    }
    return [];
}

export const getResult = async (id: string) => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/storage/${id}`);
    if (response) {
        console.log(response)
        return response.blob();
    }
    console.log("no response")
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

        if (response) {
            console.log(response);
            return await response.json();
        }
        console.log("oskour")
        return false;
    } catch (error) {
        console.log(error);
        return error;
    }
}
