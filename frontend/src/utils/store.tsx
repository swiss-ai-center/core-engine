import { configureStore } from '@reduxjs/toolkit';
import colorModeReducer from 'utils/reducers/colorModeSlice';
import menuIconReducer from 'utils/reducers/menuIconSlice';
import perPageReducer from 'utils/reducers/perPageSlice';
import runStateReducer from 'utils/reducers/runStateSlice';

export default configureStore({
    reducer: {
        menuIcon: menuIconReducer,
        runState: runStateReducer,
        colorMode: colorModeReducer,
        perPage: perPageReducer,
    },
})
