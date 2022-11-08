import { createSlice } from '@reduxjs/toolkit'

export const RunState = {
    STOPPED: 0,
    RUNNING: 1,
    PAUSED: 2,
    ENDED: 3,
    ERROR: 4
};

export const runStateSlice = createSlice({
    name: 'runState',
    initialState: {
        value: RunState.STOPPED,
    },
    reducers: {
        setRunState: (state, action) => {
            state.value = action.payload;
            console.log(state.value);
        }
    },
})

// Action creators are generated for each case reducer function
export const { setRunState } = runStateSlice.actions

export default runStateSlice.reducer
