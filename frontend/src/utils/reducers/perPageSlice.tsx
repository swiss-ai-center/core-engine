import { createSlice } from '@reduxjs/toolkit'

export const PerPage = {
    6: 6,
    15: 15,
    30: 30,
    60: 60,
}

const initialState = {
    value: {
        services: PerPage[15],
        pipelines: PerPage[15],
    }
}

const saveToLocalStorage = (state: any) => {
    try {
        const serializedState = JSON.stringify(state);
        localStorage.setItem('perPageState', serializedState);
    } catch (e) {
        console.error(e);
    }
}

const loadFromLocalStorage = () => {
    try {
        const serializedState = localStorage.getItem('perPageState');
        if (serializedState === null) return initialState;
        return JSON.parse(serializedState);
    } catch (e) {
        return initialState;
    }
}

export const perPageSlice = createSlice({
    name: 'perPage',
    initialState: loadFromLocalStorage(),
    reducers: {
        setServicePerPage: (state, action) => {
            state.value.services = action.payload;
            saveToLocalStorage(state);
        },
        setPipelinePerPage: (state, action) => {
            state.value.pipelines = action.payload;
            saveToLocalStorage(state);
        }
    },
})

// Action creators are generated for each case reducer function
export const { setServicePerPage, setPipelinePerPage } = perPageSlice.actions

export default perPageSlice.reducer
