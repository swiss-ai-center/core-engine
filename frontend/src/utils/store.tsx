import { configureStore } from '@reduxjs/toolkit';
import runStateReducer from './reducers/runStateSlice';
import colorModeReducer from './reducers/colorModeSlice';
import perPageReducer from './reducers/perPageSlice';

export default configureStore({
    reducer: {
        runState: runStateReducer,
        colorMode: colorModeReducer,
        perPage: perPageReducer,
    },
})
