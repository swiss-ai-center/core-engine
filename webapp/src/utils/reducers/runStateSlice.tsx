import { createSlice } from '@reduxjs/toolkit'

export enum RunState {
    IDLE = "idle",
    PENDING = "pending",
    FETCHING = "fetching",
    PROCESSING = "processing",
    SAVING = "saving",
    FINISHED = "finished",
    ERROR = "error",
    SCHEDULED = "scheduled",
    SKIPPED = "skipped",
    ARCHIVED = "archived",
    UNAVAILABLE = "unavailable"
}

export const runStateSlice = createSlice({
    name: 'runState',
    initialState: {
        value: RunState.IDLE,
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
    }
})

// Action creators are generated for each case reducer function
export const { setRunState, setTaskId, setResultIdList } = runStateSlice.actions

export default runStateSlice.reducer
