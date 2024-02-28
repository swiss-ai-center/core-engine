import { createSlice } from '@reduxjs/toolkit'

export enum RunState {
    IDLE = "idle",
    PENDING = "pending",
    UPLOADING = "uploading",
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
        task: null,
        taskArray: [],
        resultIdList: [],
        generalStatus: RunState.IDLE,
        timer: 0.0
    },
    reducers: {
        setCurrentTask: (state, action) => {
            state.task = action.payload;
        },
        setTaskArray: (state, action) => {
            state.taskArray = action.payload;
        },
        setResultIdList: (state, action) => {
            state.resultIdList = action.payload;
        },
        setGeneralStatus: (state, action) => {
            state.generalStatus = action.payload;
        },
        resetTimer: (state) => {
            state.timer = 0.0;
        },
        incrementTimer: (state) => {
            state.timer += 0.1;
        },
        resetRunState: (state) => {
            state.task = null;
            state.taskArray = [];
            state.resultIdList = [];
            state.generalStatus = RunState.IDLE;
        }
    }
})

// Action creators are generated for each case reducer function
export const {
    setCurrentTask, setTaskArray, setResultIdList, setGeneralStatus, resetRunState, resetTimer, incrementTimer
} = runStateSlice.actions;

export default runStateSlice.reducer;
