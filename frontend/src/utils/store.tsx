import { configureStore } from '@reduxjs/toolkit';
import colorModeReducer from './reducers/colorModeSlice';
import menuIconReducer from './reducers/menuIconSlice';
import perPageReducer from './reducers/perPageSlice';
import runStateReducer from './reducers/runStateSlice';

export default configureStore({
    reducer: {
        menuIcon: menuIconReducer,
        runState: runStateReducer,
        colorMode: colorModeReducer,
        perPage: perPageReducer,
    },
})
