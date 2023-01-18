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
        taskId: '',
        resultIdList: []
    },
    reducers: {
        setRunState: (state, action) => {
            state.value = action.payload;
        },
        setTaskId: (state, action) => {
            state.taskId = action.payload;
        },
        setResultIdList: (state, action) => {
            state.resultIdList = action.payload;
        }
    },
})

// Action creators are generated for each case reducer function
export const { setRunState, setTaskId, setResultIdList } = runStateSlice.actions

export default runStateSlice.reducer
