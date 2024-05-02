import { configureStore } from '@reduxjs/toolkit';
import runStateReducer from './reducers/runStateSlice';
import colorModeReducer from './reducers/colorModeSlice';
import perPageReducer from './reducers/perPageSlice';
import menuIconReducer from './reducers/menuIconSlice';

export default configureStore({
    reducer: {
        menuIcon: menuIconReducer,
        runState: runStateReducer,
        colorMode: colorModeReducer,
        perPage: perPageReducer,
    },
})
