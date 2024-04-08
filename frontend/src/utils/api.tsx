import { FieldDescriptionWithSetAndValue } from '../models/ExecutionUnit';

// Allow all origins
const HEADERS = {
    'Access-Control-Allow-Origin': '*',
}

const createQuery = (
    unit: string,
    filter: string,
    skip: number,
    limit: number,
    orderBy: string,
    tags: string[],
    ai?: boolean
) => {
    /*
     * Function to create the query string for the engine
     * unit: string - the unit to query (services or pipelines)
     * filter: string - the search string
     * skip: number - the number of items to skip
     * limit: number - the number of items to return
     * orderBy: string - the order by string
     * tags: string[] - the tags to filter by
     * ai: boolean - whether to filter by AI or not
     */
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
    if (ai) {
        query += `&ai=${ai}`;
    }

    return query + '&with_count=True&status=AVAILABLE';
}

export const getServices = async (filter: string, skip: number, limit: number, orderBy: string, tags: string[], ai: boolean) => {
    /*
     * Function to fetch services from the engine
     * filter: string - the search string
     * skip: number - the number of items to skip
     * limit: number - the number of items to return
     * orderBy: string - the order by string
     * tags: string[] - the tags to filter by
     * ai: boolean - whether to filter by AI or not
     */
    try {
        const query = createQuery('services', filter, skip, limit, orderBy, tags, ai);

        const response = await fetch(query, {headers: HEADERS});
        if (response.status === 200) {
            return await response.json();
        }
        return {services: [], count: 0};
    } catch (error: any) {
        return {error: error.message};
    }
}

export const getPipelines = async (filter: string, skip: number, limit: number, orderBy: string, tags: string[]) => {
    /*
     * Function to fetch pipelines from the engine
     * filter: string - the search string
     * skip: number - the number of items to skip
     * limit: number - the number of items to return
     * orderBy: string - the order by string
     * tags: string[] - the tags to filter by
     */
    try {
        const query = createQuery('pipelines', filter, skip, limit, orderBy, tags);

        const response = await fetch(query, {headers: HEADERS});
        if (response.status === 200) {
            return await response.json();
        }
        return {pipelines: [], count: 0};
    } catch (error: any) {
        return {error: error.message};
    }
}

export const getServiceDescriptionById = async (id: string) => {
    /*
     * Function to fetch a service description from the engine
     * id: string - the id of the service
     */
    try {
        const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/services/` + id, {headers: HEADERS});
        if (response.status === 200) {
            return await response.json();
        }
        return null;
    } catch (error: any) {
        return {error: error.message}
    }
}

export const getServiceDescription = async (slug: string) => {
    /*
     * Function to fetch a service description from the engine
     * slug: string - the slug of the service
     */
    try {
        const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/services/slug/` + slug, {headers: HEADERS});
        if (response.status === 200) {
            return await response.json();
        }
        return null;
    } catch (error: any) {
        return {error: error.message}
    }
}

export const getPipelineDescription = async (slug: string) => {
    /*
     * Function to fetch a pipeline description from the engine
     * slug: string - the slug of the pipeline
     */
    try {
        const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/pipelines/slug/` + slug, {headers: HEADERS});
        if (response.status === 200) {
            return await response.json();
        }
        return null;
    } catch (error: any) {
        return {error: error.message}
    }
}

export const getStats = async () => {
    /*
     * Function to fetch stats from the engine
     */
    try {
        const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/stats`, {headers: HEADERS});
        if (response.status === 200) {
            return await response.json();
        }
        return null;
    } catch (error: any) {
        return {error: error.message}
    }
}

export const getTask = async (id: string) => {
    /*
     * Function to fetch a task from the engine
     * id: string - the id of the task
     */
    try {
        const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/tasks/${id}`, {headers: HEADERS});
        if (response.status === 200) {
            return await response.json();
        }
        return {total: 0, summary: []};
    } catch (error: any) {
        return {error: error.message}
    }
}

export const getResult = async (id: string) => {
    /*
     * Function to fetch a result from the engine
     * id: string - the id of the result
     */
    try {
        const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/storage/${id}`, {headers: HEADERS});
        if (response.status === 200) {
            return {file: await response.blob()};
        }
        return {file: ""};
    } catch (error: any) {
        return {error: error.message}
    }
}

export const postToEngine = async (serviceSlug: string, parts: FieldDescriptionWithSetAndValue[]) => {
    /*
     * Function to post a task to the engine
     * serviceSlug: string - the slug of the service
     * parts: FieldDescriptionWithSetAndValue[] - the parts of the form data
     */
    try {
        const body = new FormData();

        for (const item of parts) {
            if (item.isSet) {
                body.append(item.name, item.value);
            }
        }

        const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/${serviceSlug}`, {
            headers: HEADERS,
            method: 'POST',
            body,
        });

        if (response.status === 200) {
            return await response.json();
        }
        return {error: `${response.status} ${response.statusText}`};
    } catch (error: any) {
        return {error: error.message}
    }
}
