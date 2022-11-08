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
        const data = await response.json();
        return data;
    }
    return [];
}

export const postService = async (name: string, body: any) => {
    console.log(body);
    const response = await fetch(`${process.env.REACT_APP_ENGINE_URL}/services/` + name, {
        method: 'POST',
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        body: body,
    }).catch((error) => {
        return error;
    });
    if (response) {
        return await response.json();
    }
    return false;
}
