import { FieldDescriptionWithSetAndValue } from '../models/ExecutionUnit';

const createQuery = (unit: string, filter: string, skip: number, limit: number, orderBy: string, tags: string[]) => {
    const infos = orderBy.split('-');
    const prop = infos[0];
    const asc = infos[1] === 'asc';

    let query = `${process.env.REACT_APP_ENGINE_URL}/${unit}?`;

    if (filter !== '') {
        query += `search=${filter}`;
    }
    if (orderBy !== '') {
        query += `&order_by=${prop}&order=${asc ? 'asc' : 'desc'}`;
    }
    if (tags.length > 0) {
        query += `&tags=${tags.join(',')}`;
    }
    if (skip !== 0) {
        query += `&skip=${skip}`;
    }
    if (limit !== 0) {
        query += `&limit=${limit}`;
    }

    return query;
}

export const getServices = async (filter: string, skip: number, limit: number, orderBy: string, tags: string[]) => {
    const query = createQuery('services', filter, skip, limit, orderBy, tags);
    
    const response = await fetch(query);
    if (response.status === 200) {
        return await response.json();
    }
    return [];
}

export const getPipelines = async (filter: string, skip: number, limit: number, orderBy: string, tags: string[]) => {
    const query = createQuery('pipelines', filter, skip, limit, orderBy, tags);

    const response = await fetch(query);
    if (response.status === 200) {
        return await response.json();
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

export const postToEngine = async (serviceSlug: string, parts: FieldDescriptionWithSetAndValue[]) => {
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
            const result = await response.json();
            if (result.tasks) {
                // this means that this is a Pipeline
                // return the last task
                return result.tasks[result.tasks.length - 1];
            } else {
                // this means that this is a Service
                return result;
            }
        }
        return false;
    } catch (error) {
        return error;
    }
}
