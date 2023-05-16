import { FieldDescriptionWithSetAndValue } from '../models/Service';

const createSortBy = (order: string) => {
    const infos = order.split('-');
    const prop = infos[0];
    const asc = infos[1] === 'asc';
    if (asc) {
        return function (a: any, b: any) {
            if (a[prop] > b[prop]) {
                return 1;
            } else if (a[prop] < b[prop]) {
                return -1;
            }
            return 0;
        }
    } else {
        return function (a: any, b: any) {
            if (a[prop] > b[prop]) {
                return -1;
            } else if (a[prop] < b[prop]) {
                return 1;
            }
            return 0;
        }
    }
}

const filterItems = (items: any, filter: string) => {
    return items.filter((item: any) => item.slug.toLowerCase().includes(filter.toLowerCase()) ||
        item.name.toLowerCase().includes(filter.toLowerCase()) ||
        item.summary.toLowerCase().includes(filter.toLowerCase()) ||
        item.description.toLowerCase().includes(filter.toLowerCase()));
}

export const getServices = async (filter: string, orderBy: string, tags: string[]) => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/services`);
    if (response.status === 200) {
        const json = await response.json();
        const available = json.filter((item: any) => item.status === 'available');
        const ordered = available.sort(createSortBy(orderBy));
        const tagFiltered = ordered.filter((item: any) => {
            if (tags.length === 0) {
                return true;
            } else if (!item.tags) {
                return false;
            }
            for (const tag of tags) {
                for (const itemTag of item.tags) {
                    if (itemTag.name.includes(tag)) {
                        return true;
                    }
                }
            }
            return false;
        });
        return filterItems(tagFiltered, filter);
    }
    return [];
}

export const getPipelines = async (filter: string, orderBy: string, tags: string[]) => {
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/pipelines`);
    if (response.status === 200) {
        const json = await response.json();
        const available = json.filter((item: any) => item.status === 'available');
        const ordered = available.sort(createSortBy(orderBy));
        const tagFiltered = ordered.filter((item: any) => {
            if (tags.length === 0) {
                return true;
            } else if (!item.tags) {
                return false;
            }
            for (const tag of tags) {
                for (const itemTag of item.tags) {
                    if (itemTag.name.includes(tag)) {
                        return true;
                    }
                }
            }
            return false;
        });
        return filterItems(tagFiltered, filter);
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
