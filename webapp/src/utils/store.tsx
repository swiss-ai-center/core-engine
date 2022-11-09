import { configureStore } from '@reduxjs/toolkit';
import runStateReducer from './reducers/runStateSlice';

export default configureStore({
    reducer: {
        runState: runStateReducer,
    },
})
